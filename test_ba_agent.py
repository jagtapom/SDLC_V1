import pytest
import tempfile
import json
import os
from pathlib import Path
from src.orchestrator import process_requirements_wrapper
import streamlit as st

@pytest.fixture(autouse=True)
def clean_streamlit_state():
    """Ensure clean Streamlit session state before each test."""
    st.session_state.clear()
    yield
    st.session_state.clear()

def test_process_requirements_wrapper_creates_user_stories():
    # Sample requirements content
    requirements = """
    1. Register a new user
    2. Login with valid credentials
    - Reset forgotten password
    """

    # Create a temporary requirements file
    with tempfile.NamedTemporaryFile(mode="w+", delete=False, suffix=".txt") as temp_file:
        temp_file.write(requirements)
        temp_file_path = temp_file.name

    try:
        # Run the function under test
        result_msg = process_requirements_wrapper(temp_file_path)

        # Assertions
        assert "Generated and saved" in result_msg
        assert "user stories" in result_msg

        # Extract expected stories path
        stories_file = os.path.basename(temp_file_path)
        expected_output_file = Path(__file__).parent.parent / "stories" / f"stories_{stories_file}"
        assert expected_output_file.exists(), "Output JSON file should exist"

        # Check JSON structure
        with open(expected_output_file, "r") as f:
            stories = json.load(f)
            assert len(stories) == 3
            for story in stories:
                assert "summary" in story
                assert story["summary"].startswith("As a user")
                assert "description" in story
                assert "priority" in story
                assert "story_points" in story
                assert "type" in story

        # Check Streamlit session state
        assert st.session_state["workflow_status"] == "stories_generated"
        assert st.session_state["stories_file"] == f"stories_{stories_file}"

    finally:
        # Clean up temporary files
        if os.path.exists(temp_file_path):
            os.remove(temp_file_path)
        if expected_output_file.exists():
            os.remove(expected_output_file)
