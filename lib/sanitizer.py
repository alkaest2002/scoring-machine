
from typing import TYPE_CHECKING

import pandas as pd

from lib import UNAVAILABLE_NORMS
from lib.errors import ValidationError

if TYPE_CHECKING:
    from lib.data_container import DataContainer

class Sanitizer:
    """
    A class to sanitize and validate test data based on predefined test specifications.
    This includes cleaning and normalizing norms and item answer data.
    """

    def __init__(self, data_container: DataContainer) -> None:
        """
        Initialize a `Sanitizer` instance with the given test data and specifications.

        Parameters:
            data_container (DataContainer): An instance of DataContainer containing
               raw test data and associated specifications.
        """
        self.data_container: DataContainer = data_container

    def sanitize_norms(self) -> pd.Series:
        """
        Validate and clean the "norms_id" column by ensuring all values conform
        to the set of valid norms defined in the test specifications.

        Invalid norms are replaced with the `UNAVAILABLE_NORMS` constant.

        Returns:
            pd.Series: A Series containing sanitized "norms_id" values.
        """
        # Retrieve the set of available norms from the test specifications
        available_norms: set[str] = set(self.data_container.test_specs.get_spec("norms.available_norms"))

        # Check if each entry in "norms_id" is within the set of valid norms
        condition: pd.Series = self.data_container.data_norms.map(
            lambda x: set(str(x).split(" ")).issubset(available_norms)
        )

        # Replace invalid entries with the `UNAVAILABLE_NORMS` constant
        # And sort multiple norms alphabetically for consistency
        # And for avoiding grouping issues later on
        final_norms: pd.Series = (
            self.data_container.data_norms
                .where(condition, UNAVAILABLE_NORMS)
                .apply(lambda x: " ".join(sorted(x.split(" "))))
        )

        return final_norms

    def sanitize_test_answers(self) -> pd.DataFrame | pd.Series:
        """
        Sanitize the item answer columns by coercing values to numeric types
        and restricting (clipping) them within the range specified in the test specifications.

        Returns:
            Union[pd.DataFrame, pd.Series]: A DataFrame or Series with cleaned item answers.
        """
        # Convert values to numeric and clip them to the specified Likert scale range
        # Errors during conversion are coerced to NaN
        return (
            self.data_container.data_answers
                .apply(lambda x: pd.to_numeric(x, errors="coerce", downcast="integer"))
                .clip(
                    self.data_container.test_specs.get_spec("likert.min"),
                    self.data_container.test_specs.get_spec("likert.max")
                )
        )

    def sanitize_data(self) -> DataContainer:
        """
        Validate and sanitize the test norms and answers, ensuring compatibility
        with the test specifications. The function performs checks on column consistency
        and combines sanitized norms and answers into a single DataFrame.

        Returns:
            DataContainer: The `DataContainer` instance updated with sanitized data.

        Raises:
            ValidationError:
                - If the structure of the test data does not match the column requirements
                  defined in the test specifications.
                - If the `subject_id` column contains duplicate values.
        """
        # Retrieve the required test length from the test specifications
        # This defines how many questions/columns the test should have.
        test_length: int = self.data_container.test_specs.get_spec("length")

        # Define the expected column layout based on the test specifications
        # Columns required are: ["subject_id", "norms_id", "i1", "i2", ..., "in"]
        requested_columns: list[str] = ["subject_id", "norms_id"] + [f"i{i}" for i in range(1, test_length + 1)]

        # Check for inconsistencies between the expected columns and the actual data columns
        # Using symmetric_difference to identify any mismatch in column names
        sym_dif: pd.Index = pd.Index(requested_columns).symmetric_difference(self.data_container.data.columns)

        # Raise a ValidationError if requested columns do not match the DataFrame columns
        if sym_dif.shape[0] > 0:
            raise ValidationError("Test data is not compatible with test specifications. "
                f"Missing or unexpected columns: {list(sym_dif)}")

        # Sanitize and combine "subject_id" column, sanitized norms, and sanitized answers
        sanitized_data: pd.DataFrame = pd.concat([
            self.data_container.data["subject_id"],
            self.sanitize_norms(),
            self.sanitize_test_answers()
        ], axis=1)

        # Update the data_container with the validated and sanitized data
        self.data_container.data = sanitized_data

        return self.data_container
