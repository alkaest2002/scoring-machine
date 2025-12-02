from itertools import batched
from os.path import commonprefix
from pathlib import Path
from typing import TYPE_CHECKING, Any

from jinja2 import Environment, FileSystemLoader
from weasyprint import HTML

from lib import TESTS_PATH, XEROX_PATH

if TYPE_CHECKING:
    from lib.data_container import DataContainer

# Initialize the Jinja2 environment for rendering HTML templates
jinja_env: Environment = Environment(loader=FileSystemLoader([TESTS_PATH]))

def convert_std_dict(value: dict[str, Any], n: int) -> list[dict[str, Any]]:
    # Converts a dictionary of standardized scores into a list of dictionaries,
    # Each dictionary contains std, std_interpretation, std_min, std_max keys
    items: list[tuple[str, Any]] = list(value.items())
    final: list[dict[str, Any]] = [dict(items[i::n]) for i in range(n)]
    # Normalize keys by removing common prefixes
    for entry in final:
        # Get all keys of the entry
        entry_keys: list[str] = list(entry.keys())
        # Find common prefix
        common_prefix: str = commonprefix(entry_keys)
        # Iterate through keys
        for key in entry_keys:
            # Create new key by removing common prefix and underscore
            new_key: str = key[len(common_prefix)+1:] if common_prefix else key
            # Ensure new_key is not empty
            new_key = new_key if len(new_key) > 0 else "value"
            # Update the entry with the new key
            entry[new_key] = entry.pop(key)
            # Add norms_id without the trailing underscore
            entry["norms_id"] = common_prefix[:-4]

    return final

jinja_env.filters['convert_std_dict'] = convert_std_dict


class Reporter:
    """
    A class responsible for generating PDF reports using data provided and pre-defined HTML templates.
    Utilizes Jinja2 for HTML template rendering and WeasyPrint for PDF creation.
    """

    def __init__(self, data_container: DataContainer) -> None:
        """
        Initializes the Reporter instance with a DataContainer.

        Args:
            data_container (DataContainer): An instance of DataContainer that offers the report data
                and template specifications.
        """
        # Store all test specification data sourced from the DataContainer
        self.test_specs: dict[str, Any] = data_container.test_specs_and_results["test_specs"]

        # Store all test results sourced from the DataContainer
        self.test_results: dict[str, Any] = data_container.test_specs_and_results["test_results"]

        # Store test name sourced from test specifications
        self.test_name: str = self.test_specs["name"]

        # Store the report template name sourced from test specifications
        self.report_name: str = self.test_specs["report"]

        # Store the specified HTML template for the report via Jinja2
        self.report_template = jinja_env.get_template(str(Path(self.test_name) / f"{self.report_name}.html"))


    def generate_report(self, assessment_date: str, split_reports: bool) -> None:
        """
        Generates PDF reports by rendering HTML templates with the provided data and saves them as files.

        This method supports:
        1. Generating individual PDF reports for each test result if `split_reports` is True.
        2. Generating batched consolidated PDF reports if `split_reports` is False, to improve
        performance and handle data in manageable chunks.

        Process:
        1. Splits the test results into batches to optimize PDF generation.
        - Each batch contains a predefined number of test results (`reports_per_batch`).
        2. Iterates through each batch and processes the test results within it.
        - For `split_reports=True`, generates a separate PDF file for each test result.
        - For `split_reports=False`, accumulates all rendered HTML into a combined report for the batch.
        3. Converts the rendered HTML content to PDF format.
        4. Saves the generated PDF files to the `XEROX_PATH` directory.

        Args:
            assessment_date (str): The date of the assessment to include in the report.
            split_reports (bool):
                - True: Generates a separate PDF report for each test result, with a detailed naming pattern
                        that includes batch and report-specific details.
                - False: Groups test results into batches for combined PDF reports, with each file
                        containing reports of a single batch.

        File Output:
            The generated PDF report(s) are saved in the `XEROX_PATH` directory:
            - If `split_reports` is True:
            Files follow the pattern:
            `<test_name>-<report_index>-<subject_id>.pdf`.
            Example: `test_name-001001-12345.pdf`, where:
                - `report_index`: The global report index across all batches.
                - `subject_id`: A unique identifier for the test subject.
            - If `split_reports` is False:
            Files follow the pattern:
            `<test_name>-<batch_index>.pdf`.
            Example: `test_name-001.pdf`, where:
                - `batch_index`: The batch number (padded to 3 digits).

        Notes:
            - The `reports_per_batch` variable defines how many test results are processed in a single batch.
            Batch processing improves the performance of the PDF generation process, especially when working
            with large datasets or computationally intensive tasks.
        """
        # To accumulate HTML content for combined report if `split_data` is False
        reports: str = ""

        # Define how many reports to process per batch
        reports_per_batch: int = 100

        # Create batches of data (PDF generation is heavy)
        batches: batched[str] = batched(self.test_results, n=reports_per_batch, strict=False)

        # Initialize rendered reports list
        rendered_reports: list[tuple[Path, str]] = []

        # Loop through all batches
        for batch_index, batch_test_results in enumerate(batches, 1):

            # Loop through test results in current batch
            for batch_report_index, test_results in enumerate(batch_test_results, 1):

                # Define global index
                report_index: str = f"batch-{str(batch_index).zfill(3)}-report-{str(batch_report_index).zfill(3)}"

                # Render the HTML template with test specifications, test results, and assessment date
                rendered_template: str = self.report_template.render(
                    test_specs=self.test_specs,  # Specifications of the test
                    test_results=test_results,  # Current set of test results
                    assessment_date=assessment_date  # The provided assessment date
                )

                # Generate individual PDF report for each test result
                subject_id: str = test_results["subject_id"] # type: ignore[index]
                filename: str = f"{self.test_name}-{report_index}-{subject_id}"
                output_filepath: Path = XEROX_PATH / filename

                # Persist the rendered HTML as a PDF file
                rendered_reports.append((output_filepath.with_suffix(".pdf"), rendered_template))

            # Handle PDF generation based on `split_reports` flag
            if split_reports:
                # Generate individual PDF reports for each rendered template in the batch
                for output_filepath, rendered_template in rendered_reports:
                    HTML(string=rendered_template).write_pdf(target=output_filepath)

            # Generate combined PDF report for the entire batch
            else:
                # Accumulate rendered HTML for combined report
                for _, rendered_template in rendered_reports:
                    reports += rendered_template

                # Define output filepath for the combined batch report
                filename = f"{self.test_name}-batch-{str(batch_index).zfill(3)}"
                output_filepath = XEROX_PATH / filename

                # Persist the combined rendered HTML as a PDF file
                HTML(string=reports).write_pdf(target=output_filepath.with_suffix(".pdf"))

                # For debugging
                # with output_filepath.with_suffix(".html").open("w") as html_file:
                #     html_file.write(reports)  # noqa: ERA001

