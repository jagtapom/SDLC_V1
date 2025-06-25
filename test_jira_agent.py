import pytest
import tempfile
import json
import os
from pathlib import Path
import streamlit as st
from unittest.mock import patch
from src.orchestrator import process_stories  # adjust if your function is in another file

@pytest.fixture(autouse=True)
def clean_session_state():
    st.session_state.clear()
    yield
    st.session_state.clear()

@patch("src.orchestrator.create_jira_story")
def test_process_stories_success(mock_create_jira_story):
    # Setup
    mock_create_jira_story.side_effect = lambda story: f"JIRA-{hash(story['summary']) % 1000}"

    # Mock story data
    stories = [
        {
            "summary": "As a user, I want to sign up",
            "description": "Detailed story for sign up"
        },
        {
            "summary": "As a user, I want to reset my password",
            "description": "Detailed story for password reset"
        }
    ]

    # Write mock stories to a temp file in /stories
    project_root = Path(__file__).parent.parent
    stories_dir = project_root / "stories"
    os.makedirs(stories_dir, exist_ok=True)

    temp_stories_file = tempfile.NamedTemporaryFile(delete=False, suffix=".json", dir=stories_dir)
    json.dump(stories, temp_stories_file)
    temp_stories_file.close()
    
    stories_filename = os.path.basename(temp_stories_file.name)
    st.session_state["stories_file"] = stories_filename

    try:
        result = process_stories()

        # Assertions
        assert result == "Stories created in Jira"
        assert mock_create_jira_story.call_count == 2

        called_summaries = [call_args[0]['summary'] for call_args in mock_create_jira_story.call_args_list]
        assert called_summaries == [story["summary"] for story in stories]
    finally:
        # Cleanup
        os.remove(temp_stories_file.name)

