# Import necessary modules and classes
from dataclasses import dataclass
from subprocess import Popen
from typing import Callable, Dict, Optional

from espada.core.base_execution_env import BaseExecutionEnv
from espada.core.files_dict import FilesDict
from espada.core.prompt import Prompt

# Define a dataclass for Assertable
@dataclass
class Assertable:
    # Files involved in the assertion
    files: FilesDict
    # Execution environment
    env: BaseExecutionEnv
    # Process being executed
    process: Optional[Popen]
    # Standard output from the process
    stdout: Optional[str]
    # Standard error from the process
    stderr: Optional[str]

# Type alias for an assertion function
Assertion = Callable[[Assertable], bool]

# Define a dataclass for Task
@dataclass
class Task:
    # Name of the task
    name: str
    # Initial code files for the task
    initial_code: Optional[FilesDict]
    # Command to execute the task
    command: Optional[str]
    # Prompt associated with the task
    prompt: Prompt
    # Assertions to validate the task
    assertions: Optional[Dict[str, Assertion]]

# Define a dataclass for Benchmark
@dataclass
class Benchmark:
    """A benchmark is a collection of tasks that evaluate a model's performance."""

    # Name of the benchmark
    name: str
    # List of tasks in the benchmark
    tasks: list[Task]
    # Timeout for the benchmark
    timeout: Optional[int] = None

# Define a dataclass for TaskResult
@dataclass
class TaskResult:
    # Name of the task
    task_name: str
    # Results of assertions
    assertion_results: dict[str, bool]
    # Duration of the task execution
    duration: float

    # Returns success rate from 0.00 up to 1.00
    @property
    def success_rate(self) -> float:
        # If no assertions, return 0.0
        if not self.assertion_results:
            return 0.0

        # Count the number of successful assertions
        succeeded = len(
            [result for result in self.assertion_results.values() if result is True]
        )

        # Calculate success rate
        return succeeded / len(self.assertion_results)

    # Convert TaskResult to a dictionary
    def to_dict(self) -> dict:
        # Create a dictionary from the TaskResult attributes
        out_dict = {key: value for key, value in self.__dict__.items()}
        # Add the success rate to the dictionary
        out_dict["solved"] = self.success_rate
        return out_dict
