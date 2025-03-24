from platform import platform  # Import platform module to get OS information
from sys import version_info  # Import version_info from sys to get Python version information
from typing import List, Union  # Import List and Union from typing for type hinting

from langchain.schema import AIMessage, HumanMessage, SystemMessage  # Import message types from langchain.schema

from espada.core.ai import AI  # Import AI class from espada.core.ai
from espada.core.base_execution_env import BaseExecutionEnv  # Import BaseExecutionEnv class from espada.core.base_execution_env
from espada.core.base_memory import BaseMemory  # Import BaseMemory class from espada.core.base_memory
from espada.core.chat_to_files import chat_to_files_dict  # Import chat_to_files_dict function from espada.core.chat_to_files
from espada.core.default.paths import CODE_GEN_LOG_FILE, ENTRYPOINT_FILE  # Import constants from espada.core.default.paths
from espada.core.default.steps import curr_fn, improve_fn, setup_sys_prompt  # Import functions from espada.core.default.steps
from espada.core.files_dict import FilesDict  # Import FilesDict class from espada.core.files_dict
from espada.core.preprompts_holder import PrepromptsHolder  # Import PrepromptsHolder class from espada.core.preprompts_holder
from espada.core.prompt import Prompt  # Import Prompt class from espada.core.prompt

# Type hint for chat messages
Message = Union[AIMessage, HumanMessage, SystemMessage]
MAX_SELF_HEAL_ATTEMPTS = 10


def get_platform_info() -> str:

    v = version_info
    a = f"Python Version: {v.major}.{v.minor}.{v.micro}"
    b = f"\nOS: {platform()}\n"
    return a + b


def self_heal(
    ai: AI,
    execution_env: BaseExecutionEnv,
    files_dict: FilesDict,
    prompt: Prompt = None,
    preprompts_holder: PrepromptsHolder = None,
    memory: BaseMemory = None,
    diff_timeout=3,
) -> FilesDict:

    # step 1. execute the entrypoint
    # log_path = dbs.workspace.path / "log.txt"
    if ENTRYPOINT_FILE not in files_dict:
        raise FileNotFoundError(
            "The required entrypoint "
            + ENTRYPOINT_FILE
            + " does not exist in the code."
        )

    attempts = 0
    if preprompts_holder is None:
        raise AssertionError("Prepromptsholder required for self-heal")
    while attempts < MAX_SELF_HEAL_ATTEMPTS:
        attempts += 1
        timed_out = False

        # Start the process
        execution_env.upload(files_dict)
        p = execution_env.popen(files_dict[ENTRYPOINT_FILE])

        # Wait for the process to complete and get output
        stdout_full, stderr_full = p.communicate()

        if (p.returncode != 0 and p.returncode != 2) and not timed_out:
            print("run.sh failed.  The log is:")
            print(stdout_full.decode("utf-8"))
            print(stderr_full.decode("utf-8"))

            new_prompt = Prompt(
                f"A program with this specification was requested:\n{prompt}\n, but running it produced the following output:\n{stdout_full}\n and the following errors:\n{stderr_full}. Please change it so that it fulfills the requirements."
            )
            files_dict = improve_fn(
                ai, new_prompt, files_dict, memory, preprompts_holder, diff_timeout
            )
        else:
            break
    return files_dict


def clarified_gen(
    ai: AI, prompt: Prompt, memory: BaseMemory, preprompts_holder: PrepromptsHolder
) -> FilesDict:

    preprompts = preprompts_holder.get_preprompts()
    messages: List[Message] = [SystemMessage(content=preprompts["clarify"])]
    user_input = prompt.text  # clarify does not work with vision right now
    while True:
        messages = ai.next(messages, user_input, step_name=curr_fn())
        msg = messages[-1].content.strip()

        if "nothing to clarify" in msg.lower():
            break

        if msg.lower().startswith("no"):
            print("Nothing to clarify.")
            break

        print('(answer in text, or "c" to move on)\n')
        user_input = input("")
        print()

        if not user_input or user_input == "c":
            print("(letting espada make its own assumptions)")
            print()
            messages = ai.next(
                messages,
                "Make your own assumptions and state them explicitly before starting",
                step_name=curr_fn(),
            )
            print()

        user_input += """
            \n\n
            Is anything else unclear? If yes, ask another question.\n
            Otherwise state: "Nothing to clarify"
            """

    print()

    messages = [
        SystemMessage(content=setup_sys_prompt(preprompts)),
    ] + messages[
        1:
    ]  # skip the first clarify message, which was the original clarify priming prompt
    messages = ai.next(
        messages,
        preprompts["generate"].replace("FILE_FORMAT", preprompts["file_format"]),
        step_name=curr_fn(),
    )
    print()
    chat = messages[-1].content.strip()
    memory.log(CODE_GEN_LOG_FILE, "\n\n".join(x.pretty_repr() for x in messages))
    files_dict = chat_to_files_dict(chat)
    return files_dict


def lite_gen(
    ai: AI, prompt: Prompt, memory: BaseMemory, preprompts_holder: PrepromptsHolder
) -> FilesDict:

    preprompts = preprompts_holder.get_preprompts()
    messages = ai.start(
        prompt.to_langchain_content(), preprompts["file_format"], step_name=curr_fn()
    )
    chat = messages[-1].content.strip()
    memory.log(CODE_GEN_LOG_FILE, "\n\n".join(x.pretty_repr() for x in messages))
    files_dict = chat_to_files_dict(chat)
    return files_dict
