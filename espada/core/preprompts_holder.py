
from pathlib import Path    # Import Path from pathlib to handle file system paths
from typing import Dict    # Import Dict from typing to specify dictionary types
from espada.core.default.disk_memory import DiskMemory    # Import DiskMemory from espada.core.default.disk_memory to handle disk memory operations


class PrepromptsHolder:
    # Initialize the PrepromptsHolder with the path to the preprompts
    def __init__(self, preprompts_path: Path):
        self.preprompts_path = preprompts_path

    # Retrieve all preprompts from the disk memory and return them as a dictionary
    def get_preprompts(self) -> Dict[str, str]:
        preprompts_repo = DiskMemory(self.preprompts_path)
        return {file_name: preprompts_repo[file_name] for file_name in preprompts_repo}
