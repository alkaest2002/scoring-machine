from functools import cached_property
from typing import TYPE_CHECKING, Any, Literal

import numpy as np
import pandas as pd

from lib import UNAVAILABLE_NORMS
from lib.test_specs import TestSpecs
from lib.utils import expand_dict_like_columns

if TYPE_CHECKING:
    from lib.data_provider import DataProvider

class DataContainer:
    """
    Manages the loading, organization, processing, and export of test-related data.
    This includes test data, specifications, norms, computed scores (raw and standardized),
    and combined results. The class supports data export in CSV and JSON formats.
    """

    def __init__(self, data_provider: DataProvider) -> None:
        """
        Initializes the `DataContainer` with a provided data provider and loads
        the relevant test data, specifications, and norms.

        Args:
            data_provider (DataProvider): Utility for managing file paths and performing filesystem operations.

        Attributes:
            data_provider (DataProvider): Instance of the `DataProvider` class for handling file paths.
            data (pd.DataFrame): DataFrame containing the raw test data.
            test_name (str): Identifier for the test being processed.
            test_specs (TestSpecs): Object containing configurations and specifications of the test.
            test_norms (pd.DataFrame): DataFrame containing the norms associated with the test.
            test_scores (pd.DataFrame): Placeholder for computed raw test scores.
            test_standard_scores (pd.DataFrame): Placeholder for computed standardized test scores.
        """
        self.data_provider: DataProvider = data_provider
        self.data: pd.DataFrame = data_provider.load_test_data()
        self.test_name: str = data_provider.test_name
        self.test_specs: TestSpecs = TestSpecs(data_provider.load_test_specifications())
        self.test_norms: pd.DataFrame = data_provider.load_test_norms()
        self.test_scores: pd.DataFrame = pd.DataFrame()
        self.test_standard_scores: pd.DataFrame = pd.DataFrame()

    @property # cannot be cached since sanitizer modifies the data
    def data_norms(self) -> pd.Series:
        """
        Retrieves the 'norms_id' column from the test data. If the 'norms_id' column
        is missing, assigns a default value (`UNAVAILABLE_NORMS`) to all rows.

        Returns:
            pd.Series: A pandas Series containing values from the 'norms_id' column,
            or a default value if the column is unavailable.
        """
        if "norms_id" not in self.data.columns:
            return pd.Series({"norms_id": UNAVAILABLE_NORMS}, index=self.data.index)
        return self.data.loc[:, "norms_id"]

    @property # cannot be cached since sanitizer modifies the data
    def data_answers(self) -> pd.DataFrame:
        """
        Extracts and returns test answers.

        Returns:
            pd.DataFrame: A DataFrame containing only the test response data.
        """
        return self.data.filter(regex=r"^i\d+$", axis=1)

    @cached_property # can be cached since it is not modified
    def data_subject_ids(self) -> pd.Series:
        """
        Retrieves the 'subject_id' column from the test data.

        Returns:
            pd.Series: A pandas Series containing values from the 'subject_id' column
        """
        return self.data.loc[:, "subject_id"]

    @cached_property # can be cached since it is not modified
    def results(self) -> pd.DataFrame:
        """
        Combines subject ids, answers data (`data_subject_ids`, `data_answers`), raw test scores (`test_scores`)
        and standardized scores (`test_standard_scores`) into a single DataFrame.

        Returns:
            pd.DataFrame: A DataFrame containing subject ids, answers, raw-related scores and standardized scores.
        """
        return pd.concat([
            self.data_subject_ids,
            self.data_answers,
            self.test_scores,
            self.test_standard_scores], axis=1)

    @cached_property # can be cached since it is not modified
    def test_specs_and_results(self) -> dict[str, Any]:
        """
        Aggregates test specifications, raw test data, and test results
        into a structured dictionary.

        Returns:
            dict: A dictionary containing the following keys:
                - "test_specs": Test specifications.
                - "test_data": Test response data.
                - "test_results": Combined raw and standardized test scores.
        """
        return {
            "test_specs": self.test_specs.get_spec(None),
            "test_results": self.results.replace({np.nan: None}).to_dict(orient="records")
        }

    def persist(self, type: Literal["csv", "json"]) -> None:
        """
        Exports test results in the specified format, either CSV or JSON.

        Args:
            type (str): Desired output format ('csv' or 'json').
        """
        if type == "csv":

            # Create a copy of test results
            data_to_persist_csv: pd.DataFrame = self.results.copy()

            # Expand dictionary-like columns if requested
            data_to_persist_csv_expanded: pd.DataFrame =\
                expand_dict_like_columns(data_to_persist_csv, regex_for_dict_like="std__")

            self.data_provider.persist(data_to_persist_csv_expanded)

        else:
            # Create a copy of test data
            data_to_persist_json: dict[str, Any] = self.test_specs_and_results.copy()

        # Persist the data to disk
        self.data_provider.persist(data_to_persist_json)
