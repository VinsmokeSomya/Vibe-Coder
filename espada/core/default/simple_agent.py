import tempfile  # Importing tempfile for creating temporary files

from typing import Optional  # Importing Optional for type hinting

from espada.core.ai import AI  # Importing AI class for AI operations
from espada.core.base_agent import BaseAgent  # Importing BaseAgent as a base class for agents
from espada.core.base_execution_env import BaseExecutionEnv  # Importing BaseExecutionEnv for execution environment operations
from espada.core.base_memory import BaseMemory  # Importing BaseMemory for memory operations
from espada.core.default.disk_execution_env import DiskExecutionEnv  # Importing DiskExecutionEnv for disk-based execution environment
from espada.core.default.disk_memory import DiskMemory  # Importing DiskMemory for disk-based memory operations
from espada.core.default.paths import PREPROMPTS_PATH, memory_path  # Importing paths for preprompts and memory
from espada.core.default.steps import gen_code, gen_entrypoint, improve_fn  # Importing functions for generating code, entrypoint, and improving functions
from espada.core.files_dict import FilesDict  # Importing FilesDict for file dictionary operations
from espada.core.preprompts_holder import PrepromptsHolder  # Importing PrepromptsHolder for handling preprompts
from espada.core.prompt import Prompt  # Importing Prompt for prompt operations


# SimpleAgent class inherits from BaseAgent and provides implementations for initializing and improving code.
class SimpleAgent(BaseAgent):

    def __init__(
        self,
        memory: BaseMemory,
        execution_env: BaseExecutionEnv,
        ai: AI = None,
        preprompts_holder: PrepromptsHolder = None,
    ):
        # Initialize the preprompts holder, memory, execution environment, and AI model.
        self.preprompts_holder = preprompts_holder or PrepromptsHolder(PREPROMPTS_PATH)
        self.memory = memory
        self.execution_env = execution_env
        self.ai = ai or AI()

    @classmethod
    def with_default_config(
        cls, path: str, ai: AI = None, preprompts_holder: PrepromptsHolder = None
    ):
        # Create a SimpleAgent instance with default configuration using disk-based memory and execution environment.
        return cls(
            memory=DiskMemory(memory_path(path)),
            execution_env=DiskExecutionEnv(),
            ai=ai,
            preprompts_holder=preprompts_holder or PrepromptsHolder(PREPROMPTS_PATH),
        )

    def init(self, prompt: Prompt) -> FilesDict:
        # Generate initial code files based on the provided prompt.
        files_dict = gen_code(self.ai, prompt, self.memory, self.preprompts_holder)
        # Generate an entrypoint script for the codebase.
        entrypoint = gen_entrypoint(
            self.ai, prompt, files_dict, self.memory, self.preprompts_holder
        )
        # Combine the generated code files and entrypoint into a single FilesDict.
        combined_dict = {**files_dict, **entrypoint}
        files_dict = FilesDict(combined_dict)
        return files_dict

    def improve(
        self,
        files_dict: FilesDict,
        prompt: Prompt,
        execution_command: Optional[str] = None,
    ) -> FilesDict:
        # Improve the existing code files based on the provided prompt.
        files_dict = improve_fn(
            self.ai, prompt, files_dict, self.memory, self.preprompts_holder
        )
        return files_dict

# Function to create a SimpleAgent with a default configuration using a temporary directory.
def default_config_agent():
    return SimpleAgent.with_default_config(tempfile.mkdtemp())
