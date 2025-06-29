import streamlit as st
import os
import sys
import json
from pathlib import Path
from datetime import datetime
import logging
import time

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('logs/app_log.txt'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

# Project root
project_root = Path(__file__).parent.parent.parent.resolve()
sys.path.insert(0, str(project_root))

from src.orchestrator import initialize_supervisor, run_requirements_processing, run_jira_creation

def init_session_state():
    """Initialize Streamlit session state"""
    if "workflow_phase" not in st.session_state:
        st.session_state.workflow_phase = "initial"
    if "workflow_id" not in st.session_state:
        st.session_state.workflow_id = None
    if "uploaded_file_path" not in st.session_state:
        st.session_state.uploaded_file_path = None
    if "stories_file_path" not in st.session_state:
        st.session_state.stories_file_path = None
    if "current_stories" not in st.session_state:
        st.session_state.current_stories = None

def reset_workflow():
    """Resets the workflow state"""
    st.session_state.workflow_phase = "initial"
    st.session_state.workflow_id = None
    st.session_state.uploaded_file_path = None
    st.session_state.stories_file_path = None
    st.session_state.current_stories = None
    if 'supervisor' in st.session_state:
        del st.session_state['supervisor']

def display_approval_ui():
    """Display the UI for story approval and feedback"""
    stories = st.session_state.get("current_stories")
    if not stories:
        st.error("Could not load stories for approval")
        return

    st.subheader("Generated stories for your approval")
    if isinstance(stories, list):
        for idx, story in enumerate(stories, 1):
            with st.expander(f"Story {idx}: {story.get('summary', 'No Summary')}", expanded=True):
                st.write("**Description:**", story.get('description', 'No Description'))
                st.write("**Priority:**", story.get('priority', 'No priority'))
                st.write("**Story points:**", story.get('story_points', 'No story points'))
    else:
        st.write(stories)
        st.warning("Stories data is not in the expected format.")

    st.text_area("Enter your feedback (optional):", key="user_feedback")

    col1, col2 = st.columns(2)
    with col1:
        if st.button("Approve Stories"):
            st.session_state.workflow_phase = "creating_jira"
            st.rerun()

    with col2:
        if st.button("Send Feedback"):
            feedback = st.session_state.get("user_feedback", "").strip()
            if feedback:
                with st.spinner("Regenerating stories based on feedback"):
                    updated_path = st.session_state.supervisor.regenerate_stories(
                        st.session_state.stories_file_path, feedback
                    )
                if updated_path:
                    st.session_state.stories_file_path = updated_path
                    try:
                        with open(updated_path, 'r') as f:
                            st.session_state.current_stories = json.load(f)
                    except Exception as e:
                        st.error(f"Failed to reload regenerated stories: {e}")
                st.rerun()
            else:
                st.warning("Please enter feedback before submitting")

def main():
    st.title("SDLC Automation powered by AI")

    # Initialize state and supervisor agent
    init_session_state()
    supervisor = initialize_supervisor()
    st.session_state.supervisor = supervisor

    # 1. Initial State: File Upload
    if st.session_state.workflow_phase == "initial":
        uploaded_file = st.file_uploader("Choose a requirements file", type=['txt'])
        if uploaded_file:
            input_dir = os.path.join(project_root, "input")
            os.makedirs(input_dir, exist_ok=True)

            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            new_filename = f"upload_{timestamp}.txt"
            file_path = os.path.join(input_dir, new_filename)

            with open(file_path, "wb") as f:
                f.write(uploaded_file.getbuffer())

            st.session_state["uploaded_file_path"] = file_path
            st.success(f"File uploaded and saved as: {new_filename}")

        if st.button("Start Workflow") and st.session_state.uploaded_file_path:
            st.session_state.workflow_phase = "processing"
            st.session_state.workflow_id = f"wf_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
            st.rerun()

    # 2. Requirement Processing
    elif st.session_state.workflow_phase == "processing":
        with st.spinner("Processing Requirements..."):
            stories_path = run_requirements_processing(supervisor, st.session_state.uploaded_file_path)

        if stories_path:
            st.session_state.stories_file_path = stories_path
            try:
                with open(stories_path, 'r') as f:
                    st.session_state.current_stories = json.load(f)
            except Exception as e:
                st.error(f"Failed to load stories: {e}")
                reset_workflow()
            st.session_state.workflow_phase = "approval"
        else:
            st.error("Failed to process requirements")
            reset_workflow()
        st.rerun()

    # 3. User Approval
    elif st.session_state.workflow_phase == "approval":
        display_approval_ui()

    # 4. Jira Ticket Creation
    elif st.session_state.workflow_phase == "creating_jira":
        with st.spinner("Creating Jira tickets..."):
            success = run_jira_creation(supervisor, st.session_state.stories_file_path)
        if success:
            st.success("JIRA ticket creation successful")
        else:
            st.error("Failed to create Jira tickets")
        st.session_state.workflow_phase = "done"
        st.rerun()

    # 5. Done State
    elif st.session_state.workflow_phase == "done":
        st.info(f"Workflow {st.session_state.workflow_id} has finished.")
        if st.button("Start New Workflow"):
            reset_workflow()
            st.rerun()

if __name__ == "__main__":
    main()
