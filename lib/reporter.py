from pathlib import Path
from jinja2 import FileSystemLoader, Environment
import test
from weasyprint import HTML
from lib import TESTS_PATH, XEROX_PATH
from lib.data_container import DataContainer

# Initialize the Jinja2 environment for rendering HTML templates
jinja_env: Environment = Environment(loader=FileSystemLoader([TESTS_PATH]))


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
        self.test_specs: dict = data_container.test_specs_and_results["test_specs"]

        # Store all test results sourced from the DataContainer
        self.test_results: dict = data_container.test_specs_and_results["test_results"]

        # Store test name sourced from test specifications
        self.test_name: str = self.test_specs["name"]
        
        # Store the report template name sourced from test specifications
        self.report_name: str = self.test_specs["report"]
        
        # Store the specified HTML template for the report via Jinja2
        self.report_template = jinja_env.get_template(str(Path(self.test_name) / f"{self.report_name}.html"))

    def render_report(self, assessment_date: str, split_reports: bool) -> None:
        """
        Generates PDF reports by rendering HTML templates with provided data and saves the output.

        This method can generate:
        1. Individual PDF reports for each set of test results if `split_data` is True.
        2. A single consolidated PDF report with all test results if `split_data` is False.

        Process:
        1. Iterates through test results to render HTML content for the reports.
        2. Converts the rendered HTML content to PDF format.
        3. Saves the generated file(s) to the `XEROX_PATH` directory.

        Args:
            assessment_date (str): The date of the assessment to be included in the report.
            split_data (bool): Whether to generate separate PDF reports (True) or a single, 
                            consolidated report (False).

        Output:
            The generated PDF report(s) are saved in the `XEROX_PATH` directory:
            - If `split_data` is True: Files follow the pattern: 
            `<test_name>_<subject_id>_<index>_report.pdf`.
            - If `split_data` is False: File follows the pattern: 
            `<test_name>_report.pdf`.
        """
        reports: str = ""  # To accumulate HTML content for combined report if `split_data` is False

        # Loop through all test results to render files
        for index, test_results in enumerate(self.test_results, 1):
            
            # Render the HTML template with test specifications, results, and assessment date
            rendered_template: str = self.report_template.render(
                test_specs=self.test_specs,  # Specifications of the test
                test_results=test_results,  # Current set of test results
                assessment_date=assessment_date  # The provided assessment date
            )

            if split_reports:
                # Generate individual PDF report for each test result
                output_filepath: Path = XEROX_PATH / f"{self.test_name}_{test_results['subject_id']}_{str(index).zfill(3)}_report.pdf"
                
                # Persist the rendered HTML as a PDF file
                HTML(string=rendered_template).write_pdf(output_filepath)
            else:
                # Append the rendered HTML content for consolidation
                reports += rendered_template

        if not split_reports:
            # Save the combined report as a single PDF
            output_filepath: Path = XEROX_PATH / f"{self.test_name}_report.pdf"

            # Persist the combined HTML content as a single PDF file
            HTML(string=reports).write_pdf(output_filepath)

            
