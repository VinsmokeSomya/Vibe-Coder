from pathlib import Path  # Importing Path from pathlib for file path manipulations
from typing import MutableMapping, Union  # Importing MutableMapping and Union from typing for type hinting

# Defining BaseMemory as a mutable mapping where keys can be either strings or Path objects, and values are strings
BaseMemory = MutableMapping[Union[str, Path], str]
