from typing import TYPE_CHECKING, Any, Literal

import numpy as np
import orjson
import pandas as pd

from lib import BASE_PATH, DATA_PATH, LIB_PATH, TESTS_PATH, XEROX_PATH
from lib.errors import NotFoundError

if TYPE_CHECKING:
    from pathlib import Path


class DataProvider:
    """
    Handles base folder paths and file management for the project.
    Provides methods to retrieve paths and load test data, specifications, and norms.
    """

    def __init__(self, test_name: str) -> None:
        """
        Initializes a `DataProvider` instance, setting up and validating base folder paths.

        Args:
            test_name (str): The name of the test for which paths and files will be managed.

        Attributes:
            test_name (str): The name of the test.
            base_folderpaths (dict[str, Path]): A dictionary mapping folder names to their corresponding `Path` objects.
        """
        self.test_name: str = test_name
        self.base_folderpaths: dict[str, Path] = self.set_base_folderpaths()

    def set_base_folderpaths(self) -> dict[str, Path]:
        """
        Defines and validates the base folder paths for the project.

        Returns:
            dict[str, Path]: A dictionary mapping folder names ('cwd', 'data', 'xerox', 'lib', 'tests')
                             to their respective `Path` objects.

        Raises:
            NotFoundError: If any required folder paths are missing.
        """
        base_folderpaths = {
            "cwd": BASE_PATH,  # Current working directory
            "data": DATA_PATH,  # Path to the data directory
            "xerox": XEROX_PATH,  # Path to the Xerox directory
            "lib": LIB_PATH,  # Path to the library directory
            "tests": TESTS_PATH,  # Path to the tests directory
        }

        # Ensures that all defined folder paths exist
        if all(folder.exists() for folder in base_folderpaths.values()):
            return base_folderpaths
        else:
            missing_paths = [
                str(folder)
                for folder in base_folderpaths.values()
                if not folder.exists()
            ]
            raise NotFoundError(f"The following paths are missing: {missing_paths}")

    def get_folderpath(
        self, folderpath: Literal["cwd", "data", "xerox", "lib", "tests"]
    ) -> Path:
        """
        Retrieves the path of a specified folder.

        Args:
            folderpath (Literal["cwd", "data", "xerox", "lib", "tests"]):
                The name of the folder to retrieve.

        Returns:
            Path: The `Path` object for the specified folder.
        """
        return self.base_folderpaths[folderpath]

    def get_test_path(self, type: Literal["data", "specs", "norms"]) -> Path:
        """
        Retrieves the relative path to a specific test-related file.

        Args:
            type (Literal["data", "specs", "norms"]): The type of test file.
                - "data"  -> Test's data CSV file.
                - "specs" -> Test's specifications JSON file.
                - "norms" -> Test's norms CSV file.

        Returns:
            Path: The relative path to the specified test file.
        """
        # Handle data files
        if type == "data":

            # Use glob to find all files matching data in filename
            data_files: list[Path] = list(self.get_folderpath("data").glob(f"*{self.test_name}*.csv"))

            # Ensure at least one file is found
            if not data_files:
                raise FileNotFoundError(f"No data files found for test {self.test_name}")

            # Notify user in case of multiple files found
            if len(data_files) > 1:
                print(  # noqa: T201
                    f"Multiple data files found for test {self.test_name}. "
                    f"Using the most recently modified one: {data_files[0].name}"
                )

            # Sort files by modification time, descending
            data_files.sort(key=lambda x: x.stat().st_mtime, reverse=True)

            # Assume the most recently modified file is the correct one
            filepath = data_files[0]

        # Handle norms
        elif type == "norms":
            filepath = (
                self.get_folderpath("tests")
                / self.test_name
                / f"{self.test_name}_norms.csv"
            )
        # Handle specs
        else:
            filepath = (
                self.get_folderpath("tests")
                / self.test_name
                / f"{self.test_name}_specs.json"
            )

        return filepath.relative_to(BASE_PATH)

    def load_test_data(self) -> pd.DataFrame:
        """
        Loads the test's raw data from a CSV file.

        Returns:
            pd.DataFrame: A DataFrame containing the raw test data.

        Raises:
            FileNotFoundError: If the data file does not exist.
        """
        # Get the path to the test data file
        data_filepath: Path = self.get_test_path("data")

        # Load a maximum of 1000 rows
        limited_df: pd.DataFrame = pd.read_csv(data_filepath, nrows=1000)

        return limited_df

    def load_test_specifications(self) -> Any:
        """
        Loads test-specific specifications from a JSON file.

        Returns:
            dict: A dictionary containing the test's specifications.

        Raises:
            FileNotFoundError: If the specification file does not exist.
        """
        # Get the path to the test specs
        test_specs_filepath: Path = self.get_test_path("specs")

        # Raise error if specs file does not exist
        if not test_specs_filepath.exists():
            raise FileNotFoundError(f"Test specifications file not found at {test_specs_filepath}")

        # Parse test specs
        with test_specs_filepath.open("rb") as file:
            test_specs_json = orjson.loads(file.read())

        return test_specs_json

    def load_test_norms(self) -> pd.DataFrame:
        """
        Loads norms data for the test from a CSV file, if it exists.

        Returns:
            pd.DataFrame: A DataFrame containing the norms data.
                          If the file does not exist, returns an empty DataFrame.
        """
        # Get path to norms
        norms_filepath: Path = self.get_test_path("norms")

        # Read norms if they exist
        if norms_filepath.exists():
            return pd.read_csv(
                norms_filepath, dtype={"raw": np.float64, "std": np.float64}
            )
        else:
            # Retrun void DataFrame
            return pd.DataFrame()

    def persist(self, data: pd.DataFrame | dict[str, Any]) -> None:
        # If data is an instance of pd.Dataframe, save it as a csv
        if isinstance(data, pd.DataFrame):
            data.to_csv(
                self.get_folderpath("xerox") / f"{self.test_name}_scored.csv",
                index=False,
            )

        # If data is a dict, save it as a json
        elif isinstance(data, dict):
            with (self.get_folderpath("xerox") / f"{self.test_name}_scored.json").open(
                "wb"
            ) as fout:
                fout.write(orjson.dumps(data, option=orjson.OPT_INDENT_2))
