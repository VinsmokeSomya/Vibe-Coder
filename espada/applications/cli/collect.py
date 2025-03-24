from typing import Tuple

from espada.applications.cli.learning import (
    Learning,
    Review,
    extract_learning,
    human_review_input,
)
from espada.core.default.disk_memory import DiskMemory
from espada.core.prompt import Prompt


def send_learning(learning: Learning):
    # Analytics configuration and sending (commented out)
    # import rudderstack.analytics as rudder_analytics

    # rudder_analytics.write_key = "YOUR_WRITE_KEY_HERE"    # Add your RudderStack write key here
    # rudder_analytics.dataPlaneUrl = "YOUR_DATA_PLANE_URL_HERE" # Add your RudderStack data plane URL here
    
    # rudder_analytics.track(
    #     user_id=learning.session,
    #     event="learning",
    #     properties=learning.to_dict(),  # type: ignore
    # )
    pass


def collect_learnings(
    prompt: Prompt,
    model: str,
    temperature: float,
    config: any,
    memory: DiskMemory,
    review: Review,
):
    # Analytics collection (commented out)
    # learnings = extract_learning(prompt, model, temperature, config, memory, review)
    # try:
    #     send_learning(learnings)
    # except RuntimeError:
    #     # try to remove some parts of learning that might be too big
    #     # rudderstack max event size is 32kb
    #     max_size = 32 << 10  # 32KB in bytes
    #     current_size = len(learnings.to_json().encode("utf-8"))  # get size in bytes
    #
    #     overflow = current_size - max_size
    #
    #     # Add some extra characters for the "[REMOVED...]" string and for safety margin
    #     remove_length = overflow + len(f"[REMOVED {overflow} CHARACTERS]") + 100
    #
    #     learnings.logs = (
    #         learnings.logs[:-remove_length]
    #         + f"\n\n[REMOVED {remove_length} CHARACTERS]"
    #     )
    #
    #     print(
    #         "WARNING: learning too big, removing some parts. "
    #         "Please report if this results in a crash."
    #     )
    #     try:
    #         send_learning(learnings)
    #     except RuntimeError:
    #         print(
    #             "Sending learnings crashed despite truncation. Progressing without saving learnings."
    #         )
    pass


# def steps_file_hash():
#     """
#     Compute the SHA-256 hash of the steps file.
#
#     Returns
#     -------
#     str
#         The SHA-256 hash of the steps file.
#     """
#     with open(steps.__file__, "r") as f:
#         content = f.read()
#         return hashlib.sha256(content.encode("utf-8")).hexdigest()


def collect_and_send_human_review(
    prompt: Prompt,
    model: str,
    temperature: float,
    config: Tuple[str, ...],
    memory: DiskMemory,
):
    # Analytics review collection (commented out)
    # review = human_review_input()
    # if review:
    #     collect_learnings(prompt, model, temperature, config, memory, review)
    pass
