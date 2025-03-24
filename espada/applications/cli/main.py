import difflib  # Import for generating diffs between files
import json  # Import for JSON handling
import logging  # Import for logging functionality
import os  # Import for operating system operations
import platform  # Import for system information
import subprocess  # Import for running subprocesses
import sys  # Import for system-specific parameters

from pathlib import Path  # Import for path manipulation

import openai  # Import OpenAI API client
import typer  # Import CLI framework

from dotenv import load_dotenv  # Import for loading environment variables
from langchain.globals import set_llm_cache  # Import for LLM caching
from langchain_community.cache import SQLiteCache  # Import for SQLite cache implementation
from termcolor import colored  # Import for colored terminal output

from espada.applications.cli.cli_agent import CliAgent  # Import CLI agent
from espada.applications.cli.collect import collect_and_send_human_review  # Import feedback collection
from espada.applications.cli.file_selector import FileSelector  # Import file selection
from espada.core.ai import AI, ClipboardAI  # Import AI implementations
from espada.core.default.disk_execution_env import DiskExecutionEnv  # Import disk execution environment
from espada.core.default.disk_memory import DiskMemory  # Import disk memory
from espada.core.default.file_store import FileStore  # Import file storage
from espada.core.default.paths import PREPROMPTS_PATH, memory_path  # Import path constants
from espada.core.default.steps import (  # Import step functions
    execute_entrypoint,
    gen_code,
    handle_improve_mode,
    improve_fn as improve_fn,
)
from espada.core.files_dict import FilesDict  # Import file dictionary
from espada.core.git import stage_uncommitted_to_git  # Import git operations
from espada.core.preprompts_holder import PrepromptsHolder  # Import preprompts manager
from espada.core.prompt import Prompt  # Import prompt class
from espada.tools.custom_steps import clarified_gen, lite_gen, self_heal  # Import custom steps

app = typer.Typer(  # Create CLI application
    context_settings={"help_option_names": ["-h", "--help"]}
)


def load_env_if_needed():  # Load environment variables if needed

    # We have all these checks for legacy reasons...
    if os.getenv("OPENAI_API_KEY") is None:  # Check if API key is set
        load_dotenv()  # Load from default location
    if os.getenv("OPENAI_API_KEY") is None:  # Check again
        load_dotenv(dotenv_path=os.path.join(os.getcwd(), ".env"))  # Load from current directory

    openai.api_key = os.getenv("OPENAI_API_KEY")  # Set API key

    if os.getenv("ANTHROPIC_API_KEY") is None:  # Check for Anthropic API key
        load_dotenv()  # Load from default location
    if os.getenv("ANTHROPIC_API_KEY") is None:  # Check again
        load_dotenv(dotenv_path=os.path.join(os.getcwd(), ".env"))  # Load from current directory


def concatenate_paths(base_path, sub_path):  # Concatenate paths safely
    # Compute the relative path from base_path to sub_path
    relative_path = os.path.relpath(sub_path, base_path)  # Get relative path

    # If the relative path is not in the parent directory, use the original sub_path
    if not relative_path.startswith(".."):  # Check if path is not going up
        return sub_path  # Return original path

    # Otherwise, concatenate base_path and sub_path
    return os.path.normpath(os.path.join(base_path, sub_path))  # Return normalized path


def load_prompt(  # Load prompt from file or user input
    input_repo: DiskMemory,  # Memory repository
    improve_mode: bool,  # Whether in improve mode
    prompt_file: str,  # Path to prompt file
    image_directory: str,  # Directory containing images
    entrypoint_prompt_file: str = "",  # Path to entrypoint prompt file
) -> Prompt:  # Return Prompt object

    if os.path.isdir(prompt_file):  # Check if path is directory
        raise ValueError(  # Raise error if path is directory
            f"The path to the prompt, {prompt_file}, already exists as a directory. No prompt can be read from it. Please specify a prompt file using --prompt_file"
        )
    prompt_str = input_repo.get(prompt_file)  # Get prompt from file
    if prompt_str:  # If prompt exists
        print(colored("Using prompt from file:", "green"), prompt_file)  # Print file path
        print(prompt_str)  # Print prompt
    else:  # If no prompt file
        if not improve_mode:  # If not in improve mode
            prompt_str = input(  # Get prompt from user
                "\nWhat application do you want Espada to generate?\n"
            )
        else:  # If in improve mode
            prompt_str = input("\nHow do you want to improve the application?\n")  # Get improvement prompt

    if entrypoint_prompt_file == "":  # If no entrypoint prompt
        entrypoint_prompt = ""  # Set empty prompt
    else:  # If entrypoint prompt exists
        full_entrypoint_prompt_file = concatenate_paths(  # Get full path
            input_repo.path, entrypoint_prompt_file
        )
        if os.path.isfile(full_entrypoint_prompt_file):  # If file exists
            entrypoint_prompt = input_repo.get(full_entrypoint_prompt_file)  # Get prompt

        else:  # If file doesn't exist
            raise ValueError("The provided file at --entrypoint-prompt does not exist")  # Raise error

    if image_directory == "":  # If no image directory
        return Prompt(prompt_str, entrypoint_prompt=entrypoint_prompt)  # Return prompt without images

    full_image_directory = concatenate_paths(  # Get full image directory path
        input_repo.path, image_directory
    )
    if os.path.isdir(full_image_directory):  # If directory exists
        if len(os.listdir(full_image_directory)) == 0:  # If directory is empty
            raise ValueError("The provided --image_directory is empty.")  # Raise error
        image_repo = DiskMemory(full_image_directory)  # Create memory for images
        return Prompt(  # Return prompt with images
            prompt_str,
            image_repo.get(".").to_dict(),
            entrypoint_prompt=entrypoint_prompt,
        )
    else:  # If directory doesn't exist
        raise ValueError("The provided --image_directory is not a directory.")  # Raise error


