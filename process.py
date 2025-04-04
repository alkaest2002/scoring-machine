import argparse
from datetime import date
from lib import TESTS_PATH
from lib.processor import process

# Get the list of available tests by scanning the tests folder
available_tests = [f.name for f in TESTS_PATH.glob("[!.]*") if f.is_dir()]

# Initialize the argument parser
parser = argparse.ArgumentParser(
    prog="Scoring Machine",
    description="This script computes test scores based on test specifications, norms, "
                "and provided response data."
)

# Add command-line arguments
parser.add_argument(
    "-t", "--test",
    required=True,
    choices=available_tests,
    help="Specify the test to use. Must be one of the available tests present in the test folder."
)

parser.add_argument(
    "-n", "--compute_norms",
    choices=["0", "1"],
    default="1",
    help="Specify whether to compute standard scores. Default is '1' (compute norms)."
)

parser.add_argument(
    "-e", "--expand_norms",
    choices=["0", "1"],
    default="0",
    help="Specify whether to expand dictionary-like columns in the results (0 = No, 1 = Yes). Default is 0 (do not expand)."
)

parser.add_argument(
    "-o", "--output_type",
    choices=["csv", "json", "pdf"],
    default="pdf",
    help="Specify whether to export the results as csv, json, or pdf. Default is pdf."
)

parser.add_argument(
    "-d", "--assessment_date",
    default=date.today().strftime('%d/%m/%Y'),
    help="Specify the assesment date. Default is the current date."
)

# Parse command-line arguments and process
process(parser.parse_args())