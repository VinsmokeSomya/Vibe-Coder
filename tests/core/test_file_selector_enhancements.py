import os
import toml

from pathlib import Path
from typing import List, Union

from espada.applications.cli.file_selector import FileSelector

editorcalled = False


def set_editor_called(
    self, input_path: Union[str, Path], init: bool = True
) -> List[str]:
    global editorcalled
    editorcalled = True
    return []


def set_file_selector_tmpproject(tmp_path):
    project_path = tmp_path / "project/"
    os.mkdir(project_path)
    os.mkdir(project_path / "x")
    os.mkdir(project_path / "a")

    gpteng_path = project_path / ".gpteng"
    os.mkdir(gpteng_path)

    with open(gpteng_path / "file_selection.toml", "w") as file:
        file.write("[files]\n")
        file.write(' "x/xxtest.py" = "selected"\n')
        file.write(' "a/aatest.py" = "selected"\n')

    with open(project_path / "x/xxtest.py", "w") as file:
        file.write('print("Hello")')

    with open(project_path / "a/aatest.py", "w") as file:
        file.write('print("Hello")')

    return project_path


def test_file_selector_enhancement_skip_file_selector(tmp_path):
    project_path = set_file_selector_tmpproject(tmp_path)
    fileSelector = FileSelector(project_path=project_path)
    fileSelector.editor_file_selector = set_editor_called
    file_list = {
        "a/aatest.py": True,
        "x/xxtest.py": True
    }
    fileSelector.metadata_db[fileSelector.FILE_LIST_NAME] = toml.dumps({"files": file_list})
    fileSelector.ask_for_files(skip_file_selection=True)

    assert editorcalled is False, "FileSelector.skip_file_selector is not working"


def test_file_selector_enhancement_sort(tmp_path):
    project_path = set_file_selector_tmpproject(tmp_path)
    fileSelector = FileSelector(project_path=project_path)

    sortedFiles = fileSelector.get_current_files(project_path)
    assert [os.path.normpath(f) for f in sortedFiles] == [
        os.path.normpath("a/aatest.py"),
        os.path.normpath("x/xxtest.py"),
    ], "FileSelector.get_current_files is unsorted!"
