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
        args (argparse.Namespace): arguments parsed from the command line.
            args.test (str): Identifier for the test.
            args.do_not_compute_standard_scores (bool): whether to compute standard scores.
            args.output_type (str): Type of output to generate ("csv", "json", or "pdf").
            args.split_reports (bool): Whether to split PDF reports or keep them in a single file.
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

        # Step 5: Compute standard scores based on norms if not excluded
        if not args.do_not_compute_standard_scores:
            data_container: DataContainer = Standardizer(data_container).compute_standard_scores()

        # Step 6: Branch based on the requested output type
        if args.output_type != "pdf":
            # Persist data
            data_container.persist(type=args.output_type)
        else:
            # Generate PDF report(s)
            Reporter(data_container).generate_report(
                assessment_date=args.assessment_date, 
                split_reports=args.split_reports
            )

    except Exception as e:
        # Log the error message for debugging purposes.
        print(f"Error occurred: {e}")

        # Send notification with traceback details using TracebackNotifier
        TracebackNotifier(e).notify_traceback()
