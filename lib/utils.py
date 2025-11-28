from typing import TYPE_CHECKING, Any

import numpy as np
import pandas as pd

if TYPE_CHECKING:
    from numpy.typing import NDArray

    from lib.test_specs import TestSpecs


def expand_dict_like_columns(df: pd.DataFrame, regex_for_dict_like: str) -> pd.DataFrame:
    """
    Expands dict-like (or JSON-like) columns in a DataFrame into separate columns.

    Args:
        df (pd.DataFrame): The input DataFrame containing dict-like columns to expand.
        regex_for_dict_like (str): A regex pattern to identify columns
                                   that contain dict-like structures.

    Returns:
        pd.DataFrame: A new DataFrame where designated dict-like columns
                      are expanded into individual columns, with their keys as new columns.
                      The names of the expanded columns are prefixed with the original column name.
    """
    # Identify dict-like columns in the DataFrame based on the provided regex pattern.
    dict_like_columns: pd.DataFrame = df.filter(regex=regex_for_dict_like)

    # Extract all non-dict-like columns by excluding dict-like ones.
    df_except_dictlike: pd.DataFrame = df.loc[:, ~(df.columns.isin(dict_like_columns.columns))]

    # Initialize the final DataFrame starting with non-dict-like columns.
    final_df: pd.DataFrame = df_except_dictlike

    # Iterate over the identified dict-like columns to expand their contents.
    for col_dict_name, col_dict in dict_like_columns.items():
        # Expand each dict-like column using `pd.json_normalize` and add a prefix for clarity.
        expanded_column: pd.DataFrame = (
            pd.json_normalize(col_dict, meta_prefix="_") # type: ignore[arg-type]
                .add_prefix(f"{col_dict_name}.")
        )

        # Concatenate the expanded columns into the final DataFrame.
        final_df = pd.concat([final_df, expanded_column], axis=1)

    # Return the new DataFrame with expanded columns.
    return final_df


def create_normative_table(test_specs: TestSpecs, norms_data: pd.DataFrame) -> pd.DataFrame:
    """
    Creates a normative table for psychological scales based on test specifications
    and normative data. The resulting table includes raw scores and corresponding
    normalized T-scores for each scale.

    Args:
        test_specs (TestSpecs): An object providing configuration for test
                                specifications such as maximum Likert scale values
                                and scale definitions (names and items for each scale).
        norms_data (pd.DataFrame): A DataFrame containing the normative data for the scales.
                                   This must include scale names, mean scores, standard
                                   deviations ('ds'), and a unique norms ID for each entry.

    Returns:
        pd.DataFrame: A DataFrame containing the normative T-scores table with the following columns:
                      - 'norms_id': ID of the normative data entry.
                      - 'scale': Name of the psychological scale.
                      - 'raw': The raw scores.
                      - 'std': The standardized T-scores (scaled between 0 and 150).
    """
    # Initialize an empty DataFrame to store the normative table.
    norms_table: pd.DataFrame = pd.DataFrame()

    # Get the maximum Likert-scale value from test specifications.
    likert_max: int = test_specs.get_spec("likert.max")

    # Get type of raw score
    type_of_raw_score: str = test_specs.get_spec("norms.type_of_raw_score")

    # Iterate over norms_id
    for norms_id in norms_data["norms_id"].unique():

        # Iterate over each scale defined in the test specifications.
        for scale_name, items_straight, items_reversed in test_specs.get_spec("scales"):

            # Filter the norms data for the current scale and norms_id.
            condition: NDArray[np.bool_] = np.logical_and(
                norms_data["norms_id"].eq(norms_id),
                norms_data["scale"].eq(scale_name)
            )

            # Filter the norms data for the current scale.
            scale_norms_data: pd.DataFrame = norms_data[condition]

            # Extract the mean and standard deviation ('ds') for the current scale.
            scale_mean: float = scale_norms_data["mean"].iloc[0]
            scale_ds: float = scale_norms_data["ds"].iloc[0]

            # Calculate the total number of items in the scale.
            scale_length: int = len([*items_straight, *items_reversed])
            # Generate the range of raw scores depending on the specified type.
            if type_of_raw_score == "mean":
                # Raw scores are generated with steps of 0.05 if type is 'mean'.
                scale_raw_scores: pd.Series[Any] = pd.Series(np.arange(0, likert_max + 0.05, 0.05)).round(2)
            else:
                # Raw scores are integers up to the maximum possible score.
                scale_raw_scores = pd.Series(range(0, scale_length * likert_max + 1))

            # Compute the normative table entries for the current scale.
            scale_norms = pd.DataFrame({
                "norms_id": norms_id,   # Norms ID.
                "scale": scale_name,                                # Scale name.
                "raw": scale_raw_scores,                            # Raw scores.
                "std": scale_raw_scores
                        .sub(scale_mean)                               # Subtract the mean.
                        .div(scale_ds)                                 # Divide by the standard deviation.
                        .mul(10)                                       # Multiply by 10 to calculate T-scores.
                        .add(50)                                       # Add 50 to adjust to T-score range.
                        .clip(0, 200)                                 # Clip values between 0 and 200
                        .astype(int),                                  # Convert T-scores to integers.
                "std_interpretation": "◦"                          # Placeholder for interpretation.
            })

            # Append the current scale's normative data to the overall table.
            norms_table = pd.concat([norms_table, scale_norms])

    # Reset the index of the final norms table and return it.
    return norms_table.reset_index(drop=True)
