from functools import cached_property
from typing import TYPE_CHECKING, Any

import numpy as np
import pandas as pd

if TYPE_CHECKING:
    from lib.data_container import DataContainer
    from lib.test_specs import TestSpecs


class Scorer:
    """
    A class to compute scores for group test data based on test specifications and norms.
    It handles the calculation of raw, raw corrected, and mean scores for straight and reversed items by scale.
    """

    def __init__(self, data_container: DataContainer) -> None:
        """
        Initializes the Scorer class with provided data.

        Args:
            data_container (DataContainer): Instance of DataContainer containing test specifications, answers, and norms.
        """
        self.data_container: DataContainer = data_container
        self.test_specs: TestSpecs = data_container.test_specs
        self.answers: pd.DataFrame = data_container.data_answers
        self.norms_id: pd.Series = data_container.data_norms
        self.straight_items_by_scale: pd.DataFrame
        self.reversed_items_by_scale: pd.DataFrame
        self.straight_items_by_scale, self.reversed_items_by_scale = self.convert_to_matrices()

    @cached_property
    def test_scales(self) -> Any:
        """
        Retrieves the names of the scales defined in the test specifications.

        Returns:
            pd.Index: A Pandas Index of the scale names.
        """
        return pd.Index([scale[0] for scale in self.test_specs.get_spec("scales")])

    @cached_property
    def count_items_by_scale(self) -> tuple[pd.Series, pd.Series]:
        """
        Counts the number of straight and reversed items for each scale.

        Returns:
            tuple[pd.Series, pd.Series]:
                - Count of straight items per scale.
                - Count of reversed items per scale.
        """
        return self.straight_items_by_scale.sum(), self.reversed_items_by_scale.sum()

    @cached_property
    def missing_items_by_scale(self) -> tuple[pd.DataFrame, pd.DataFrame]:
        """
        Calculates the number of missing items for straight and reversed items in each scale.

        Returns:
            tuple[pd.DataFrame, pd.DataFrame]:
                - Missing items for straight items by scale.
                - Missing items for reversed items by scale.
        """
        # Filter answers by scale items
        lambda_fn = lambda x: self.answers.T.loc[x.astype(bool).values].isna().sum()  # noqa: E731

        # Calculate missing for straight items
        missing_straight = self.straight_items_by_scale.apply(lambda_fn)

        # Calculate missing for reversed items
        missing_reversed = self.reversed_items_by_scale.apply(lambda_fn)

        # Return missing items (straight and reversed)
        return missing_straight, missing_reversed

    def convert_to_matrices(self) -> tuple[pd.DataFrame, pd.DataFrame]:
        """
        Maps test specifications' scale and item indices into 0-1 matrices for straight and reversed items.
        i.e.: 1,5,10 -> 1,0,0,0,1,0,0,0,0,1
        This is done for each scale defined in the test specifications.
        The resulting matrices are used for further calculations of raw scores.
        The function also handles the conversion of item indices from 1-based to 0-based indexing.

        Args:
            None

        Returns:
            Tuple[pd.DataFrame, pd.DataFrame]:
                - Matrix for straight items by scale.
                - Matrix for reversed items by scale.
        """
        # Matrix to store straight items and reversed items
        straight_items_matrix = pd.DataFrame()
        reversed_items_matrix = pd.DataFrame()

        # Iterate through scales defined in test specifications
        for scale in self.test_specs.get_spec("scales"):
            # Unpack the scale components
            scale_label, straight_items, reversed_items = scale
            for matrix, items in [(straight_items_matrix, straight_items),
                                   (reversed_items_matrix, reversed_items)]:
                # Initialize matrix with zeros and set the length based on test specifications
                items_series = pd.Series(np.zeros(self.test_specs.get_spec("length")))
                # Convert items position to a matrix of 0s and 1s (e.g., 1,4,5 ->  1,0,0,1,1)
                items_indices = pd.Series(items).sub(1)
                # Set the items in the series to 1
                items_series[items_indices] = 1
                # Assign the series to the corresponding scale in the matrix
                matrix[scale_label] = items_series

        # Return converted matrices
        return straight_items_matrix, reversed_items_matrix

    def compute_raw_score_component(self, items_by_scale: pd.DataFrame, fillna_value: int) -> pd.DataFrame:
        """
        Computes raw scores for a given type (straight or reversed) using matrix multiplication.

        Args:
            items_by_scale (pd.DataFrame): Binary matrix of items per scale.
            fillna_value (int): Value to use for filling missing data before computation.

        Returns:
            pd.DataFrame: DataFrame of raw scores for the given type of items.
        """
        # Compute raw scores through the dot product
        raw_scores = np.dot(
            self.answers.fillna(fillna_value).sub(fillna_value).abs(),
            items_by_scale
        )

        # Wrap results in a DataFrame for clarity and indexing
        return pd.DataFrame(raw_scores, index=self.answers.index, columns=self.test_scales)

    def compute_raw_scores(self) -> tuple[pd.DataFrame, pd.DataFrame]:
        """
        Computes raw scores for both straight and reversed items.

        Returns:
            tuple[pd.DataFrame, pd.DataFrame]:
                - Raw scores for straight items.
                - Raw scores for reversed items.
        """
        # Raw scores for straight items
        straight_scores = self.compute_raw_score_component(self.straight_items_by_scale, 0)

        # Raw scores for reversed items
        reversed_scores = self.compute_raw_score_component(
            self.reversed_items_by_scale,
            sum(self.test_specs.get_spec("likert").values())
        )

        # Return straight and reversed scores
        return straight_scores, reversed_scores

    def compute_raw_corrected_mean_scores(self) -> tuple[pd.DataFrame, pd.DataFrame, pd.DataFrame]:
        """
        Computes and returns raw, corrected raw, and mean scores across all test scales.

        Returns:
            Tuple[pd.DataFrame, pd.DataFrame, pd.DataFrame]:
                - Raw scores: Sum of straight and reversed scores.
                - raw corrected scores: Scores adjusted based on the number of answered items.
                - Mean scores: Raw scores divided by the number of answered items.
        """
        with np.errstate(divide="ignore", invalid="ignore"):
            # Get counts items by scale
            count_items_straight, count_items_reversed = self.count_items_by_scale

            # Get missing items by scale
            missing_straight, missing_reversed = self.missing_items_by_scale

            # Compute raw scores
            raw_straight, raw_reversed = self.compute_raw_scores()

            # Compute raw corrected scores per component (straight/reversed)
            raw_corrected_components = []
            for raw, missing, count in [
                (raw_straight, missing_straight, count_items_straight),
                (raw_reversed, missing_reversed, count_items_reversed)
            ]:
                items_answered = count - missing  # Number of answered items
                mean_scores = np.true_divide(raw, items_answered)  # Compute means
                raw_corrected_scores = np.nan_to_num(mean_scores) * count.values  # Adjusted raw scores
                raw_corrected_components.append(raw_corrected_scores)

            # Calculate final raw corrected scores
            raw_corrected_scores = pd.DataFrame(
                sum(raw_corrected_components),
                index=self.answers.index,
                columns=self.test_scales
            )

            # Calculate mean scores
            mean_scores = (raw_straight + raw_reversed).div(
                count_items_straight + count_items_reversed - missing_straight - missing_reversed
            )

            # Return all scores
            return \
                (raw_straight + raw_reversed).astype(int).astype(np.float64), \
                raw_corrected_scores.astype(int).astype(np.float64), \
                mean_scores.round(2).astype(np.float64)

    def compute_raw_related_scores(self) -> DataContainer:
        """
        Computes all test scores (raw, corrected, mean) and adds them to the DataContainer.

        Returns:
            DataContainer: Updated DataContainer instance with combined scores and missing item statistics.
        """
        # Calculate missing items
        missing_straight, missing_reversed = self.missing_items_by_scale
        missing_by_scale = missing_straight.add(missing_reversed)

        # Calculate raw related scores
        raw_scores, raw_corrected_scores, mean_scores = self.compute_raw_corrected_mean_scores()

        # Combine norms_id and scores into a single DataFrame
        test_scores = pd.concat([
            self.norms_id,
            missing_by_scale.add_prefix("missing__"),
            raw_scores.add_prefix("raw__"),
            raw_corrected_scores.add_prefix("raw_corrected__"),
            mean_scores.add_prefix("mean__"),
        ], axis=1)

        # Update data_container with the new scores
        self.data_container.test_scores = pd.concat([self.data_container.test_scores, test_scores])

        # Return updated data_container
        return self.data_container
