import tempfile  # Importing tempfile for creating temporary directories

from pathlib import Path  # Importing Path for file path manipulations
from typing import Union  # Importing Union for type hinting

from espada.core.files_dict import FilesDict  # Importing FilesDict for file dictionary operations
from espada.core.linting import Linting  # Importing Linting for code linting operations


class FileStore:
    # Class to handle file storage operations

    def __init__(self, path: Union[str, Path, None] = None):
        # Initialize the FileStore with a given path or create a temporary directory
        if path is None:
            path = Path(tempfile.mkdtemp(prefix="espada-"))  # Create a temporary directory with a prefix

        self.working_dir = Path(path)  # Set the working directory
        self.working_dir.mkdir(parents=True, exist_ok=True)  # Create the directory if it doesn't exist
        self.id = self.working_dir.name.split("-")[-1]  # Extract the unique ID from the directory name

    def push(self, files: FilesDict):
        # Save files to the working directory
        for name, content in files.items():
            path = self.working_dir / name  # Determine the file path
            path.parent.mkdir(parents=True, exist_ok=True)  # Create parent directories if needed
            with open(path, "w", encoding="utf-8") as f:  # Open the file for writing
                f.write(content)  # Write the file content
        return self  # Return the FileStore instance

    def linting(self, files: FilesDict) -> FilesDict:
        # Lint the code files
        linting = Linting()  # Create a Linting instance
        return linting.lint_files(files)  # Return the linted files

    def pull(self) -> FilesDict:
        # Retrieve files from the working directory
        files = {}  # Initialize a dictionary to store file contents
        for path in self.working_dir.glob("**/*"):  # Iterate over all files in the directory
            if path.is_file():  # Check if the path is a file
                with open(path, "r") as f:  # Open the file for reading
                    try:
                        content = f.read()  # Read the file content
                    except UnicodeDecodeError:
                        content = "binary file"  # Handle binary files
                    files[str(path.relative_to(self.working_dir))] = content  # Store the content in the dictionary
        return FilesDict(files)  # Return the files as a FilesDict
