# lot's of docstrings are missing, don't complain for now...
# pylint: disable-msg=C0111

from pyflow.lib.antlr3.treewizard import TreeWizard

try:
    from pyflow.lib.antlr3.dottreegen import toDOT
except ImportError as exc:
    def toDOT(*args, **kwargs):
        raise exc
