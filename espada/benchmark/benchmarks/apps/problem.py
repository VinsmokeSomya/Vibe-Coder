import json  # Import json module for parsing JSON data

from dataclasses import dataclass  # Import dataclass decorator from dataclasses module
from functools import cached_property  # Import cached_property decorator from functools module
from typing import List  # Import List type from typing module


@dataclass(frozen=True)  # Define a frozen dataclass named Problem
class Problem:
    id: int  # Integer representing the problem ID
    question: str  # String representing the problem question
    input_output: str  # String representing the input and output data in JSON format
    starter_code: str  # String representing the starter code for the problem

    @property  # Define a property method
    def inputs(self) -> List[str]:
        return self._parsed_inputs_outputs["inputs"]  # Return the list of inputs

    @property  # Define a property method
    def outputs(self) -> List[str]:
        return self._parsed_inputs_outputs["outputs"]  # Return the list of outputs

    @cached_property  # Define a cached property method
    def _parsed_inputs_outputs(self):
        return json.loads(self.input_output.replace("\n", ""))  # Parse the input_output string as JSON and return the result
