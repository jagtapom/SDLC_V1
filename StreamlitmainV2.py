import streamlit as st
import os
import sys
import json
from pathlib import Path
from datetime import datetime
import logging
import time
import requests

# Configure logging output to a list
log_messages = []
class StreamlitLogger(logging.Handler):
    def emit(self, record):
        log_entry = self.format(record)
        log_messages.append(log_entry)

# Set up logging
log_handler = StreamlitLogger()
log_handler.setFormatter(logging.Formatter('%(asctime)s - %(levelname)s - %(message)s'))
logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)
logger.addHandler(log_handler)

# Project root
project_root = Path.cwd()
sys.path.insert(0, str(project_root))

from src.orchestrator import initialize_supervisor, run_requirements_processing, run_jira_creation
from tools.mermaid_utils import generate_mermaid_from_stories, preview_confluence_page, publish_to_confluence

def init_session_state():
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
    if "timeline" not in st.session_state:
        st.session_state.timeline = []
    if "mermaid_code" not in st.session_state:
        st.session_state.mermaid_code = None

def log_step(step):
    timestamp = datetime.now().strftime("%H:%M:%S")
    st.session_state.timeline.append(f"{timestamp} - {step}")
    logger.info(step)

def reset_workflow():
    st.session_state.workflow_phase = "initial"
    st.session_state.workflow_id = None
    st.session_state.uploaded_file_path = None
    st.session_state.stories_file_path = None
    st.session_state.current_stories = None
    st.session_state.timeline = []
    st.session_state.mermaid_code = None
    if 'supervisor' in st.session_state:
        del st.session_state['supervisor']

def display_approval_ui():
    stories = st.session_state.get("current_stories")
    if not stories:
        st.error("Could not load stories for approval")
        return

    st.subheader("Generated Stories for Approval")
    if isinstance(stories, list):
        for idx, story in enumerate(stories, 1):
            with st.expander(f"Story {idx}: {story.get('summary', 'No Summary')}", expanded=True):
                st.markdown(f"**Description:** {story.get('description', 'No Description')}")
                st.markdown(f"**Priority:** {story.get('priority', 'No priority')}")
                st.markdown(f"**Story points:** {story.get('story_points', 'No story points')}")
    else:
        st.write(stories)
        st.warning("Stories data is not in the expected format.")

    st.text_area("Enter your feedback (optional):", key="user_feedback")

    col1, col2 = st.columns(2)
    with col1:
        if st.button("Approve Stories"):
            st.session_state.workflow_phase = "creating_jira"
            log_step("User approved stories")
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
                        log_step("Stories regenerated with feedback")
                    except Exception as e:
                        st.error(f"Failed to reload regenerated stories: {e}")
                        logger.error(str(e))
                st.rerun()
            else:
                st.warning("Please enter feedback before submitting")

def main():
    init_session_state()
    supervisor = initialize_supervisor()
    st.session_state.supervisor = supervisor

    col1, col2 = st.columns([1, 4])
    with col1:
        st.image("https://upload.wikimedia.org/wikipedia/commons/5/59/Barclays_logo.svg", width=100)
        st.markdown("### Workflow Timeline")
        for step in st.session_state.timeline:
            st.markdown(f"- {step}")

    with col2:
        st.title("SDLC Automation - Barclays")

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

                st.session_state.uploaded_file_path = file_path
                log_step(f"File uploaded: {new_filename}")
                st.success(f"File uploaded and saved as: {new_filename}")

            if st.button("Start Workflow") and st.session_state.uploaded_file_path:
                st.session_state.workflow_phase = "processing"
                st.session_state.workflow_id = f"wf_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
                log_step("Workflow started")
                st.rerun()

        elif st.session_state.workflow_phase == "processing":
            with st.spinner("Processing Requirements..."):
                stories_path = run_requirements_processing(supervisor, st.session_state.uploaded_file_path)

            if stories_path:
                st.session_state.stories_file_path = stories_path
                try:
                    with open(stories_path, 'r') as f:
                        st.session_state.current_stories = json.load(f)
                    st.session_state.workflow_phase = "approval"
                    log_step("Requirements processed")
                except Exception as e:
                    st.error(f"Failed to load stories: {e}")
                    logger.error(str(e))
                    reset_workflow()
            else:
                st.error("Failed to process requirements")
                reset_workflow()
            st.rerun()

        elif st.session_state.workflow_phase == "approval":
            display_approval_ui()

        elif st.session_state.workflow_phase == "creating_jira":
            with st.spinner("Creating Jira tickets..."):
                run_jira_creation(supervisor, st.session_state.stories_file_path)
            st.session_state.workflow_phase = "generate_mermaid"
            log_step("JIRA tickets created")
            st.rerun()

        elif st.session_state.workflow_phase == "generate_mermaid":
            try:
                with open(st.session_state.stories_file_path, 'r') as f:
                    stories_data = json.load(f)
                mermaid_code = generate_mermaid_from_stories(stories_data)
                st.session_state.mermaid_code = mermaid_code
                log_step("Mermaid diagram generated")
                st.session_state.workflow_phase = "publish_preview"
            except Exception as e:
                st.error("Failed to generate diagram")
                logger.error(str(e))
                st.session_state.workflow_phase = "done"
            st.rerun()

        elif st.session_state.workflow_phase == "publish_preview":
            with st.expander("Mermaid Diagram Preview"):
                st.markdown(f"""```mermaid\n{st.session_state.mermaid_code}```""")

            st.markdown("### Confluence Publishing")
            with st.form("confluence_form"):
                confluence_url = st.text_input("Confluence Base URL")
                username = st.text_input("Username")
                password = st.text_input("Password", type="password")
                page_id = st.text_input("Page ID")
                preview_btn, publish_btn = st.columns(2)

                preview = preview_btn.form_submit_button("Preview in Confluence")
                publish = publish_btn.form_submit_button("Publish")

                if preview:
                    preview_result = preview_confluence_page(confluence_url, page_id, username, password)
                    if preview_result:
                        st.success("Page preview fetched successfully")
                        st.markdown(f"**Title:** {preview_result['title']}")
                        st.markdown(f"**Version:** {preview_result['version']} | **Space:** {preview_result['space']} ")
                    else:
                        st.error("Failed to fetch page preview")

                if publish:
                    try:
                        success = publish_to_confluence(
                            confluence_url, page_id, username, password, st.session_state.mermaid_code
                        )
                        if success:
                            st.success("Diagram published to Confluence successfully")
                            log_step("Diagram published to Confluence")
                            st.session_state.workflow_phase = "done"
                        else:
                            st.error("Failed to publish to Confluence")
                    except Exception as e:
                        st.error(f"Error publishing to Confluence: {e}")
                        logger.error(str(e))

        elif st.session_state.workflow_phase == "done":
            st.info(f"Workflow {st.session_state.workflow_id} has finished.")
            if st.button("Start New Workflow"):
                reset_workflow()
                log_step("Workflow reset")
                st.rerun()

        st.markdown("---")
        st.markdown("### Activity Logs")
        for msg in log_messages[-10:]:
            st.markdown(f"<pre style='color:gray;'>{msg}</pre>", unsafe_allow_html=True)

if __name__ == "__main__":
    main()
