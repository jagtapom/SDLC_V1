# orchestrator.py (with corrected GroupChat usage)

from autogen import GroupChat, GroupChatManager
from src.agents.ba_agent import ba_agent
from src.agents.jira_agent import jira_agent
from src.agents.coder_agent import coder_agent
from src.agents.review_agent import review_agent
from src.agents.devops_agent import devops_agent
from src.agents.supervisor_agent import supervisor_agent
from src.agents.hitl_agent import wait_for_approval
from src.diagram_generator import generate_mermaid_diagram
from src.confluence_uploader import upload_to_confluence
from src.document_processor import extract_relevant_content
import asyncio
import os

# === Main async orchestrator ===
async def run_workflow_async(file_path, keyword=None):
    os.makedirs("generated", exist_ok=True)

    print("[INFO] Extracting relevant content from document...")
    content = extract_relevant_content(file_path, keyword)
    print("[INFO] Extracted content:\n", content[:300])

    with open("generated/ba_output.txt", "w", encoding="utf-8") as f:
        f.write("### Extracted Requirement:\n" + content)

    await wait_for_approval("ba")

    print("[INFO] Generating JIRA Stories...")
    jira_story = jira_agent.generate_story(content)
    with open("generated/jira_output.txt", "w", encoding="utf-8") as f:
        f.write(jira_story)

    await wait_for_approval("jira")

    print("[INFO] Generating Code...")
    code = coder_agent.generate_code(jira_story)
    with open("generated/code_output.txt", "w", encoding="utf-8") as f:
        f.write(code)

    await wait_for_approval("code")

    print("[INFO] Reviewing Code...")
    review = review_agent.review_code(code)
    with open("generated/review_output.txt", "w", encoding="utf-8") as f:
        f.write(review)

    await wait_for_approval("review")

    print("[INFO] Creating GitLab Pipeline...")
    pipeline = devops_agent.create_pipeline(code)
    with open("generated/devops_output.txt", "w", encoding="utf-8") as f:
        f.write(pipeline)

    await wait_for_approval("devops")

    # Optional: Mermaid diagram generation
    mermaid = generate_mermaid_diagram(jira_story)
    with open("generated/requirement_diagram.mmd", "w", encoding="utf-8") as f:
        f.write(mermaid)

    print("[INFO] Uploading diagram to Confluence...")
    upload_to_confluence(mermaid)

    print("✅ SDLC workflow completed!")

# Used by app.py (NiceGUI)
step_event_map = {}

def pass_approval(step):
    event = step_event_map.get(step)
    if event:
        event.set()

def reset_approval_events():
    global step_event_map
    step_event_map = {step: asyncio.Event() for step in ['ba', 'jira', 'code', 'review', 'devops']}

reset_approval_events()
