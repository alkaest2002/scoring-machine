from pathlib import Path
from jinja2 import FileSystemLoader, Environment
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
        # Store all report-related data sourced from the DataContainer
        self.report_data: dict = data_container.test_specs_and_results

        # Store test name from test specifications
        self.test_name: str = data_container.test_specs_and_results["test_specs"]["name"]
        
        # Store the report template name specified in the test specifications
        self.report_name: str = data_container.test_specs_and_results["test_specs"]["report"]
        
        # Store the specified HTML template for the report via Jinja2
        self.report_template = jinja_env.get_template(str(Path(self.test_name) / f"{self.report_name}.html"))

    def render_report(self, assessment_date: str) -> None:
        """
        Generates a PDF report by rendering an HTML template with the report data and saves the output.

        Process:
        1. Renders the HTML template with the provided data and assessment date.
        2. Converts the rendered HTML to a PDF.
        3. Saves the generated PDF file to the designated directory with an appropriate filename.

        Args:
            assessment_date (str): The date of the assessment to be included in the report.

        File Output:
            The generated PDF report is saved in the `XEROX_PATH` directory, with a filename pattern:
            `<timestamp>_<report_name>.pdf`.
        """
        # Render the HTML template with the provided report data and assessment date
        rendered_template: str = self.report_template.render(data=self.report_data, assessment_date=assessment_date)
        
        # Define the output file path
        output_filepath: Path = XEROX_PATH / f"{self.test_name}_report.pdf"
        
        # Convert the rendered HTML content to a PDF and save it to the determined output path
        HTML(string=rendered_template).write_pdf(output_filepath)
