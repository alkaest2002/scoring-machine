import os
from pathlib import Path

# Define constants
BASE_PATH = Path(os.getcwd())
LIB_PATH = BASE_PATH / "lib"
TESTS_PATH =  LIB_PATH / "tests"
DATA_PATH = BASE_PATH / "data"
XEROX_PATH = BASE_PATH / "xerox"
UNAVAILABLE_NORMS = "n.a."
