from functools import cached_property
from typing import TYPE_CHECKING

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

    @cached_property
    def test_scales(self) -> list[str]:
        """
        Retrieves the names of the scales defined in the test specifications.

        Returns:
            list[str]: A list of the scale names.
        """
        return [scale[0] for scale in self.test_specs.get_spec("scales")]

    @cached_property
    def straight_items_by_scale(self) -> pd.DataFrame:
        """
        Binary matrix for straight items by scale.

        Returns:
            pd.DataFrame: Matrix where each column represents a scale and rows represent items.
        """
        return self._convert_to_matrix(item_type="straight")

    @cached_property
    def reversed_items_by_scale(self) -> pd.DataFrame:
        """
        Binary matrix for reversed items by scale.

        Returns:
            pd.DataFrame: Matrix where each column represents a scale and rows represent items.
        """
        return self._convert_to_matrix(item_type="reversed")

    def _convert_to_matrix(self, item_type: str) -> pd.DataFrame:
        """
        Maps test specifications' scale and item indices into 0-1 matrices.

        Args:
            item_type (str): Either "straight" or "reversed"

        Returns:
            pd.DataFrame: Binary matrix of items by scale.
        """
        n_items = self.test_specs.get_spec("length")
        n_scales = len(self.test_scales)

        # Pre-allocate matrix
        matrix = np.zeros((n_items, n_scales), dtype=np.int8)

        # Fill matrix
        item_idx = 1 if item_type == "straight" else 2
        for scale_idx, scale in enumerate(self.test_specs.get_spec("scales")):
            # Get items for the specified type
            items = scale[item_idx]
            # Check if there are any items
            if items:
                # Convert to 0-based indexing
                items_indices = np.array(items) - 1
                # Set corresponding positions to 1
                # (indicating presence of item in scale)
                matrix[items_indices, scale_idx] = 1

        return pd.DataFrame(matrix, columns=self.test_scales)

    @cached_property
    def count_items_by_scale(self) -> pd.DataFrame:
        """
        Counts the number of straight and reversed items for each scale.

        Returns:
            pd.DataFrame: DataFrame with 'straight' and 'reversed' rows, scales as columns.
        """
        counts = np.vstack([
            self.straight_items_by_scale.values.sum(axis=0),
            self.reversed_items_by_scale.values.sum(axis=0)
        ])
        return pd.DataFrame(
            counts,
            index=["straight", "reversed"],
            columns=self.test_scales
        )

    @cached_property
    def missing_items_by_scale(self) -> pd.DataFrame:
        """
        Calculates the number of missing items for straight and reversed items in each scale for each person.

        Returns:
            pd.DataFrame: DataFrame with scales as columns and MultiIndex ['straight', 'reversed'] showing missing counts.
        """
        # Vectorized computation using numpy @ operator
        answers_isna = self.answers.isna().values  # (n_persons, n_items)

        # Matrix multiplication: (n_persons, n_items) @ (n_items, n_scales)
        missing_straight = answers_isna @ self.straight_items_by_scale.values  # (n_persons, n_scales)
        missing_reversed = answers_isna @ self.reversed_items_by_scale.values  # (n_persons, n_scales)

        # Concatenate as separate columns with prefixes
        # The resulting DataFrame will have a MultiIndex for columns
        # Like: ('straight', scale1), ('straight', scale2), ... ('reversed', scale1), ('reversed', scale2), ...
        return pd.concat([
            pd.DataFrame(missing_straight, index=self.answers.index, columns=self.test_scales),
            pd.DataFrame(missing_reversed, index=self.answers.index, columns=self.test_scales)
        ], keys=['straight', 'reversed'], axis=1)

    @cached_property
    def missing_by_scale(self) -> pd.DataFrame:
        """
        Total missing items by scale (straight + reversed) for each person.

        Returns:
            pd.DataFrame: Total missing items per person per scale.
        """
        answers_isna = self.answers.isna().values
        total_items_matrix = self.straight_items_by_scale.values + self.reversed_items_by_scale.values
        total_missing = answers_isna @ total_items_matrix

        return pd.DataFrame(
            total_missing,
            index=self.answers.index,
            columns=self.test_scales
        ).astype(int)

    @cached_property
    def raw_scores_straight(self) -> pd.DataFrame:
        """
        Computes raw scores for straight items.

        Returns:
            pd.DataFrame: Raw scores for straight items (persons x scales).
        """
        # Fill NaN with 0, then matrix multiply
        raw_scores = self.answers.fillna(0).values @ self.straight_items_by_scale.values
        return pd.DataFrame(raw_scores, index=self.answers.index, columns=self.test_scales)

    @cached_property
    def raw_scores_reversed(self) -> pd.DataFrame:
        """
        Computes raw scores for reversed items.

        Returns:
            pd.DataFrame: Raw scores for reversed items (persons x scales).
        """
        # Maximum possible score for likert scale
        likert_sum = sum(self.test_specs.get_spec("likert").values())

        # Reverse scoring: |likert_sum - answer|
        raw_scores = (
            self.answers.fillna(likert_sum)
                .rsub(likert_sum).values @ self.reversed_items_by_scale.values
        )

        return pd.DataFrame(raw_scores, index=self.answers.index, columns=self.test_scales)

    @cached_property
    def raw_scores(self) -> pd.DataFrame:
        """
        Computes total raw scores (straight + reversed).

        Returns:
            pd.DataFrame: Total raw scores per person per scale.
        """
        return (self.raw_scores_straight + self.raw_scores_reversed).astype(np.float64)

    @cached_property
    def raw_corrected_scores(self) -> pd.DataFrame:
        """
        Computes raw corrected scores adjusted for missing items.
        Raw corrected score = mean score x number of items per scale

        Returns:
            pd.DataFrame: Raw corrected scores per scale.
        """
        # Total number of items per scale (straight + reversed)
        total_items_per_scale = self.count_items_by_scale.sum(axis=0).values

        # Raw corrected = mean score x total items in scale
        raw_corrected = self.mean_scores.values * total_items_per_scale

        return pd.DataFrame(
            raw_corrected,
            index=self.answers.index,
            columns=self.test_scales
        ).astype(np.float64)

    @cached_property
    def mean_scores(self) -> pd.DataFrame:
        """
        Computes mean scores per scale.

        Returns:
            pd.DataFrame: Mean scores per scale.
        """
        with np.errstate(divide="ignore", invalid="ignore"):
            # Total items answered per scale
            total_items = self.count_items_by_scale.sum(axis=0).values
            total_missing = self.missing_by_scale.values
            items_answered = total_items - total_missing

            # Compute mean
            mean = self.raw_scores.values / items_answered

            return pd.DataFrame(
                np.round(mean, 2),
                index=self.answers.index,
                columns=self.test_scales
            ).astype(np.float64)

    @cached_property
    def test_scores(self) -> pd.DataFrame:
        """
        Computes all test scores (raw, corrected, mean) combined with norms and missing data.

        Returns:
            pd.DataFrame: Combined DataFrame with all scoring information.
        """
        # Combine all scores
        return pd.concat([
            self.norms_id,
            self.missing_by_scale.add_prefix("missing__"),
            self.raw_scores.astype(int).add_prefix("raw__"),
            self.raw_corrected_scores.astype(int).add_prefix("raw_corrected__"),
            self.mean_scores.add_prefix("mean__"),
        ], axis=1)

    def compute_raw_related_scores(self) -> DataContainer:
        """
        Computes all test scores and adds them to the DataContainer.

        Returns:
            DataContainer: Updated DataContainer instance with combined scores.
        """
        # Update data_container with the test scores (uses cached property)
        self.data_container.test_scores = self.test_scores

        # Return updated data_container
        return self.data_container
