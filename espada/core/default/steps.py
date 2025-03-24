# Importing necessary modules for inspection, input/output operations, regular expressions, system-specific parameters, and traceback handling
import inspect
import io
import re
import sys
import traceback

# Importing Path for file path manipulations and type hints for type checking
from pathlib import Path
from typing import List, MutableMapping, Union

# Importing message types from langchain schema
from langchain.schema import HumanMessage, SystemMessage
# Importing colored for terminal text coloring
from termcolor import colored

# Importing AI class for AI operations
from espada.core.ai import AI
# Importing BaseExecutionEnv for execution environment operations
from espada.core.base_execution_env import BaseExecutionEnv
# Importing BaseMemory for memory operations
from espada.core.base_memory import BaseMemory
# Importing functions for handling chat to file operations
from espada.core.chat_to_files import apply_diffs, chat_to_files_dict, parse_diffs
# Importing constants for default settings
from espada.core.default.constants import MAX_EDIT_REFINEMENT_STEPS
# Importing paths for various log and configuration files
from espada.core.default.paths import (
    CODE_GEN_LOG_FILE,
    DEBUG_LOG_FILE,
    DIFF_LOG_FILE,
    ENTRYPOINT_FILE,
    ENTRYPOINT_LOG_FILE,
    IMPROVE_LOG_FILE,
    PREPROMPTS_PATH,
    STEPS_FILE,
    WORKSPACE_PATH,
    memory_path,
)
# Importing FilesDict for file dictionary operations and file_to_lines_dict for file line operations
from espada.core.files_dict import FilesDict, file_to_lines_dict
# Importing PrepromptsHolder for handling preprompts
from espada.core.preprompts_holder import PrepromptsHolder
# Importing Prompt for prompt operations
from espada.core.prompt import Prompt


def curr_fn() -> str:

    return inspect.stack()[1].function


def setup_sys_prompt(preprompts: MutableMapping[Union[str, Path], str]) -> str:

    return (
        preprompts["roadmap"]
        + preprompts["generate"].replace("FILE_FORMAT", preprompts["file_format"])
        + "\nUseful to know:\n"
        + preprompts["philosophy"]
    )


def setup_sys_prompt_existing_code(
    preprompts: MutableMapping[Union[str, Path], str]
) -> str:

    return (
        preprompts["roadmap"]
        + preprompts["improve"].replace("FILE_FORMAT", preprompts["file_format_diff"])
        + "\nUseful to know:\n"
        + preprompts["philosophy"]
    )


def gen_code(
    ai: AI, prompt: Prompt, memory: BaseMemory, preprompts_holder: PrepromptsHolder
) -> FilesDict:

    preprompts = preprompts_holder.get_preprompts()
    messages = ai.start(
        setup_sys_prompt(preprompts), prompt.to_langchain_content(), step_name=curr_fn()
    )
    chat = messages[-1].content.strip()
    memory.log(CODE_GEN_LOG_FILE, "\n\n".join(x.pretty_repr() for x in messages))
    files_dict = chat_to_files_dict(chat)
    return files_dict


def gen_entrypoint(
    ai: AI,
    prompt: Prompt,
    files_dict: FilesDict,
    memory: BaseMemory,
    preprompts_holder: PrepromptsHolder,
) -> FilesDict:

    user_prompt = prompt.entrypoint_prompt
    if not user_prompt:
        user_prompt = """
        Make a unix script that
        a) installs dependencies
        b) runs all necessary parts of the codebase (in parallel if necessary)
        """
    preprompts = preprompts_holder.get_preprompts()
    messages = ai.start(
        system=(preprompts["entrypoint"]),
        user=user_prompt
        + "\nInformation about the codebase:\n\n"
        + files_dict.to_chat(),
        step_name=curr_fn(),
    )
    print()
    chat = messages[-1].content.strip()
    regex = r"```\S*\n(.+?)```"
    matches = re.finditer(regex, chat, re.DOTALL)
    entrypoint_code = FilesDict(
        {ENTRYPOINT_FILE: "\n".join(match.group(1) for match in matches)}
    )
    memory.log(ENTRYPOINT_LOG_FILE, "\n\n".join(x.pretty_repr() for x in messages))
    return entrypoint_code