def get_preprompts_path(use_custom_preprompts: bool, input_path: Path) -> Path:  # Get path to preprompts

    original_preprompts_path = PREPROMPTS_PATH  # Get default path
    if not use_custom_preprompts:  # If not using custom preprompts
        return original_preprompts_path  # Return default path

    custom_preprompts_path = input_path / "preprompts"  # Create custom path
    if not custom_preprompts_path.exists():  # If directory doesn't exist
        custom_preprompts_path.mkdir()  # Create directory

    for file in original_preprompts_path.glob("*"):  # Copy default preprompts
        if not (custom_preprompts_path / file.name).exists():  # If file doesn't exist
            (custom_preprompts_path / file.name).write_text(file.read_text())  # Copy file
    return custom_preprompts_path  # Return custom path


def compare(f1: FilesDict, f2: FilesDict):  # Compare two file dictionaries
    def colored_diff(s1, s2):  # Generate colored diff
        lines1 = s1.splitlines()  # Split first string into lines
        lines2 = s2.splitlines()  # Split second string into lines

        diff = difflib.unified_diff(lines1, lines2, lineterm="")  # Generate diff

        RED = "\033[38;5;202m"  # Define red color
        GREEN = "\033[92m"  # Define green color
        RESET = "\033[0m"  # Define reset color

        colored_lines = []  # Initialize colored lines list
        for line in diff:  # Process each diff line
            if line.startswith("+"):  # If line is added
                colored_lines.append(GREEN + line + RESET)  # Color green
            elif line.startswith("-"):  # If line is removed
                colored_lines.append(RED + line + RESET)  # Color red
            else:  # If line is unchanged
                colored_lines.append(line)  # Keep original

        return "\n".join(colored_lines)  # Join lines

    for file in sorted(set(f1) | set(f2)):  # Process each file
        diff = colored_diff(f1.get(file, ""), f2.get(file, ""))  # Generate diff
        if diff:  # If there are differences
            print(f"Changes to {file}:")  # Print file name
            print(diff)  # Print diff


def prompt_yesno() -> bool:  # Get yes/no input from user
    TERM_CHOICES = colored("y", "green") + "/" + colored("n", "red") + " "  # Define choices
    while True:  # Loop until valid input
        response = input(TERM_CHOICES).strip().lower()  # Get user input
        if response in ["y", "yes"]:  # If yes
            return True  # Return true
        if response in ["n", "no"]:  # If no
            break  # Break loop
        print("Please respond with 'y' or 'n'")  # Print error message


def get_system_info():  # Get system information
    system_info = {  # Create system info dictionary
        "os": platform.system(),  # Get OS name
        "os_version": platform.version(),  # Get OS version
        "architecture": platform.machine(),  # Get architecture
        "python_version": sys.version,  # Get Python version
        "packages": format_installed_packages(get_installed_packages()),  # Get installed packages
    }
    return system_info  # Return system info


def get_installed_packages():  # Get list of installed packages
    try:  # Try to get packages
        result = subprocess.run(  # Run pip list command
            [sys.executable, "-m", "pip", "list", "--format=json"],
            capture_output=True,
            text=True,
        )
        packages = json.loads(result.stdout)  # Parse JSON output
        return {pkg["name"]: pkg["version"] for pkg in packages}  # Return package dict
    except Exception as e:  # If error occurs
        return str(e)  # Return error message


def format_installed_packages(packages):  # Format package list
    return "\n".join([f"{name}: {version}" for name, version in packages.items()])  # Join package info


