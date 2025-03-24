from pathlib import Path  # Import Path class from pathlib module
from subprocess import TimeoutExpired  # Import TimeoutExpired exception from subprocess module
from typing import Union  # Import Union type from typing module

from datasets import Dataset, DatasetDict, load_dataset, load_from_disk  # Import necessary functions and classes from datasets module

from espada.benchmark.bench_config import AppsConfig  # Import AppsConfig class from bench_config module
from espada.benchmark.benchmarks.apps.problem import Problem  # Import Problem class from problem module
from espada.benchmark.types import Assertable, Benchmark, Task  # Import Assertable, Benchmark, and Task types from types module
from espada.core.default.disk_execution_env import DiskExecutionEnv  # Import DiskExecutionEnv class from disk_execution_env module
from espada.core.files_dict import FilesDict  # Import FilesDict class from files_dict module
from espada.core.prompt import Prompt  # Import Prompt class from prompt module

DATASET_PATH = Path(__file__).parent / "dataset"  # Define the path to the dataset directory


class AppsAssertion:
    def __init__(self, expected: str, command: str):
        self.expected_output = self._format(expected)
        self.command = command

    def evaluate(self, assertable: Assertable) -> bool:
        # Create new execution environment for every run to avoid side effects
        env = DiskExecutionEnv()
        env.upload(assertable.files)
        pro = env.popen(self.command)
        try:
            stdout, stderr = pro.communicate(timeout=2)
            stdout, stderr = stdout.decode("utf-8"), stderr.decode("utf-8")
        except TimeoutExpired:
            print("Execution Timeout")
            return False

        return self.expected_output in self._format(stdout)

    def _format(self, string: str) -> str:
        return string.replace(" ", "").replace("\n", "")


def _get_dataset() -> Union[Dataset, DatasetDict]:
    try:
        return load_from_disk(str(DATASET_PATH))
    except FileNotFoundError:
        print("Dataset not found locally, downloading...")

    dataset = load_dataset("codeparrot/apps", trust_remote_code=True)
    dataset.save_to_disk(str(DATASET_PATH))

    return dataset


def load_apps(config: AppsConfig) -> Benchmark:

    dataset = _get_dataset()
    tasks = []
    problems = list()
    for dataset_type in ["test", "train"]:
        problems += [
            Problem(
                id=problem["problem_id"],
                question=problem["question"],
                input_output=problem["input_output"],
                starter_code=problem["starter_code"],
            )
            for index, problem in enumerate(dataset[dataset_type])
            if (index < config.__getattribute__(dataset_type + "_end_index"))
            and (index >= config.__getattribute__(dataset_type + "_start_index"))
        ]

    for problem in problems:
        prompt = Prompt(
            problem.question
            + "\nThe program, including its inputs, should be run from the command "
            "line like 'python main \"input1 input2 etc \"', with all inputs inside "
            "the quotation marks. The program should not read inputs from stdin."
        )

        tasks.append(
            Task(
                name=str(problem.id),
                initial_code=FilesDict({"main.py": problem.starter_code}),
                command=None,  # Explicitly setting `None` because each assertion specifies its command
                prompt=prompt,
                assertions={
                    f"correct output {i}": AppsAssertion(
                        expected=problem.outputs[i],
                        command="python main.py" + ' "' + problem.inputs[i] + '"',
                    ).evaluate
                    for i in range(
                        min(len(problem.outputs), config.examples_per_problem)
                    )
                },
            )
        )

    return Benchmark(
        name="apps",
        tasks=tasks,
    )
