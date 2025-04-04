from functools import reduce
from typing import Any, Union, List, Literal, Tuple
from pydantic import BaseModel, Field, ValidationError, field_validator


class Likert(BaseModel):
    """
    Represents a Likert scale configuration with minimum and maximum values for the scale.
    """
    min: int = Field(..., description="The minimum value of the Likert scale.")
    max: int = Field(..., description="The maximum value of the Likert scale. Must be greater than 'min'.")

    @field_validator("max")
    @classmethod
    def max_greater_than_min(cls, value: int, info) -> int:
        """
        Validate that the 'max' value is greater than the 'min' value.

        Args:
            value (int): The maximum value of the Likert scale.
            info: Pydantic validation information that includes the 'min' value.

        Returns:
            int: The validated 'max' value.

        Raises:
            ValueError: If the 'max' value is not greater than the 'min' value.
        """
        if value <= info.data["min"]:
            raise ValueError("The 'max' value must be greater than the 'min' value.")
        return value


class Norms(BaseModel):
    """
    Represents the configuration of norms and the type of raw score used for norms.
    """
    available_norms: List[str] = Field(..., description="List containing available norms.")
    type_of_raw_score: Literal["raw", "raw_corrected", "mean"] = Field(
        ..., description="The type of raw score used for norms (raw, raw_corrected, or mean)."
    )


class TestSpecsModel(BaseModel):
    """
    Defines the structure and constraints for test specifications using Pydantic.
    """
    name: str = Field(..., description="The name of the test specification.")
    length: int = Field(..., gt=0, description="The number of test items. Must be greater than 0.")
    likert: Likert
    scales: List[Tuple[str, List[int], List[int]]] = Field(
        ..., description="List of scales, each defined with a name and two index lists (straight and reversed)."
    )
    norms: Norms
    report: str = Field(..., description="The report name associated with the test.")

    @field_validator("scales")
    @classmethod
    def validate_scales(cls, scales: List[Tuple[str, List[int], List[int]]], info) -> List[Tuple[str, List[int], List[int]]]:
        """
        Validate the 'scales' field for proper formatting and constraints.

        Args:
            scales (List[Tuple[str, List[int], List[int]]]): A list of scales with their respective indices.
            info: Pydantic validation information that includes the 'length' of the test.

        Returns:
            List[Tuple[str, List[int], List[int]]]: The validated list of scales.

        Raises:
            ValueError: If any scale contains duplicates, indices exceeding test length, or other constraints.
        """
        # Retrieve the test length for validation.
        length = info.data.get("length")

        # Ensure length is provided before validating scales.
        if length is None:
            raise ValueError("'length' must be provided before validating scales.")

        # Validate each scale's structure and constraints.
        for scale in scales:
            # Unpack the scale components.
            scale_name, first_list, second_list = scale

            # Check for duplicate indices within the individual lists.
            if len(first_list) != len(set(first_list)):
                raise ValueError(f"Duplicate items found within the first list of scale '{scale_name}'.")
            if len(second_list) != len(set(second_list)):
                raise ValueError(f"Duplicate items found within the second list of scale '{scale_name}'.")

            # Validate that indices do not exceed the test length.
            if any(index > length for index in first_list):
                raise ValueError(f"Straight item indices of scale '{scale_name}' exceed the test length: {length}.")
            if any(index > length for index in second_list):
                raise ValueError(f"Reversed item indices of scale '{scale_name}' exceed the test length: {length}.")

        return scales


class TestSpecs:
    """
    Manages and accesses test specifications stored in a dictionary format.
    Provides functionality to retrieve nested data using dot-separated JSON paths.
    """

    def __init__(self, data: dict) -> None:
        """
        Initialize a `TestSpecs` instance with the given test specifications.

        Args:
            data (dict): A dictionary containing the test specifications.

        Raises:
            ValidationError: If the data does not satisfy the `TestSpecsModel` constraints.
        """
        try:
            # Validate the input data using the Pydantic model.
            _ = TestSpecsModel(**data)

            # Store the validated test specifications.
            self.test_specs = data
        
        except ValidationError as e:
            print("Validation Error Occurred!")
            raise e

    def get_spec(self, path: Union[str, None]) -> Any:
        """
        Retrieve a specific value from the test specifications using a dot-separated JSON path.

        Args:
            path (Union[str, None]): A dot-separated string specifying the hierarchical keys to the desired value.
                                     If None, the full test specifications are returned.

        Returns:
            Any: The value corresponding to the given path. If the path is invalid or a key is missing,
                 an empty dictionary is returned.
        """
        # Return the full specifications if no path is provided.
        if not path:
            return self.test_specs

        # Split the path into individual keys.
        path_bits = path.split(".")

        # Traverse the nested dictionary and return the appropriate value.
        return reduce(lambda acc, key: acc.get(key, {}), path_bits, self.test_specs)
