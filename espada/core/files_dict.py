from collections import OrderedDict
from pathlib import Path
from typing import Union


# class Code(MutableMapping[str | Path, str]):
# ToDo: implement as mutable mapping, potentially holding a dict instead of being a dict.
class FilesDict(dict):
    # Custom dictionary class that extends the built-in dict to handle file paths as keys
    # and file contents as values.

    def __setitem__(self, key: Union[str, Path], value: str):
        # Override the __setitem__ method to enforce key and value types.

        if not isinstance(key, (str, Path)):
            # Ensure the key is either a string or a Path object.
            raise TypeError("Keys must be strings or Path's")
        if not isinstance(value, str):
            # Ensure the value is a string.
            raise TypeError("Values must be strings")
        super().__setitem__(key, value)  # Call the parent class's __setitem__ method.

    def to_chat(self):
        # Convert the dictionary to a formatted string suitable for chat display.

        chat_str = ""
        for file_name, file_content in self.items():
            # Iterate over each file and its content in the dictionary.
            lines_dict = file_to_lines_dict(file_content)
            # Convert file content to a dictionary of line numbers and lines.
            chat_str += f"File: {file_name}\n"
            for line_number, line_content in lines_dict.items():
                # Append each line with its line number to the chat string.
                chat_str += f"{line_number} {line_content}\n"
            chat_str += "\n"
        return f"```\n{chat_str}```"  # Return the formatted string enclosed in code block markers.

    def to_log(self):
        # Convert the dictionary to a plain string suitable for logging.

        log_str = ""
        for file_name, file_content in self.items():
            # Iterate over each file and its content in the dictionary.
            log_str += f"File: {file_name}\n"
            log_str += file_content  # Append the file content directly to the log string.
            log_str += "\n"
        return log_str  # Return the plain log string.


def file_to_lines_dict(file_content: str) -> dict:
    # Helper function to convert file content into a dictionary of line numbers and lines.

    lines_dict = OrderedDict(
        {
            line_number: line_content
            for line_number, line_content in enumerate(file_content.split("\n"), 1)
            # Enumerate over each line in the file content, starting line numbers at 1.
        }
    )
    return lines_dict  # Return the ordered dictionary of lines.
