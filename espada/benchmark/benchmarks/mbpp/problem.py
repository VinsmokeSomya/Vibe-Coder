from dataclasses import dataclass  # Import dataclass decorator from dataclasses module
from typing import List  # Import List type from typing module


@dataclass(frozen=True)  # Define a frozen dataclass named Problem
class Problem:
    source_file: int  # Integer representing the source file
    task_id: str  # String representing the task ID
    prompt: str  # String representing the prompt
    code: str  # String representing the code
    test_imports: str  # String representing the test imports
    test_list: List[str]  # List of strings representing the test list

    @property  # Define a property method
    def starting_code(self) -> str:
        lines: List[str] = []  # Initialize an empty list to store lines

        for line in self.code.split("\n"):  # Iterate over each line in the code
            lines.append(line)  # Append the line to the list

            if line.startswith("def "):  # Check if the line starts with "def "
                lines.append("pass #  TODO: Implement method\n")  # Append a placeholder line
                break  # Exit the loop

        return "\n".join(lines)  # Join the lines with newline characters and return the result
