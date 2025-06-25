import pytest
import os
from unittest.mock import patch, MagicMock
from pathlib import Path
import streamlit as st

from src.agents.coder_agent import process_story_to_code

@pytest.fixture(autouse=True)
def clear_session_state():
    """Ensure Streamlit session state is clean before and after."""
    st.session_state.clear()
    yield
    st.session_state.clear()

@patch("src.agents.coder_agent.write_file")
@patch("src.agents.coder_agent.read_file")
def test_process_story_to_code_user_creation(mock_read_file, mock_write_file):
    # Arrange
    # Mock story file contents with "user creation" in summary
    story = [{
        "summary": "As a user, I want user creation feature",
        "description": "Allow creating users"
    }]
    mock_read_file.return_value = str(story).replace("'", '"')  # JSON string

    # Set up mock session state
    st.session_state["stories_file"] = "mock_stories.json"

    # Act
    result_path = process_story_to_code()

    # Assert
    assert result_path.endswith("user_creation.py")
    assert "code_file" in st.session_state
    mock_write_file.assert_called_once()
    assert "user_creation" in mock_write_file.call_args[0][0]  # path to file

@patch("src.agents.coder_agent.write_file")
@patch("src.agents.coder_agent.read_file")
def test_process_story_to_code_fallback_factorial(mock_read_file, mock_write_file):
    # Arrange
    story = [{
        "summary": "As a user, I want to calculate math stuff",
        "description": "Math function"
    }]
    mock_read_file.return_value = str(story).replace("'", '"')

    st.session_state["stories_file"] = "mock_stories.json"

    # Act
    result_path = process_story_to_code()

    # Assert
    assert result_path.endswith("factorial.py")
    assert "code_file" in st.session_state
    mock_write_file.assert_called_once()
    assert "factorial" in mock_write_file.call_args[0][0]
