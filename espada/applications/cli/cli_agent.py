from typing import Callable, Optional, TypeVar  # Import required type hints

# from espada.core.default.git_version_manager import GitVersionManager  # Commented out import
from espada.core.ai import AI  # Import AI class for model interactions
from espada.core.base_agent import BaseAgent  # Import base agent class
from espada.core.base_execution_env import BaseExecutionEnv  # Import execution environment base
from espada.core.base_memory import BaseMemory  # Import memory management base
from espada.core.default.disk_execution_env import DiskExecutionEnv  # Import disk execution environment
from espada.core.default.disk_memory import DiskMemory  # Import disk memory implementation
from espada.core.default.paths import PREPROMPTS_PATH  # Import path constants
from espada.core.default.steps import (  # Import step functions
    execute_entrypoint,
    gen_code,
    gen_entrypoint,
    improve_fn,
)
from espada.core.files_dict import FilesDict  # Import file dictionary class
from espada.core.preprompts_holder import PrepromptsHolder  # Import preprompts manager
from espada.core.prompt import Prompt  # Import prompt class

CodeGenType = TypeVar("CodeGenType", bound=Callable[[AI, str, BaseMemory], FilesDict])  # Type for code generation functions
CodeProcessor = TypeVar(  # Type for code processing functions
    "CodeProcessor", bound=Callable[[AI, BaseExecutionEnv, FilesDict], FilesDict]
)
ImproveType = TypeVar(  # Type for code improvement functions
    "ImproveType", bound=Callable[[AI, str, FilesDict, BaseMemory], FilesDict]
)


class CliAgent(BaseAgent):  # Define CliAgent class inheriting from BaseAgent

    def __init__(  # Initialize the CliAgent with required components
        self,
        memory: BaseMemory,  # Memory system for storing information
        execution_env: BaseExecutionEnv,  # Environment for code execution
        ai: AI = None,  # AI model instance
        code_gen_fn: CodeGenType = gen_code,  # Code generation function
        improve_fn: ImproveType = improve_fn,  # Code improvement function
        process_code_fn: CodeProcessor = execute_entrypoint,  # Code processing function
        preprompts_holder: PrepromptsHolder = None,  # Preprompts manager
    ):
        self.memory = memory  # Store memory instance
        self.execution_env = execution_env  # Store execution environment
        self.ai = ai or AI()  # Create AI instance if not provided
        self.code_gen_fn = code_gen_fn  # Store code generation function
        self.process_code_fn = process_code_fn  # Store code processing function
        self.improve_fn = improve_fn  # Store code improvement function
        self.preprompts_holder = preprompts_holder or PrepromptsHolder(PREPROMPTS_PATH)  # Store preprompts manager

    @classmethod  # Class method for creating CliAgent with default configuration
    def with_default_config(
        cls,
        memory: DiskMemory,  # Disk-based memory system
        execution_env: DiskExecutionEnv,  # Disk-based execution environment
        ai: AI = None,  # AI model instance
        code_gen_fn: CodeGenType = gen_code,  # Code generation function
        improve_fn: ImproveType = improve_fn,  # Code improvement function
        process_code_fn: CodeProcessor = execute_entrypoint,  # Code processing function
        preprompts_holder: PrepromptsHolder = None,  # Preprompts manager
        diff_timeout=3,  # Timeout for diff operations
    ):

        return cls(  # Create and return new CliAgent instance
            memory=memory,  # Set memory system
            execution_env=execution_env,  # Set execution environment
            ai=ai,  # Set AI model
            code_gen_fn=code_gen_fn,  # Set code generation function
            process_code_fn=process_code_fn,  # Set code processing function
            improve_fn=improve_fn,  # Set code improvement function
            preprompts_holder=preprompts_holder or PrepromptsHolder(PREPROMPTS_PATH),  # Set preprompts manager
        )

    def init(self, prompt: Prompt) -> FilesDict:  # Initialize code generation


        files_dict = self.code_gen_fn(  # Generate code using provided function
            self.ai, prompt, self.memory, self.preprompts_holder
        )
        entrypoint = gen_entrypoint(  # Generate entrypoint file
            self.ai, prompt, files_dict, self.memory, self.preprompts_holder
        )
        combined_dict = {**files_dict, **entrypoint}  # Combine generated files
        files_dict = FilesDict(combined_dict)  # Create new FilesDict
        files_dict = self.process_code_fn(  # Process the generated code
            self.ai,
            self.execution_env,
            files_dict,
            preprompts_holder=self.preprompts_holder,
            prompt=prompt,
            memory=self.memory,
        )
        return files_dict  # Return processed files

    def improve(  # Improve existing code
        self,
        files_dict: FilesDict,  # Files to improve
        prompt: Prompt,  # Improvement instructions
        execution_command: Optional[str] = None,  # Optional execution command
        diff_timeout=3,  # Timeout for diff operations
    ) -> FilesDict:  # Return improved files

        files_dict = self.improve_fn(  # Improve code using provided function
            self.ai,
            prompt,
            files_dict,
            self.memory,
            self.preprompts_holder,
            diff_timeout=diff_timeout,
        )
        # entrypoint = gen_entrypoint(  # Commented out entrypoint generation
        #     self.ai, prompt, files_dict, self.memory, self.preprompts_holder
        # )
        # combined_dict = {**files_dict, **entrypoint}  # Commented out file combination
        # files_dict = FilesDict(combined_dict)  # Commented out FilesDict creation
        # files_dict = self.process_code_fn(  # Commented out code processing
        #     self.ai,
        #     self.execution_env,
        #     files_dict,
        #     preprompts_holder=self.preprompts_holder,
        #     prompt=prompt,
        #     memory=self.memory,
        # )

        return files_dict  # Return improved files
