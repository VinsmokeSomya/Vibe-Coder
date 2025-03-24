import os  # Importing os module for interacting with the operating system

from pathlib import Path  # Importing Path from pathlib for file path manipulations


META_DATA_REL_PATH = ".espada"  # Relative path to the metadata directory
MEMORY_REL_PATH = os.path.join(META_DATA_REL_PATH, "memory")  # Relative path to the memory directory within the metadata directory
CODE_GEN_LOG_FILE = "all_output.txt"  # File name for the code generation log
IMPROVE_LOG_FILE = "improve.txt"  # File name for the improvement log
DIFF_LOG_FILE = "diff_errors.txt"  # File name for the diff errors log
DEBUG_LOG_FILE = "debug_log_file.txt"  # File name for the debug log
ENTRYPOINT_FILE = "run.sh"  # File name for the entrypoint script
ENTRYPOINT_LOG_FILE = "gen_entrypoint_chat.txt"  # File name for the entrypoint log 
PREPROMPTS_PATH = Path(__file__).parent.parent.parent / "preprompts"  # File path for the preprompts directory
STEPS_FILE = "steps.txt"  # File name for the steps file
WORKSPACE_PATH = "."  # Path to the workspace directory


def memory_path(path):
    # Function to get the full path to the memory directory
    return os.path.join(path, MEMORY_REL_PATH)

def metadata_path(path):
    # Function to get the full path to the metadata directory
    return os.path.join(path, META_DATA_REL_PATH)
