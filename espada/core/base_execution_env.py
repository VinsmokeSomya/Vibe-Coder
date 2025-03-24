from abc import ABC, abstractmethod  # Importing ABC and abstractmethod for creating abstract base classes
from subprocess import Popen  # Importing Popen for handling subprocesses
from typing import Optional, Tuple  # Importing Optional and Tuple for type hinting

from espada.core.files_dict import FilesDict  # Importing FilesDict from the files_dict module


class BaseExecutionEnv(ABC):
    # Abstract base class for execution environments

    @abstractmethod
    def run(self, command: str, timeout: Optional[int] = None) -> Tuple[str, str, int]:
        # Abstract method to run a command with an optional timeout
        raise NotImplementedError

    @abstractmethod
    def popen(self, command: str) -> Popen:
        # Abstract method to open a subprocess with the given command
        raise NotImplementedError

    @abstractmethod
    def upload(self, files: FilesDict) -> "BaseExecutionEnv":
        # Abstract method to upload files to the execution environment
        raise NotImplementedError

    @abstractmethod
    def download(self) -> FilesDict:
        # Abstract method to download files from the execution environment
        raise NotImplementedError
