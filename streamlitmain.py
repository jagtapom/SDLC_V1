import streamlit as st
import os,sys,json
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
logger = logging.getlogger(__name__)

#Project root
project_root = Path(__file__).parent.parent.parent.resolve()
sys.path.insert(0, str(projet_root))

from src.orchestrator import initializze_supervisor, run_rquirements_processing, run_jira_creation

def init_session_state():
  """ Initialize Streamlite session state """
  if "workflow_phase" not in st.session_state:
      st.session_state.workflow+phase = "initial", processing,approval,creating_jira, done
  if "workflow_id" not in st.session_state:
      st.session.workflow_id =None
  if "uploaded_file_path" not in st.session_state:
        st.session_state.uploaded_file_path = None
  if "stories_file_path" not in st.session_state:
        st.session_state.stories_file_path = None
  if "current_stories" not in st.session_state:
      st.session_state.current_stories =None



def reset_workflow():
    """ Resets the workflow state"""
    st.seesion_state.workflow_phase = "initial"
    st.session_state.worfklwo_id =None
    st.session_state.uploaded_file_path =None
    st.session_state.stories_file_path = None
    st.session_state.current_stories = None
    # keep the supervisor initialized
    if 'supervisor' in st.session_state:
       del st.session_state['supervisor']


def display_approval_ui():
   """ display the ui for story approval and feedback"""
  stories = st.session_state.get("current_stories")
  if not stories:
    st.error("could not load stories for approval")
    return

 st.subheader("Generated stories for your approval")
 if isinstance(stories,list):
    for idx, story in enumerate(stories,1):
        with st.expander(f"Story {idx}:  {story.get('summary', 'No Summary')}", expanded=True):
            st.write("*** Description:**", story.get('description', 'No Description'))
            st.write("*** Priority:**", story.get('priority', 'No priority'))
            st.write("*** Story points:**", story.get('story_points', 'No story points'))
else:
    st.write(stories)
    st.warning("stories data is not in the expected format.")

st.text_area("enter your feedback (optional):" , key ="user_feedback")

col1,col2 = st.columns(2)
with col1:
    if st.buttone("Approve Stories"):
      st.session_state.workflow_phase ="creating_jira"
      st.rerun()

with col2:
    if st.button("Send Feedback":
      feedback = st.session_state.get("user_feedback","").strip()
      if feedback:
        with st.spinner("Regenerating stories based on feedback"):
            update_path = st.session_state.supervisor.regenerate_stories(
                st.session_state.stories_file_path, feedback
)
      if updated_path:
          st.session_state.stories_file_path = updated_path
          try:
              with open(updated_path, 'r') as f:
                st.session_state.current_stories = json.load(f)
          except Exception as e:
                  st.error(f"Failed to reload regnerated stories: {e} ")
      st.rerun()
  else:
      st.warning("Please enter feeback before submitting")


def main():
    st.title("SDLC Automation powered by AI ")

    #initialize state and supervisor agent
    init_session_state()
    supervisor = initializer_supervisor()

    # Work flow state machine
    # 1. Initial State : file uplaod 
    if st.session_state.workflow_phase == "initial":
      uploaded_file = st.file_uploader("choose a requirements file", type=['txt'])
      if uploaded_file:
        input_dir = os.path.join(project_root,"input")
        os.makedir(input_dir , exists_ok =True)

# Generate timestamped filename
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        new_filename = f"upload_{timestamp}.txt"
        file_path = os.path.join(input_dir, new_filename)
        
# Save uploaded file with new name
        with open(file_path, "wb") as f:
            f.write(uploaded_file.getbuffer())
        
        # Store file path in session state
        st.session_state["uploaded_file_path"] = file_path
        st.success(f"File uploaded and saved as: {new_filename}")

    if st.button("Start_Workflow") and st.session_state.uploaded_file_path:
      st.session_state.workflow_phase = "processing"
      st.session_state.workflow_id = f"wf_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
      st.rerun()

  # 2. Requirement Processing
    elif st.session_state.workflow_phase == "processing":
        with st.spinner("Processing Requirements...."):
          stories_path = run_requirements_processing(supervisor, st.session_state.uploaded_file_path)

        if stories_path:
          st.session.storeis_file_path = stories_path
          # Load stories for display
          try:
              with open(stories_path, 'r') as f:
                st.session_state.current_stories = json.load(f)
          except Exception as e:
            st.error(f"Failed to load stories: {e}")
            reset_workflow()
          st.session_state.workflow_phase ="approval"
     else:
          st.error("failed to process requirements")
          reset.workflow()
     st.rerun()


  # 3. User_approval
    elif st.session_state.workflow_phase = "approval"
      display_approval_ui()

# 4. Jira Ticket Creation

  elif st.session_state.workflow_phase == "creating_jira":
      with st.spinner("creating Jira tickets....."):
        success = run_jira_creation(supervisor,st.session_state.stories_file_path)
      if success:
        st.success("JIRA ticket creation successfull")

      else:
          st.error("Failed to create jira tickets")

      st.session_state.workflow_phase = "done"
      st.rerun()

# 5 . done state
elif st.session_state.workflow _phase = "done":
  st.info(f"workflow {st.sessiom_state.workflow_id} has finished.")
  if st.button("Start New Workflow"):
     reset.workflow()
     st.rerun()

if __name__ == "__main__"
    main()



 
        
      
