"""
Tests for the revised data collection consent mechanism in the cli/learning module.
"""

from pathlib import Path
from unittest.mock import patch

import pytest

from espada.applications.cli.learning import (
    ask_collection_consent,
    check_collection_consent,
)


# Use a fixture to clean up created files after each test
@pytest.fixture
def cleanup():
    yield
    if Path(".espada_consent").exists():
        Path(".espada_consent").unlink()


"""
Test the following 4 scenarios for check_collection_consent():
    * The .espada_consent file exists and its content is "true".
    * The .espada_consent file exists but its content is not "true".
    * The .espada_consent file does not exist and the user gives consent when asked.
    * The .espada_consent file does not exist and the user does not give consent when asked.
"""


def test_check_consent_file_exists_and_true(cleanup):
    Path(".espada_consent").write_text("true")
    assert check_collection_consent() is True


def test_check_consent_file_exists_and_false(cleanup):
    Path(".espada_consent").write_text("false")
    with patch("builtins.input", side_effect=["n"]):
        assert check_collection_consent() is False


def test_check_consent_file_not_exists_and_user_says_yes(cleanup):
    with patch("builtins.input", side_effect=["y"]):
        assert check_collection_consent() is True
    assert Path(".espada_consent").exists()
    assert Path(".espada_consent").read_text() == "true"


def test_check_consent_file_not_exists_and_user_says_no(cleanup):
    with patch("builtins.input", side_effect=["n"]):
        assert check_collection_consent() is False
    assert not Path(".espada_consent").exists()


"""
Test the following 4 scenarios for ask_collection_consent():
    1. The user immediately gives consent with "y":
        * The .espada_consent file is created with content "true".
        * The function returns True.
    2. The user immediately denies consent with "n":
        * The .espada_consent file is not created.
        * The function returns False.
    3. The user first provides an invalid response, then gives consent with "y":
        * The user is re-prompted after the invalid input.
        * The .espada_consent file is created with content "true".
        * The function returns True.
    4. The user first provides an invalid response, then denies consent with "n":
        * The user is re-prompted after the invalid input.
        * The .espada_consent file is not created.
        * The function returns False.
"""


def test_ask_collection_consent_yes(cleanup):
    with patch("builtins.input", side_effect=["y"]):
        result = ask_collection_consent()
    assert Path(".espada_consent").exists()
    assert Path(".espada_consent").read_text() == "true"
    assert result is True


def test_ask_collection_consent_no(cleanup):
    with patch("builtins.input", side_effect=["n"]):
        result = ask_collection_consent()
    assert not Path(".espada_consent").exists()
    assert result is False


def test_ask_collection_consent_invalid_then_yes(cleanup):
    with patch("builtins.input", side_effect=["invalid", "y"]):
        result = ask_collection_consent()
    assert Path(".espada_consent").exists()
    assert Path(".espada_consent").read_text() == "true"
    assert result is True


def test_ask_collection_consent_invalid_then_no(cleanup):
    with patch("builtins.input", side_effect=["invalid", "n"]):
        result = ask_collection_consent()
    assert not Path(".espada_consent").exists()
    assert result is False
