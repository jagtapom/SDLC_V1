import pytest
import json
import os
from unittest.mock import patch, mock_open, MagicMock
from pathlib import Path

import streamlit as st
from src.agents.ba_agent import process_requirements_wrapper

@pytest.fixture(autouse=True)
def clear_session_state():
    """Clear Streamlit session before and after each test."""
    st.session_state.clear()
    yield
    st.session_state.clear()

@patch("src.agents.ba_agent.read_file")
@patch("builtins.open", new_callable=mock_open)
@patch("json.dump")
@patch("os.makedirs")
def test_process_requirements_wrapper_success(mock_makedirs, mock_json_dump, mock_open_file, mock_read_file):
    # Arrange
    fake_file_path = "requirements.txt"
    mock_read_file.return_value = """
1. Login functionality
2. Password reset
- Email verification
"""

    # Act
    result = process_requirements_wrapper(fake_file_path)

    # Assert expected session state and result
    assert st.session_state["workflow_status"] == "stories_generated"
    assert "stories_file" in st.session_state
    assert result.startswith("Generated and saved 3 user stories")

    # Check file save and logging
    mock_open_file.assert_called_once()
    mock_json_dump.assert_called_once()
