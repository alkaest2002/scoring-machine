import json
import numpy as np
import pandas as pd
from pathlib import Path
from typing import Literal, Union
from lib.errors import NotFoundError
from lib import BASE_PATH, DATA_PATH, XEROX_PATH, LIB_PATH, TESTS_PATH


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
        self.test_name = test_name
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
            "cwd": BASE_PATH,     # Current working directory
            "data": DATA_PATH,    # Path to the data directory
            "xerox": XEROX_PATH,  # Path to the Xerox directory
            "lib": LIB_PATH,      # Path to the library directory
            "tests": TESTS_PATH   # Path to the tests directory
        }

        # Ensures that all defined folder paths exist
        if all(folder.exists() for folder in base_folderpaths.values()):
            return base_folderpaths
        else:
            missing_paths = [str(folder) for folder in base_folderpaths.values() if not folder.exists()]
            raise NotFoundError(f"The following paths are missing: {missing_paths}")

    def get_folderpath(self, folderpath: Literal["cwd", "data", "xerox", "lib", "tests"]) -> Path:
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
        if type == "data":
            filepath = self.get_folderpath("data") / f"{self.test_name}_data.csv"
        elif type == "norms":
            filepath = self.get_folderpath("tests") / self.test_name / f"{self.test_name}_norms.csv"
        else:
            filepath = self.get_folderpath("tests") / self.test_name / f"{self.test_name}_specs.json"
        
        return filepath.relative_to(BASE_PATH)

    def load_test_data(self) -> pd.DataFrame:
        """
        Loads the test's raw data from a CSV file.

        Returns:
            pd.DataFrame: A DataFrame containing the raw test data.

        Raises:
            FileNotFoundError: If the data file does not exist.
        """
        data_filepath = self.get_test_path("data")
        return pd.read_csv(data_filepath)

    def load_test_specifications(self) -> dict:
        """
        Loads test-specific specifications from a JSON file.

        Returns:
            dict: A dictionary containing the test's specifications.

        Raises:
            FileNotFoundError: If the specification file does not exist.
        """
        test_specs_filepath = self.get_test_path("specs")
        
        with test_specs_filepath.open() as file:
            test_specs_json = json.load(file)
        
        return test_specs_json

    def load_test_norms(self) -> pd.DataFrame:
        """
        Loads norms data for the test from a CSV file, if it exists.

        Returns:
            pd.DataFrame: A DataFrame containing the norms data. 
                          If the file does not exist, returns an empty DataFrame.
        """
        norms_filepath = self.get_test_path("norms")

        if norms_filepath.exists():
            return pd.read_csv(norms_filepath, dtype={"raw": np.float64, "std": np.float64})
        else:
            return pd.DataFrame()
        
    def persist(self, data: Union[pd.DataFrame, dict]) -> None:

        # If data is an instance of pd.Dataframe, save it as a csv
        if isinstance(data, pd.DataFrame):
            data.to_csv(self.get_folderpath("xerox") / f"{self.test_name}_scored.csv", index=False)
        
        # If data is a dict, save it as a json 
        elif isinstance(data, dict):
            with open(self.get_folderpath("xerox") / f"{self.test_name}_scored.json", "w") as fout:
                json.dump(data, fout, indent=2)