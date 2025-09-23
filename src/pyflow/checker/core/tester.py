# Security test runner
import copy
import logging
from . import constants
from . import context as b_context
from . import utils

LOG = logging.getLogger(__name__)


class SecurityTester:
    def __init__(self, testset, debug, nosec_lines, metrics):
        self.results = []
        self.testset = testset
        self.last_result = None
        self.debug = debug
        self.nosec_lines = nosec_lines
        self.metrics = metrics

    def run_tests(self, raw_context, checktype):
        """Run all tests for a certain type of check"""
        scores = {
            "SEVERITY": [0] * len(constants.RANKING),
            "CONFIDENCE": [0] * len(constants.RANKING),
        }

        tests = self.testset.get_tests(checktype)
        for test in tests:
            name = test.__name__
            # Execute test with an instance of the context class
            temp_context = copy.copy(raw_context)
            context = b_context.Context(temp_context)
            try:
                if hasattr(test, "_config"):
                    result = test(context, test._config)
                else:
                    result = test(context)

                if result is not None:
                    # Handle both single issues and lists of issues
                    issues = result if isinstance(result, list) else [result]
                    
                    for issue in issues:
                        nosec_tests_to_skip = self._get_nosecs_from_contexts(
                            temp_context, test_result=issue
                        )

                        if isinstance(temp_context["filename"], bytes):
                            issue.fname = temp_context["filename"].decode("utf-8")
                        else:
                            issue.fname = temp_context["filename"]
                        issue.fdata = temp_context["file_data"]

                        if issue.lineno is None:
                            issue.lineno = temp_context["lineno"]
                        if issue.linerange == []:
                            issue.linerange = temp_context["linerange"]
                        if issue.col_offset == -1:
                            issue.col_offset = temp_context["col_offset"]
                        issue.end_col_offset = temp_context.get("end_col_offset", 0)
                        issue.test = name
                        if issue.test_id == "":
                            issue.test_id = test._test_id

                        # Don't skip the test if there was no nosec comment
                        if nosec_tests_to_skip is not None:
                            # If the set is empty then it means that nosec was
                            # used without test number -> update nosecs counter.
                            # If the test id is in the set of tests to skip,
                            # log and increment the skip by test count.
                            if not nosec_tests_to_skip:
                                LOG.debug("skipped, nosec without test number")
                                self.metrics.note_nosec()
                                continue
                            if issue.test_id in nosec_tests_to_skip:
                                LOG.debug(f"skipped, nosec for test {issue.test_id}")
                                self.metrics.note_skipped_test()
                                continue

                        self.results.append(issue)

                        LOG.debug("Issue identified by %s: %s", name, issue)
                        sev = constants.RANKING.index(issue.severity)
                        val = constants.RANKING_VALUES[issue.severity]
                        scores["SEVERITY"][sev] += val
                        con = constants.RANKING.index(issue.confidence)
                        val = constants.RANKING_VALUES[issue.confidence]
                        scores["CONFIDENCE"][con] += val
                else:
                    nosec_tests_to_skip = self._get_nosecs_from_contexts(temp_context)
                    if (
                        nosec_tests_to_skip
                        and test._test_id in nosec_tests_to_skip
                    ):
                        LOG.warning(
                            f"nosec encountered ({test._test_id}), but no "
                            f"failed test on line {temp_context['lineno']}"
                        )

            except Exception as e:
                self.report_error(name, context, e)
                if self.debug:
                    raise
        LOG.debug("Returning scores: %s", scores)
        return scores

    def _get_nosecs_from_contexts(self, context, test_result=None):
        """Use context and optional test result to get set of tests to skip"""
        nosec_tests_to_skip = set()
        base_tests = (
            self.nosec_lines.get(test_result.lineno, None)
            if test_result
            else None
        )
        context_tests = utils.get_nosec(self.nosec_lines, context)

        # If both are none there were no comments
        if base_tests is None and context_tests is None:
            nosec_tests_to_skip = None

        # Combine tests from current line and context line
        if base_tests is not None:
            nosec_tests_to_skip.update(base_tests)
        if context_tests is not None:
            nosec_tests_to_skip.update(context_tests)

        return nosec_tests_to_skip

    @staticmethod
    def report_error(test, context, error):
        """Report an error that occurred during testing"""
        what = "Security checker internal error running: "
        what += f"{test} "
        what += "on file %s at line %i: " % (
            context._context["filename"],
            context._context["lineno"],
        )
        what += str(error)
        import traceback
        what += traceback.format_exc()
        LOG.error(what)
