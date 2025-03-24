from espada.benchmark.bench_config import Espadar1Config  # Import Espadar1Config class for configuration
from espada.benchmark.types import Benchmark, Task  # Import Benchmark and Task types
from espada.core.files_dict import FilesDict  # Import FilesDict class for file management
from espada.core.prompt import Prompt  # Import Prompt class for task prompts

def load_espadar1(config: Espadar1Config) -> Benchmark:
    # Function to load the espadar1 benchmark with the given configuration

    return Benchmark(
        name="espadar1",  # Name of the benchmark
        tasks=[
            Task(
                name="hello",  # Task name
                initial_code=FilesDict({"hello.py": "print('Hello, world!')"}),  # Initial code for the task
                command="python hello.py",  # Command to execute the task
                prompt=Prompt("Change the code in hello.py to print 'Hello, human!'"),  # Prompt for the task
                assertions={
                    "correct output": lambda assertable: assertable.stdout
                    == "Hello, human!\n",  # Assertion for correct output
                    "correct file": lambda assertable: assertable.files[
                        "hello.py"
                    ].strip()
                    == "print('Hello, human!')",  # Assertion for correct file content
                },
            ),
            Task(
                name="hello-patch",  # Task name
                initial_code=FilesDict({"hello.py": "print('Hello, world!')"}),  # Initial code for the task
                command="python hello.py",  # Command to execute the task
                prompt=Prompt("Patch the code in hello.py to print 'Hello, human!'"),  # Prompt for the task
                assertions={
                    "correct output": lambda assertable: assertable.stdout
                    == "Hello, human!\n",  # Assertion for correct output
                    "correct file": lambda assertable: assertable.files[
                        "hello.py"
                    ].strip()
                    == "print('Hello, human!')",  # Assertion for correct file content
                },
            ),
            Task(
                name="hello-ask",  # Task name
                initial_code=FilesDict({"hello.py": "print('Hello, world!')"}),  # Initial code for the task
                command="echo 'Erik' | python hello.py",  # Command to execute the task with input
                prompt=Prompt(
                    "modify hello.py to ask the user for their name and print 'Hello, <name>!'. don't try to execute it"
                ),  # Prompt for the task
                assertions={
                    "correct output": lambda assertable: "Hello, Erik!"
                    in assertable.stdout,  # Assertion for correct output
                },
            ),
            Task(
                name="prime100",  # Task name
                initial_code=FilesDict(
                    {}
                ),  # Empty dictionary since no initial code is provided
                command="python prime.py",  # Command to execute the task
                prompt=Prompt(
                    "write a script prime.py that computes and prints the 100th prime number"
                ),  # Prompt for the task
                assertions={
                    "correct output": lambda assertable: "541"
                    in assertable.stdout.split(),  # Assertion for correct output
                },
            ),
            Task(
                name="init-git",  # Task name
                initial_code=FilesDict(
                    {}
                ),  # Empty dictionary since no initial code is provided
                command="git status",  # Command to execute the task
                prompt=Prompt(
                    "initialize a git repository, write a main.py file, and commit it"
                ),  # Prompt for the task
                assertions={
                    "clean exit": lambda assertable: assertable.process.returncode == 0,  # Assertion for clean exit
                    "clean working tree": lambda assertable: "nothing to commit, working tree clean"
                    in assertable.stdout,  # Assertion for clean working tree
                    "main.py exists": lambda assertable: "main.py" in assertable.files,  # Assertion for main.py existence
                    "we have a commit": lambda assertable: "No commits yet"
                    not in assertable.stdout,  # Assertion for having a commit
                },
            ),
        ],
    )
