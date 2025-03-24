# Version Manager Module
# This module provides an abstract base class for a version manager that handles the creation of snapshots for code. 

from abc import ABC, abstractmethod  # Importing abstract base class and abstract method decorator
from pathlib import Path  # Importing Path class for filesystem paths
from typing import Union  # Importing Union type for type hinting

from espada.core.files_dict import FilesDict  # Importing FilesDict from espada.core.files_dict


class BaseVersionManager(ABC):  # Defining an abstract base class for version management

    @abstractmethod
    def __init__(self, path: Union[str, Path]):  # Abstract method for initializing with a path
        pass

    @abstractmethod
    def snapshot(self, files_dict: FilesDict) -> str:  # Abstract method for creating a snapshot from FilesDict
        pass