@app.command(  # Define CLI command
    help="""
        Espada lets you:

        \b
        - Specify a software in natural language
        - Sit back and watch as an AI writes and executes the code
        - Ask the AI to implement improvements
    """
)
def main(  # Main CLI function
    project_path: str = typer.Argument(".", help="path"),  # Project path argument
    model: str = typer.Option(  # Model option
        os.environ.get("MODEL_NAME", "gpt-4o"), "--model", "-m", help="model id string"
    ),
    temperature: float = typer.Option(  # Temperature option
        0.1,
        "--temperature",
        "-t",
        help="Controls randomness: lower values for more focused, deterministic outputs",
    ),
    improve_mode: bool = typer.Option(  # Improve mode option
        False,
        "--improve",
        "-i",
        help="Improve an existing project by modifying the files.",
    ),
    lite_mode: bool = typer.Option(  # Lite mode option
        False,
        "--lite",
        "-l",
        help="Lite mode: run a generation using only the main prompt.",
    ),
    clarify_mode: bool = typer.Option(  # Clarify mode option
        False,
        "--clarify",
        "-c",
        help="Clarify mode - discuss specification with AI before implementation.",
    ),
    self_heal_mode: bool = typer.Option(  # Self-heal mode option
        False,
        "--self-heal",
        "-sh",
        help="Self-heal mode - fix the code by itself when it fails.",
    ),
    azure_endpoint: str = typer.Option(  # Azure endpoint option
        "",
        "--azure",
        "-a",
        help="""Endpoint for your Azure OpenAI Service (https://xx.openai.azure.com).
            In that case, the given model is the deployment name chosen in the Azure AI Studio.""",
    ),
    use_custom_preprompts: bool = typer.Option(  # Custom preprompts option
        False,
        "--use-custom-preprompts",
        help="""Use your project's custom preprompts instead of the default ones.
          Copies all original preprompts to the project's workspace if they don't exist there.""",
    ),
    llm_via_clipboard: bool = typer.Option(  # Clipboard mode option
        False,
        "--llm-via-clipboard",
        help="Use the clipboard to communicate with the AI.",
    ),
    verbose: bool = typer.Option(  # Verbose mode option
        False, "--verbose", "-v", help="Enable verbose logging for debugging."
    ),
    debug: bool = typer.Option(  # Debug mode option
        False, "--debug", "-d", help="Enable debug mode for debugging."
    ),
    prompt_file: str = typer.Option(  # Prompt file option
        "prompt",
        "--prompt_file",
        help="Relative path to a text file containing a prompt.",
    ),
    entrypoint_prompt_file: str = typer.Option(  # Entrypoint prompt option
        "",
        "--entrypoint_prompt",
        help="Relative path to a text file containing a file that specifies requirements for you entrypoint.",
    ),
    image_directory: str = typer.Option(  # Image directory option
        "",
        "--image_directory",
        help="Relative path to a folder containing images.",
    ),
    use_cache: bool = typer.Option(  # Cache option
        False,
        "--use_cache",
        help="Speeds up computations and saves tokens when running the same prompt multiple times by caching the LLM response.",
    ),
    skip_file_selection: bool = typer.Option(  # Skip file selection option
        False,
        "--skip-file-selection",
        "-s",
        help="Skip interactive file selection in improve mode and use the generated TOML file directly.",
    ),
    no_execution: bool = typer.Option(  # No execution option
        False,
        "--no_execution",
        help="Run setup but to not call LLM or write any code. For testing purposes.",
    ),
    sysinfo: bool = typer.Option(  # System info option
        False,
        "--sysinfo",
        help="Output system information for debugging",
    ),
    diff_timeout: int = typer.Option(  # Diff timeout option
        3,
        "--diff_timeout",
        help="Diff regexp timeout. Default: 3. Increase if regexp search timeouts.",
    ),
):

    if debug:  # If debug mode is enabled
        import pdb  # Import debugger

        sys.excepthook = lambda *_: pdb.pm()  # Set exception hook

    if sysinfo:  # If system info is requested
        sys_info = get_system_info()  # Get system info
        for key, value in sys_info.items():  # Print each info item
            print(f"{key}: {value}")
        raise typer.Exit()  # Exit after printing

    # Validate arguments
    if improve_mode and (clarify_mode or lite_mode):  # Check incompatible modes
        typer.echo("Error: Clarify and lite mode are not compatible with improve mode.")  # Print error
        raise typer.Exit(code=1)  # Exit with error

    # Set up logging
    logging.basicConfig(level=logging.DEBUG if verbose else logging.INFO)  # Configure logging
    if use_cache:  # If caching is enabled
        set_llm_cache(SQLiteCache(database_path=".langchain.db"))  # Set up cache
    if improve_mode:  # If in improve mode
        assert not (  # Verify mode compatibility
            clarify_mode or lite_mode
        ), "Clarify and lite mode are not active for improve mode"

    load_env_if_needed()  # Load environment variables

    if llm_via_clipboard:  # If using clipboard
        ai = ClipboardAI()  # Create clipboard AI
    else:  # If using regular AI
        ai = AI(  # Create regular AI
            model_name=model,  # Set model name
            temperature=temperature,  # Set temperature
            azure_endpoint=azure_endpoint,  # Set Azure endpoint
        )

    path = Path(project_path)  # Create path object
    print("Running espada in", path.absolute(), "\n")  # Print working directory

    prompt = load_prompt(  # Load prompt
        DiskMemory(path),  # Create memory
        improve_mode,  # Pass improve mode
        prompt_file,  # Pass prompt file
        image_directory,  # Pass image directory
        entrypoint_prompt_file,  # Pass entrypoint prompt
    )

    # todo: if ai.vision is false and not llm_via_clipboard - ask if they would like to use gpt-4-vision-preview instead? If so recreate AI
    if not ai.vision:  # If vision is not available
        prompt.image_urls = None  # Clear image URLs

    # configure generation function
    if clarify_mode:  # If in clarify mode
        code_gen_fn = clarified_gen  # Use clarified generation
    elif lite_mode:  # If in lite mode
        code_gen_fn = lite_gen  # Use lite generation
    else:  # If in normal mode
        code_gen_fn = gen_code  # Use normal generation

    # configure execution function
    if self_heal_mode:  # If in self-heal mode
        execution_fn = self_heal  # Use self-heal execution
    else:  # If in normal mode
        execution_fn = execute_entrypoint  # Use normal execution

    preprompts_holder = PrepromptsHolder(  # Create preprompts holder
        get_preprompts_path(use_custom_preprompts, Path(project_path))
    )

    memory = DiskMemory(memory_path(project_path))  # Create memory
    memory.archive_logs()  # Archive logs

    execution_env = DiskExecutionEnv()  # Create execution environment
    agent = CliAgent.with_default_config(  # Create CLI agent
        memory,  # Pass memory
        execution_env,  # Pass execution environment
        ai=ai,  # Pass AI
        code_gen_fn=code_gen_fn,  # Pass code generation function
        improve_fn=improve_fn,  # Pass improvement function
        process_code_fn=execution_fn,  # Pass execution function
        preprompts_holder=preprompts_holder,  # Pass preprompts holder
    )

    files = FileStore(project_path)  # Create file store
    if not no_execution:  # If execution is enabled
        if improve_mode:  # If in improve mode
            files_dict_before, is_linting = FileSelector(project_path).ask_for_files(  # Get files to improve
                skip_file_selection=skip_file_selection
            )

            # lint the code
            if is_linting:  # If linting is enabled
                files_dict_before = files.linting(files_dict_before)  # Lint files

            files_dict = handle_improve_mode(  # Handle improvement
                prompt, agent, memory, files_dict_before, diff_timeout=diff_timeout
            )
            if not files_dict or files_dict_before == files_dict:  # If no changes
                print(  # Print error message
                    f"No changes applied. Could you please upload the debug_log_file.txt in {memory.path}/logs folder in a github issue?"
                )

            else:  # If changes were made
                print("\nChanges to be made:")  # Print changes
                compare(files_dict_before, files_dict)  # Compare files

                print()  # Print prompt
                print(colored("Do you want to apply these changes?", "light_green"))  # Ask for confirmation
                if not prompt_yesno():  # If user declines
                    files_dict = files_dict_before  # Revert changes

        else:  # If not in improve mode
            files_dict = agent.init(prompt)  # Initialize code generation
            # collect user feedback if user consents
            config = (code_gen_fn.__name__, execution_fn.__name__)  # Create config
            collect_and_send_human_review(prompt, model, temperature, config, memory)  # Collect feedback

        stage_uncommitted_to_git(path, files_dict, improve_mode)  # Stage changes to git

        files.push(files_dict)  # Push changes to file store

    if ai.token_usage_log.is_openai_model():  # If using OpenAI model
        print("Total api cost: $ ", ai.token_usage_log.usage_cost())  # Print API cost
    elif os.getenv("LOCAL_MODEL"):  # If using local model
        print("Total api cost: $ 0.0 since we are using local LLM.")  # Print zero cost
    else:  # If using other model
        print("Total tokens used: ", ai.token_usage_log.total_tokens())  # Print token usage


if __name__ == "__main__":  # If running as main
    app()  # Run CLI application
