import re
from typing import TYPE_CHECKING, Any

import pandas as pd

if TYPE_CHECKING:
    from collections.abc import Hashable

    from lib.data_container import DataContainer

class Standardizer:
    """
    A class to map raw test scores into standardized scores using provided norms.
    Supports multi-scale scoring and includes optional interpretations if available.
    """

    def __init__(self, data_container: DataContainer) -> None:
        """
        Initializes the Standardizer instance with the provided data provider.

        Args:
            data_container (DataContainer): An instance of DataContainer containing test data,
                norms, and specifications required for standardization.
        """
        self.data_container: DataContainer = data_container

    def get_standard_scores_from_table(
        self,
        series: pd.Series,
        norms: pd.DataFrame
    ) -> list[dict[Hashable, Any]]:
        """
        Maps raw scale scores into standardized scores using lookup from norms.

        Args:
            series (pd.Series): A Pandas Series containing raw scores for a single scale.
            norms (pd.DataFrame): Norms dataset used to map raw scores to standardized scores.

        Returns:
            list[dict]: A list of dictionaries where each dictionary contains:
                - The standardized scores for each raw score.
                - Optional interpretations if available in the norms dataset.
        """
        # Extract the scale name from the raw score column name (e.g., "raw_scale_1" -> "scale_1")
        scale_name: str = re.sub(r"raw__|raw_corrected__|mean__", "", str(series.name))

        # Filter norms to include only those relevant to the current scale
        norms_to_use: pd.DataFrame = norms[norms["scale"].eq(scale_name)]

        # Sort the series by its values (required for `merge_asof`)
        sorted_series: pd.Series = series.sort_values()

        # Sort norms by the "raw" score column (required for `merge_asof`)
        sorted_norms: pd.DataFrame = norms_to_use.sort_values(by="raw")

        # Perform a nearest-neighbor lookup to map raw scores to standardized scores
        # Using merge_asof ensures mapping to the nearest standardized score.
        standard_scores: pd.DataFrame = pd.merge_asof(
            sorted_series,
            sorted_norms,
            left_on=str(series.name),
            right_on="raw",
            direction="nearest"
        )

        # Replace the index of standardized scores with the original series index
        standard_scores.index = sorted_series.index

        # Restore the original order of the series by sorting standardized scores by their index
        standard_scores = standard_scores.sort_index()

        # Convert the standardized scores to a list of dictionaries
        return standard_scores.iloc[:, 3:].to_dict(orient="records")

    def compute_standard_scores_for_group(
        self, group_data: pd.DataFrame) -> pd.DataFrame:
        """
        Computes standardized scores for a specific group of participants based on their norms.

        Args:
            grougroup_scoresp_data (pd.DataFrame): A DataFrame containing raw scores and the corresponding `norms_id` for a group.

        Returns:
            pd.DataFrame: A DataFrame containing standardized scores for the group,
                including optional interpretations if available in the norms dataset.
        """
        # Extract the norms_id for the current group
        group_norms_id: str = group_data["norms_id"].iloc[0]
        group_scores: pd.DataFrame = group_data.drop(columns=["norms_id"])

        # Parse the norms ID string into a list of applicable norms IDs
        norms_list: list[str] = group_norms_id.split(" ")

        # Extract relevant norms data based on the parsed norms IDs
        test_norms: pd.DataFrame = (
            self.data_container.test_norms[self.data_container.test_norms["norms_id"].isin(norms_list)]
        )

        # Identify relevant columns for standardized scores and interpretations
        relevant_columns: list[str] = [col for col in ["std", "std_interpretation"] if col in test_norms.columns]

        # Create a pivot table for norms, grouping by scale, raw values, and norms IDs
        norms_pivot: pd.DataFrame = test_norms.pivot_table(
            index=["scale", "raw"],
            columns=["norms_id"],
            values=relevant_columns,
            aggfunc=lambda x: x  # Preserve the original values
        ).reset_index()

        # Adjust the multi-index columns to a flat structure for easier manipulation
        norms_pivot.columns = norms_pivot.columns.map("{0[1]}_{0[0]}".format)
        norms_pivot.columns = norms_pivot.columns.str.replace(r"^_", "", regex=True).str.replace(r"_std", "", regex=True)

        # Compute standardized scores for each column in the group scores DataFrame
        return group_scores.apply(self.get_standard_scores_from_table, norms=norms_pivot)

    def compute_standard_scores(self) -> DataContainer:
        """
        Computes standardized scores for all participants and scales using norms data.

        Returns:
            DataContainer: The updated DataContainer instance with computed standardized scores added.
        """

        # If no norms are available, just return dataprovider
        if self.data_container.test_norms.empty:
            return self.data_container

        # Define the raw score type to perform standardization on
        type_of_raw_score: str = self.data_container.test_specs.get_spec("norms.type_of_raw_score")

        # Define the regex pattern for the raw score type
        type_of_raw_score_regex: str = rf"^{type_of_raw_score}__"

        # Combine test norms and raw scores into one DataFrame for processing
        test_scores_with_norms_id: pd.DataFrame = pd.concat(
            [
                self.data_container.data_norms,
                self.data_container.test_scores.filter(regex=type_of_raw_score_regex)
            ],
            axis=1
        )

        results = []
        for _, group in test_scores_with_norms_id.groupby(["norms_id"], sort=False):
            result = self.compute_standard_scores_for_group(group)
            results.append(result)

        self.data_container.test_standard_scores = (
            pd.concat(results)
            .add_prefix("std_")
            .sort_index()
        )

        # Return the updated DataContainer instance with standardized scores included
        return self.data_container
