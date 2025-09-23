# Security issue representation
import linecache


class Cwe:
    NOTSET = 0
    IMPROPER_INPUT_VALIDATION = 20
    PATH_TRAVERSAL = 22
    OS_COMMAND_INJECTION = 78
    XSS = 79
    BASIC_XSS = 80
    SQL_INJECTION = 89
    CODE_INJECTION = 94
    IMPROPER_WILDCARD_NEUTRALIZATION = 155
    HARD_CODED_PASSWORD = 259
    IMPROPER_ACCESS_CONTROL = 284
    IMPROPER_CERT_VALIDATION = 295
    CLEARTEXT_TRANSMISSION = 319
    INADEQUATE_ENCRYPTION_STRENGTH = 326
    BROKEN_CRYPTO = 327
    INSUFFICIENT_RANDOM_VALUES = 330
    INSECURE_TEMP_FILE = 377
    UNCONTROLLED_RESOURCE_CONSUMPTION = 400
    DOWNLOAD_OF_CODE_WITHOUT_INTEGRITY_CHECK = 494
    DESERIALIZATION_OF_UNTRUSTED_DATA = 502
    MULTIPLE_BINDS = 605
    IMPROPER_CHECK_OF_EXCEPT_COND = 703
    INCORRECT_PERMISSION_ASSIGNMENT = 732
    INAPPROPRIATE_ENCODING_FOR_OUTPUT_CONTEXT = 838

    MITRE_URL_PATTERN = "https://cwe.mitre.org/data/definitions/%s.html"

    def __init__(self, id=NOTSET):
        self.id = id

    def link(self):
        return "" if self.id == Cwe.NOTSET else Cwe.MITRE_URL_PATTERN % str(self.id)

    def __str__(self):
        return "" if self.id == Cwe.NOTSET else "CWE-%i (%s)" % (self.id, self.link())

    def as_dict(self):
        return {"id": self.id, "link": self.link()} if self.id != Cwe.NOTSET else {}

    def __eq__(self, other):
        return self.id == other.id

    def __ne__(self, other):
        return self.id != other.id

    def __hash__(self):
        return id(self)


class Issue:
    def __init__(self, severity, cwe=0, confidence="UNDEFINED", text="", ident=None, 
                 lineno=None, test_id="", col_offset=-1, end_col_offset=0):
        self.severity = severity
        self.cwe = Cwe(cwe)
        self.confidence = confidence
        self.text = text.decode("utf-8") if isinstance(text, bytes) else text
        self.ident = ident
        self.fname = ""
        self.fdata = None
        self.test = ""
        self.test_id = test_id
        self.lineno = lineno
        self.col_offset = col_offset
        self.end_col_offset = end_col_offset
        self.linerange = []

    def __str__(self):
        return ("Issue: '%s' from %s:%s: CWE: %s, Severity: %s Confidence: %s at %s:%i:%i") % (
            self.text, self.test_id, (self.ident or self.test), str(self.cwe),
            self.severity, self.confidence, self.fname, self.lineno, self.col_offset)

    def __eq__(self, other):
        match_fields = ["text", "severity", "cwe", "confidence", "fname", "test", "test_id"]
        return all(getattr(self, field) == getattr(other, field) for field in match_fields)

    def __ne__(self, other):
        return not self.__eq__(other)

    def __hash__(self):
        return id(self)

    def filter(self, severity, confidence):
        """Filter on confidence and severity thresholds"""
        from .constants import RANKING
        return (RANKING.index(self.severity) >= RANKING.index(severity) and 
                RANKING.index(self.confidence) >= RANKING.index(confidence))

    def get_code(self, max_lines=3, tabbed=False):
        """Get lines of code from the file that generated this issue"""
        max_lines = max(max_lines, 1)
        lmin = max(1, self.lineno - max_lines // 2)
        lmax = lmin + len(self.linerange) + max_lines - 1

        if self.fname == "<stdin>":
            self.fdata.seek(0)
            for _ in range(1, lmin):
                self.fdata.readline()

        tmplt = "%i\t%s" if tabbed else "%i %s"
        lines = []
        for line in range(lmin, lmax):
            text = self.fdata.readline() if self.fname == "<stdin>" else linecache.getline(self.fname, line)
            if not text:
                break
            if isinstance(text, bytes):
                text = text.decode("utf-8")
            lines.append(tmplt % (line, text))
        return "".join(lines)

    def as_dict(self, with_code=True, max_lines=3):
        """Convert the issue to a dict for output"""
        out = {
            "filename": self.fname, "test_name": self.test, "test_id": self.test_id,
            "issue_severity": self.severity, "issue_cwe": self.cwe.as_dict(),
            "issue_confidence": self.confidence, "issue_text": self.text,
            "line_number": self.lineno, "line_range": self.linerange,
            "col_offset": self.col_offset, "end_col_offset": self.end_col_offset,
        }
        if with_code:
            out["code"] = self.get_code(max_lines=max_lines)
        return out
