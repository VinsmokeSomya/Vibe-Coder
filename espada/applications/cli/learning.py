import json  # Import for JSON handling
import random  # Import for generating random numbers
import tempfile  # Import for creating temporary files

from dataclasses import dataclass, field  # Import for creating data classes
from datetime import datetime  # Import for handling date and time
from pathlib import Path  # Import for path manipulation
from typing import Optional, Tuple  # Import for type hinting

from dataclasses_json import dataclass_json  # Import for JSON serialization of data classes
from termcolor import colored  # Import for colored terminal output

from espada.core.default.disk_memory import DiskMemory  # Import for disk memory operations
from espada.core.prompt import Prompt  # Import for handling prompts


@dataclass_json
@dataclass
class Review:
    # Review class to store feedback on generated code
    ran: Optional[bool]  # Whether the code ran
    perfect: Optional[bool]  # Whether the code was perfect
    works: Optional[bool]  # Whether the code was useful
    comments: str  # Additional comments
    raw: str  # Raw input data


@dataclass_json
@dataclass
class Learning:
    # Learning class to store learning session data
    prompt: str  # The prompt used for code generation
    model: str  # The model used for code generation
    temperature: float  # The temperature setting for the model
    config: str  # Configuration settings
    logs: str  # Logs of the session
    session: str  # Session identifier
    review: Optional[Review]  # Review of the session
    timestamp: str = field(default_factory=lambda: datetime.utcnow().isoformat())  # Timestamp of the session
    version: str = "0.3"  # Version of the learning data format


TERM_CHOICES = (
    colored("y", "green")
    + "/"
    + colored("n", "red")
    + "/"
    + colored("u", "yellow")
    + "(ncertain): "
)


def human_review_input() -> Optional[Review]:
    # Function to collect human review input

    print()
    if not check_collection_consent():
        return None
    print()
    print(
        colored("To help espada learn, please answer 3 questions:", "light_green")
    )
    print()

    ran = input("Did the generated code run at all? " + TERM_CHOICES)
    ran = ask_for_valid_input(ran)

    if ran == "y":
        perfect = input(
            "Did the generated code do everything you wanted? " + TERM_CHOICES
        )
        perfect = ask_for_valid_input(perfect)

        if perfect != "y":
            useful = input("Did the generated code do anything useful? " + TERM_CHOICES)
            useful = ask_for_valid_input(useful)
        else:
            useful = ""
    else:
        perfect = ""
        useful = ""

    if perfect != "y":
        comments = input(
            "If you have time, please explain what was not working "
            + colored("(ok to leave blank)\n", "light_green")
        )
    else:
        comments = ""

    return Review(
        raw=", ".join([ran, perfect, useful]),
        ran={"y": True, "n": False, "u": None, "": None}[ran],
        works={"y": True, "n": False, "u": None, "": None}[useful],
        perfect={"y": True, "n": False, "u": None, "": None}[perfect],
        comments=comments,
    )


def ask_for_valid_input(ran):
    # Function to ensure valid input from user
    while ran not in ("y", "n", "u"):
        ran = input("Invalid input. Please enter y, n, or u: ")
    return ran


def check_collection_consent() -> bool:
    # Check if user has consented to data collection

    path = Path(".espada_consent")
    if path.exists() and path.read_text() == "true":
        return True
    else:
        return ask_collection_consent()


def ask_collection_consent() -> bool:
    # Ask user for consent to collect data

    answer = input(
        "Is it ok if we store your prompts to help improve Espada? (y/n)"
    )
    while answer.lower() not in ("y", "n"):
        answer = input("Invalid input. Please enter y or n: ")

    if answer.lower() == "y":
        path = Path(".espada_consent")
        path.write_text("true")
        print(colored("Thank you️", "light_green"))
        print()
        print(
            "(If you no longer wish to participate in data collection, delete the file .espada_consent)"
        )
        return True
    else:
        print(
            colored(
                "No worries! Espada will not collect your prompts. ❤️",
                "light_green",
            )
        )
        return False


def extract_learning(
    prompt: Prompt,
    model: str,
    temperature: float,
    config: Tuple[str, ...],
    memory: DiskMemory,
    review: Review,
) -> Learning:
    # Extract learning data from session

    return Learning(
        prompt=prompt.to_json(),
        model=model,
        temperature=temperature,
        config=json.dumps(config),
        session=get_session(),
        logs=memory.to_json(),
        review=review,
    )

def get_session() -> str:
    # Get or create a session identifier

    path = Path(tempfile.gettempdir()) / "espada_user_id.txt"

    try:
        if path.exists():
            user_id = path.read_text()
        else:
            # Generate a random user ID
            user_id = str(random.randint(0, 2**32))
            path.write_text(user_id)
        return user_id
    except IOError:
        return "ephemeral_" + str(random.randint(0, 2**32))
