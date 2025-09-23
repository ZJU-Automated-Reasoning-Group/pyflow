# Security checker constants
RANKING = ["UNDEFINED", "LOW", "MEDIUM", "HIGH"]
RANKING_VALUES = {"UNDEFINED": 1, "LOW": 3, "MEDIUM": 5, "HIGH": 10}
CRITERIA = [("SEVERITY", "UNDEFINED"), ("CONFIDENCE", "UNDEFINED")]

# Add each ranking to globals for direct access
for rank in RANKING:
    globals()[rank] = rank

CONFIDENCE_DEFAULT = "UNDEFINED"

# Values Python considers to be False
FALSE_VALUES = [None, False, "False", 0, 0.0, 0j, "", (), [], {}]

# Directories to exclude by default
EXCLUDE = (
    ".svn",
    "CVS", 
    ".bzr",
    ".hg",
    ".git",
    "__pycache__",
    ".tox",
    ".eggs",
    "*.egg",
)
