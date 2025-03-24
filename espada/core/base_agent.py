from abc import ABC, abstractmethod  # Importing ABC and abstractmethod for creating abstract base classes
from typing import Optional  # Importing Optional for type hinting

from espada.core.files_dict import FilesDict  # Importing FilesDict from the files_dict module
from espada.core.prompt import Prompt  # Importing Prompt from the prompt module


class BaseAgent(ABC):  # Defining BaseAgent as an abstract base class

    @abstractmethod  # Decorator to define an abstract method
    def init(self, prompt: Prompt) -> FilesDict:  # Abstract method to initialize with a prompt and return a FilesDict
        pass  # Placeholder for the method implementation

    @abstractmethod  # Decorator to define an abstract method
    def improve(self, files_dict: FilesDict, prompt: Prompt) -> FilesDict:  # Abstract method to improve files based on a prompt and return a FilesDict
        pass  # Placeholder for the method implementation