def execute_entrypoint(
    ai: AI,
    execution_env: BaseExecutionEnv,
    files_dict: FilesDict,
    prompt: Prompt = None,
    preprompts_holder: PrepromptsHolder = None,
    memory: BaseMemory = None,
) -> FilesDict:

    if ENTRYPOINT_FILE not in files_dict:
        raise FileNotFoundError(
            "The required entrypoint "
            + ENTRYPOINT_FILE
            + " does not exist in the code."
        )

    command = files_dict[ENTRYPOINT_FILE]

    print()
    print(
        colored(
            "Do you want to execute this code? (Y/n)",
            "red",
        )
    )
    print()
    print(command)
    print()
    if input("").lower() not in ["", "y", "yes"]:
        print("Ok, not executing the code.")
        return files_dict
    print("Executing the code...")
    print()
    print(
        colored(
            "Note: If it does not work as expected, consider running the code"
            + " in another way than above.",
            "green",
        )
    )
    print()
    print("You can press ctrl+c *once* to stop the execution.")
    print()

    execution_env.upload(files_dict).run(f"bash {ENTRYPOINT_FILE}")
    return files_dict


def improve_fn(
    ai: AI,
    prompt: Prompt,
    files_dict: FilesDict,
    memory: BaseMemory,
    preprompts_holder: PrepromptsHolder,
    diff_timeout=3,
) -> FilesDict:

    preprompts = preprompts_holder.get_preprompts()
    messages = [
        SystemMessage(content=setup_sys_prompt_existing_code(preprompts)),
    ]

    # Add files as input
    messages.append(HumanMessage(content=f"{files_dict.to_chat()}"))
    messages.append(HumanMessage(content=prompt.to_langchain_content()))
    memory.log(
        DEBUG_LOG_FILE,
        "UPLOADED FILES:\n" + files_dict.to_log() + "\nPROMPT:\n" + prompt.text,
    )
    return _improve_loop(ai, files_dict, memory, messages, diff_timeout=diff_timeout)


def _improve_loop(
    ai: AI, files_dict: FilesDict, memory: BaseMemory, messages: List, diff_timeout=3
) -> FilesDict:
    messages = ai.next(messages, step_name=curr_fn())
    files_dict, errors = salvage_correct_hunks(
        messages, files_dict, memory, diff_timeout=diff_timeout
    )

    retries = 0
    while errors and retries < MAX_EDIT_REFINEMENT_STEPS:
        messages.append(
            HumanMessage(
                content="Some previously produced diffs were not on the requested format, or the code part was not found in the code. Details:\n"
                + "\n".join(errors)
                + "\n Only rewrite the problematic diffs, making sure that the failing ones are now on the correct format and can be found in the code. Make sure to not repeat past mistakes. \n"
            )
        )
        messages = ai.next(messages, step_name=curr_fn())
        files_dict, errors = salvage_correct_hunks(
            messages, files_dict, memory, diff_timeout
        )
        retries += 1

    return files_dict


def salvage_correct_hunks(
    messages: List, files_dict: FilesDict, memory: BaseMemory, diff_timeout=3
) -> tuple[FilesDict, List[str]]:
    error_messages = []
    ai_response = messages[-1].content.strip()

    diffs = parse_diffs(ai_response, diff_timeout=diff_timeout)
    # validate and correct diffs

    for _, diff in diffs.items():
        # if diff is a new file, validation and correction is unnecessary
        if not diff.is_new_file():
            problems = diff.validate_and_correct(
                file_to_lines_dict(files_dict[diff.filename_pre])
            )
            error_messages.extend(problems)
    files_dict = apply_diffs(diffs, files_dict)
    memory.log(IMPROVE_LOG_FILE, "\n\n".join(x.pretty_repr() for x in messages))
    memory.log(DIFF_LOG_FILE, "\n\n".join(error_messages))
    return files_dict, error_messages


class Tee(object):
    def __init__(self, *files):
        self.files = files

    def write(self, obj):
        for file in self.files:
            file.write(obj)

    def flush(self):
        for file in self.files:
            file.flush()


def handle_improve_mode(prompt, agent, memory, files_dict, diff_timeout=3):
    captured_output = io.StringIO()
    old_stdout = sys.stdout
    sys.stdout = Tee(sys.stdout, captured_output)

    try:
        files_dict = agent.improve(files_dict, prompt, diff_timeout=diff_timeout)
    except Exception as e:
        print(
            f"Error while improving the project: {e}\nCould you please upload the debug_log_file.txt in {memory.path}/logs folder to github?\nFULL STACK TRACE:\n"
        )
        traceback.print_exc(file=sys.stdout)  # Print the full stack trace
    finally:
        # Reset stdout
        sys.stdout = old_stdout

        # Get the captured output
        captured_string = captured_output.getvalue()
        print(captured_string)
        memory.log(DEBUG_LOG_FILE, "\nCONSOLE OUTPUT:\n" + captured_string)

    return files_dict
