import tempfile

import pytest

from langchain.schema import AIMessage

from espada.core.default.disk_execution_env import DiskExecutionEnv
from espada.core.default.paths import ENTRYPOINT_FILE
from espada.core.default.simple_agent import SimpleAgent
from espada.core.files_dict import FilesDict
from espada.core.prompt import Prompt
from tests.mock_ai import MockAI


def test_init():
    temp_dir = tempfile.mkdtemp()
    mock_ai = MockAI(
        [
            AIMessage(
                "hello_world.py\n```\nwith open('output.txt', 'w') as file:\n    file.write('Hello World!')\n```"
            ),
            AIMessage("```run.sh\npython3 hello_world.py\n```"),
        ],
    )
    lean_agent = SimpleAgent.with_default_config(temp_dir, mock_ai)
    outfile = "output.txt"
    code = lean_agent.init(
        Prompt(
            f"Make a program that prints 'Hello World!' to a file called '{outfile}'"
        )
    )

    env = DiskExecutionEnv()
    env.upload(code).run(f"bash {ENTRYPOINT_FILE}")
    code = env.download()

    assert any(outfile in content for content in code.values())
    assert code[outfile] == "Hello World!"


def test_improve():
    temp_dir = tempfile.mkdtemp()
    code = FilesDict(
        {
            "main.py": "def write_hello_world_to_file(filename):\n    \"\"\"\n    Writes 'Hello World!' to the specified file.\n    \n    :param filename: The name of the file to write to.\n    \"\"\"\n    with open(filename, 'w') as file:\n        file.write('Hello World!')\n\nif __name__ == \"__main__\":\n    output_filename = 'output.txt'\n    write_hello_world_to_file(output_filename)",
            "requirements.txt": "# No dependencies required",
            "run.sh": "python3 main.py\n",
        }
    )
    mock_ai = MockAI(
        [
            AIMessage(
                "```diff\n--- main.py\n+++ main.py\n@@ -7,3 +7,3 @@\n     with open(filename, 'w') as file:\n-        file.write('Hello World!')\n+        file.write('!dlroW olleH')\n```"
            )
        ]
    )
    lean_agent = SimpleAgent.with_default_config(temp_dir, mock_ai)
    code = lean_agent.improve(
        code,
        Prompt(
            "Change the program so that it prints '!dlroW olleH' instead of 'Hello World!' "
        ),
        f"bash {ENTRYPOINT_FILE}",
    )

    env = DiskExecutionEnv()
    env.upload(code).run(f"bash {ENTRYPOINT_FILE}")
    code = env.download()

    outfile = "output.txt"
    assert any(outfile in content for content in code.values())
    assert code[outfile] == "!dlroW olleH"


if __name__ == "__main__":
    pytest.main()
