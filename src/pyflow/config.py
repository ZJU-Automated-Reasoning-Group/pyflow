# Use a JIT?
usePsyco = True

debugOnFailiure = False

# Create output directory relative to this config file.
import os.path

base, junk = os.path.split(__file__)
outputDirectory = os.path.normpath(os.path.join(base, "..", "summaries"))

doDump = False
maskDumpErrors = False
doThreadCleanup = False

dumpStats = False


# Pointer analysis testing
useXTypes = True
useControlSensitivity = True
useCPA = True
