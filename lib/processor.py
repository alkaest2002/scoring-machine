import argparse
from lib.data_container import DataContainer
from lib.errors import TracebackNotifier
from lib.data_provider import DataProvider
from lib.sanitizer import Sanitizer
from lib.scorer import Scorer
from lib.standardizer import Standardizer
from lib.reporter import Reporter

def process(args: argparse.Namespace) -> None:
    """
    Main function to process test data, compute scores, and generate output.

    This function orchestrates the processing of test data by interacting with various 
    modules such as DataProvider, DataContainer, Sanitizer, Scorer, Standardizer, and Reporter. 
    It handles input sanitization, score computation, and renders output in the requested 
    format (CSV, JSON, or PDF).

    Args:
        args (argparse.Namespace): The namespace containing arguments parsed from the 
                                   command line.
            args.test (str): Identifier for the test.
            args.compute_norms (str): Flag ("1" or "0") indicating whether to compute 
                                      standard scores using norms.
            args.output_type (str): Type of output to generate ("csv", "json", or "pdf").
            args.expand_norms (bool): Whether to expand norms data in the output file.
            args.assessment_date (str): Assessment date for inclusion in reports.

    Raises:
        Exception: Handles any unexpected error that may occur during processing and sends 
                   traceback notifications using `TracebackNotifier`.
    """
    try:
        # Step 1: Initialize DataProvider
        data_provider: DataProvider = DataProvider(args.test)

        # Step 2: Initialize DataContainer
        data_container: DataContainer = DataContainer(data_provider)

        # Step 3: Sanitize and validate data using Sanitizer
        data_container: DataContainer = Sanitizer(data_container).sanitize_data()

        # Step 4: Compute raw scores, corrected raw scores, and mean scores using Scorer
        data_container: DataContainer = Scorer(data_container).compute_raw_related_scores()

        # Step 5: Compute standard scores if requested
        if args.compute_norms == "1":
            # Initialize Standardizer to compute scores based on norms
            data_container: DataContainer = Standardizer(data_container).compute_standard_scores()

        # Step 6: Branch based on the requested output type
        if args.output_type != "pdf":
            # Persist cleaned and processed data
            data_container.persist(type=args.output_type, expand_norms=args.expand_norms)
        else:
            # Generate and render a PDF report
            Reporter(data_container).render_report(assessment_date=args.assessment_date)

    except Exception as e:
        # Log the error message for debugging purposes.
        print(f"Error occurred: {e}")

        # Send notification with traceback details using TracebackNotifier
        TracebackNotifier(e).notify_traceback()
