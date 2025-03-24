import os  # Importing os module for interacting with the operating system
import subprocess  # Importing subprocess module for running subprocesses
import time  # Importing time module for time-related functions

from pathlib import Path  # Importing Path from pathlib for file path manipulations
from typing import Optional, Tuple, Union  # Importing typing for type hinting

from espada.core.base_execution_env import BaseExecutionEnv  # Importing BaseExecutionEnv as a base class for execution environments
from espada.core.default.file_store import FileStore  # Importing FileStore for file storage operations
from espada.core.files_dict import FilesDict  # Importing FilesDict for file dictionary operations


class DiskExecutionEnv(BaseExecutionEnv):

    def __init__(self, path: Union[str, Path, None] = None):
        self.files = FileStore(path)

    def upload(self, files: FilesDict) -> "DiskExecutionEnv":
        self.files.push(files)
        return self

    def download(self) -> FilesDict:
        return self.files.pull()

    def popen(self, command: str) -> subprocess.Popen:
        p = subprocess.Popen(
            command,
            shell=True,
            cwd=self.files.working_dir,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
        )
        return p

    def run(self, command: str, timeout: Optional[int] = None) -> Tuple[str, str, int]:
        start = time.time()
        print("\n--- Start of run ---")
        # Fix Windows line endings in shell scripts
        if command.startswith("bash "):
            for file in os.listdir(self.files.working_dir):
                if file.endswith(".sh"):
                    file_path = os.path.join(self.files.working_dir, file)
                    with open(file_path, "r") as f:
                        content = f.read()
                    with open(file_path, "w", newline="\n") as f:
                        f.write(content)

        # while running, also print the stdout and stderr
        p = subprocess.Popen(
            command,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            cwd=self.files.working_dir,
            text=True,
            shell=True,
        )
        print("$", command)
        stdout_full, stderr_full = "", ""

        try:
            while p.poll() is None:
                assert p.stdout is not None
                assert p.stderr is not None
                stdout = p.stdout.readline()
                stderr = p.stderr.readline()
                if stdout:
                    print(stdout, end="")
                    stdout_full += stdout
                if stderr:
                    print(stderr, end="")
                    stderr_full += stderr
                if timeout and time.time() - start > timeout:
                    print("Timeout!")
                    p.kill()
                    raise TimeoutError()
        except KeyboardInterrupt:
            print()
            print("Stopping execution.")
            print("Execution stopped.")
            p.kill()
            print()
            print("--- Finished run ---\n")

        return stdout_full, stderr_full, p.returncode
