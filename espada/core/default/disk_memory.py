import base64  # Importing base64 for encoding binary data to ASCII
import json  # Importing json for JSON operations
import shutil  # Importing shutil for file operations

from datetime import datetime  # Importing datetime for date and time operations
from pathlib import Path  # Importing Path for file path manipulations
from typing import Any, Dict, Iterator, Optional, Union  # Importing typing for type hinting

from espada.core.base_memory import BaseMemory  # Importing BaseMemory as a base class for memory operations
from espada.tools.supported_languages import SUPPORTED_LANGUAGES  # Importing supported languages for file extension validation


# This class represents a simple database that stores its tools as files in a directory.
class DiskMemory(BaseMemory):

    def __init__(self, path: Union[str, Path]):
        # Initialize the DiskMemory with a given path
        self.path: Path = Path(path).absolute()  # Set the absolute path

        self.path.mkdir(parents=True, exist_ok=True)  # Create the directory if it doesn't exist

    def __contains__(self, key: str) -> bool:
        # Check if a file with the given key exists
        return (self.path / key).is_file()

    def __getitem__(self, key: str) -> str:
        # Retrieve the content of a file with the given key
        full_path = self.path / key  # Determine the full path

        if not full_path.is_file():
            raise KeyError(f"File '{key}' could not be found in '{self.path}'")  # Raise an error if the file doesn't exist

        if full_path.suffix in [".png", ".jpeg", ".jpg"]:  # Check if the file is an image
            with full_path.open("rb") as image_file:  # Open the image file in binary mode
                encoded_string = base64.b64encode(image_file.read()).decode("utf-8")  # Encode the image to base64
                mime_type = "image/png" if full_path.suffix == ".png" else "image/jpeg"  # Determine the MIME type
                return f"data:{mime_type};base64,{encoded_string}"  # Return the base64 encoded image
        else:
            with full_path.open("r", encoding="utf-8") as f:  # Open the file in text mode
                return f.read()  # Return the file content

    def get(self, key: str, default: Optional[Any] = None) -> Any:
        # Get the content of a file or directory with a default value
        item_path = self.path / key  # Determine the item path
        try:
            if item_path.is_file():
                return self[key]  # Return the file content
            elif item_path.is_dir():
                return DiskMemory(item_path)  # Return a DiskMemory instance for the directory
            else:
                return default  # Return the default value
        except:
            return default  # Return the default value in case of an exception

    def __setitem__(self, key: Union[str, Path], val: str) -> None:
        # Set the content of a file with the given key
        if str(key).startswith("../"):
            raise ValueError(f"File name {key} attempted to access parent path.")  # Prevent accessing parent paths

        if not isinstance(val, str):
            raise TypeError("val must be str")  # Ensure the value is a string

        full_path = self.path / key  # Determine the full path
        full_path.parent.mkdir(parents=True, exist_ok=True)  # Create parent directories if needed

        full_path.write_text(val, encoding="utf-8")  # Write the content to the file

    def __delitem__(self, key: Union[str, Path]) -> None:
        # Delete a file or directory with the given key
        item_path = self.path / key  # Determine the item path
        if not item_path.exists():
            raise KeyError(f"Item '{key}' could not be found in '{self.path}'")  # Raise an error if the item doesn't exist

        if item_path.is_file():
            item_path.unlink()  # Delete the file
        elif item_path.is_dir():
            shutil.rmtree(item_path)  # Delete the directory

    def __iter__(self) -> Iterator[str]:
        # Iterate over all files in the directory
        return iter(
            sorted(
                str(item.relative_to(self.path))  # Get the relative path of each file
                for item in sorted(self.path.rglob("*"))  # Recursively find all files
                if item.is_file()  # Check if the item is a file
            )
        )

    def __len__(self) -> int:
        # Get the number of files in the directory
        return len(list(self.__iter__()))

    def _supported_files(self) -> str:
        # Get a list of supported files based on their extensions
        valid_extensions = {
            ext for lang in SUPPORTED_LANGUAGES for ext in lang["extensions"]  # Collect valid extensions
        }
        file_paths = [
            str(item)
            for item in self
            if Path(item).is_file() and Path(item).suffix in valid_extensions  # Check if the file has a valid extension
        ]
        return "\n".join(file_paths)  # Return the list of supported files

    def _all_files(self) -> str:
        # Get a list of all files in the directory
        file_paths = [str(item) for item in self if Path(item).is_file()]  # Collect all file paths
        return "\n".join(file_paths)  # Return the list of all files

    def to_path_list_string(self, supported_code_files_only: bool = False) -> str:
        # Get a string representation of file paths
        if supported_code_files_only:
            return self._supported_files()  # Return only supported files
        else:
            return self._all_files()  # Return all files

    def to_dict(self) -> Dict[Union[str, Path], str]:
        # Convert the files to a dictionary
        return {file_path: self[file_path] for file_path in self}  # Create a dictionary of file paths and contents

    def to_json(self) -> str:
        # Convert the files to a JSON string
        return json.dumps(self.to_dict())  # Convert the dictionary to JSON

    def log(self, key: Union[str, Path], val: str) -> None:
        # Log a message to a file
        if str(key).startswith("../"):
            raise ValueError(f"File name {key} attempted to access parent path.")  # Prevent accessing parent paths

        if not isinstance(val, str):
            raise TypeError("val must be str")  # Ensure the value is a string

        full_path = self.path / "logs" / key  # Determine the full path for the log file
        full_path.parent.mkdir(parents=True, exist_ok=True)  # Create parent directories if needed

        # Touch if it doesnt exist
        if not full_path.exists():
            full_path.touch()  # Create the log file if it doesn't exist

        with open(full_path, "a", encoding="utf-8") as file:  # Open the log file in append mode
            file.write(f"\n{datetime.now().isoformat()}\n")  # Write the current timestamp
            file.write(val + "\n")  # Write the log message

    def archive_logs(self):
        # Archive the logs by moving them to a new directory
        if "logs" in self:
            archive_dir = (
                self.path / f"logs_{datetime.now().strftime('%Y-%m-%d-%H-%M-%S')}"  # Create a new directory for the archive
            )
            shutil.move(self.path / "logs", archive_dir)  # Move the logs to the archive directory
