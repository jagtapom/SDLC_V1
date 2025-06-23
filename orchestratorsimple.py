# orchestrator.py (Updated: Summary Markdown Report)
from autogen import GroupChatManager, GroupChat
from src.agents.ba_agent import ba_agent
from src.agents.coder_agent import coder_agent
from src.agents.jira_agent import jira_agent
from src.agents.supervisor_agent import supervisor_agent
from src.agents.hitl_agent import hitl_agent
from src.agents.review_agent import review_agent
from src.agents.devops_agent import devops_agent
from src.document_processor import extract_text
from src.confluence_uploader import upload_to_confluence
import asyncio
import os

state = {
    'approvals': {
        'ba': asyncio.Event(),
        'jira': asyncio.Event(),
        'code': asyncio.Event(),
        'review': asyncio.Event(),
        'devops': asyncio.Event(),
        'supervisor': asyncio.Event(),
    }
}

async def run_workflow_async(file_path: str, keyword: str):
    report_lines = [
        "# SDLC Automation Summary",
        f"**Uploaded File:** {os.path.basename(file_path)}",
        f"**Keyword Used:** {keyword or 'None'}",
        "---"
    ]
    os.makedir("generated",exist_ok=True)
    content = extract_text(file_path, keyword)
    report_lines.append("## 📋 BA Extracted Requirement")
    report_lines.append(content.strip())

    await run_supervised_step('ba', ba_agent, content, step_outputs=step_outputs)
    with open("generated/jira_output.txt", "w" , encoding="utf-8") as f:
        f.write(content)

    await run_supervised_step('jira', jira_agent,step_outputs=step_outputs)
    with open("generated/ba_output.txt", "w" , encoding="utf-8") as f:
        f.write(step_outputs.get('jira',''))
    report_lines.append("\n## 📌 JIRA Stories")
    report_lines.append(jira_agent.last_output or "*No output captured*")

    if await evaluate_supervisor_skip('code', content):
        print("Supervisor chose to SKIP coder_agent ✅")
        report_lines.append("\n## 🧠 Code Generation")
        report_lines.append("*Skipped by supervisor.*")
    else:
        await run_supervised_step('code', coder_agent,step_outputs=step_outputs)
        with open("generated/code_output.txt", "w" ,encoding="utf-8") as f:
            f.write(step_outputs.get('code',''))
        report_lines.append("\n## 🧠 Code Output")
        report_lines.append(coder_agent.last_output or "*No output captured*")

    async def gather_review():
        await run_supervised_step('review', review_agent,step_ouputs=step_outputs)
        with open("generated/review_output.txt", "w" ,encoding="utf-8") as f:
            f.write(step_outputs.get('review,''))
        report_lines.append("\n## 🔍 Code Review")
        report_lines.append(review_agent.last_output or "*No review captured*")

    async def gather_devops():
        await run_supervised_step('devops', devops_agent, step_outputs=step_outputs)
        with open("generated/devops_output.txt", "w" ,encoding="utf-8") as f:
            f.write(step_outputs.get('devops',''))
        report_lines.append("\n## 🔧 DevOps CI/CD YAML")
        report_lines.append(devops_agent.last_output or "*No pipeline output captured*")

    await asyncio.gather(gather_review(), gather_devops())

    # Save report to disk
    os.makedirs("generated", exist_ok=True)
    markdown_text = "\n\n".join(report_lines)
    with open("generated/sdlc_report.md", "w", encoding="utf-8") as f:
        f.write(markdown_text)

    print("✅ Markdown summary report saved.")
    upload_to_confluence(markdown_text)
    print("📤 Report uploaded to Confluence.")

async def run_supervised_step(step: str, target_agent, user_input: str = None):
    print(f"[SUPERVISOR] Triggering {step.upper()} via supervisor agent")
    supervisor_prompt = f"Please delegate the {step} task."
    system_msg = [{"role": "user", "content": user_input}] if user_input else []
    system_msg.insert(0, {"role": "user", "content": supervisor_prompt})

    groupchat = GroupChat(
        agents=[supervisor_agent, target_agent],
        messages=system_msg,
        speaker_selection_method="round_robin"
    )
    manager = GroupChatManager(groupchat=groupchat)
    await asyncio.to_thread(manager.run)

    print(f"Waiting for HITL approval: {step}...")
    await state['approvals'][step].wait()
    print(f"[HITL] {step.upper()} step approved ✅")
    if groupchat.messages and len(grouchat.messages)>0:
        if step_outputs is not None:
        last_msg = groupchat.messages[-1].get("content","")
        step_outputs[step] = last_msg.strip()
    else:
        print(f"[Warn] No messages found for step '{step} '")
        if step_outputs is not None:
          step_outputs[step] = "* No output captured"
        

async def run_parallel_steps(agent_steps):
    tasks = []
    for step, agent in agent_steps:
        task = asyncio.create_task(run_supervised_step(step, agent))
        tasks.append(task)
    await asyncio.gather(*tasks)

async def evaluate_supervisor_skip(step, context):
    print(f"Evaluating if {step} step can be skipped...")
    prompt = f"Should the {step} step be skipped based on this context? Respond with: 'run {step}_agent', 'skip {step}_agent', or 'ask hitl to confirm'.\n\nContext:\n{context}"

    groupchat = GroupChat(
        agents=[supervisor_agent],
        messages=[{"role": "user", "content": prompt}],
        speaker_selection_method="auto"
    )
    manager = GroupChatManager(groupchat=groupchat)
    await asyncio.to_thread(manager.run)
    if grouchat.messages:    
      last_msg = manager.chat.messages[-1]["content"].lower()
    else:
        print(f"[Warm] No messages found for supervisor evaluation on '{step}'")
        last_msg = ""
    if f" skip {step}_agent" in last_msg:
                return True
            

    if f"skip {step}_agent" in last_msg:
        return True
    elif "ask hitl" in last_msg:
        print("Waiting for HITL to confirm supervisor skip decision...")
        await state['approvals']['supervisor'].wait()
        return False
    return False

def pass_approval(step):
    if step in state['approvals']:
        state['approvals'][step].set()



# # orchestrator.py (with corrected GroupChat usage)

# from autogen import GroupChat, GroupChatManager
# from src.agents.ba_agent import ba_agent
# from src.agents.jira_agent import jira_agent
# from src.agents.coder_agent import coder_agent
# from src.agents.review_agent import review_agent
# from src.agents.devops_agent import devops_agent
# from src.agents.supervisor_agent import supervisor_agent
# from src.agents.hitl_agent import wait_for_approval
# from src.diagram_generator import generate_mermaid_diagram
# from src.confluence_uploader import upload_to_confluence
# from src.document_processor import extract_relevant_content
# import asyncio
# import os

# # === Main async orchestrator ===
# async def run_workflow_async(file_path, keyword=None):
#     os.makedirs("generated", exist_ok=True)

#     print("[INFO] Extracting relevant content from document...")
#     content = extract_relevant_content(file_path, keyword)
#     print("[INFO] Extracted content:\n", content[:300])

#     with open("generated/ba_output.txt", "w", encoding="utf-8") as f:
#         f.write("### Extracted Requirement:\n" + content)

#     await wait_for_approval("ba")

#     print("[INFO] Generating JIRA Stories...")
#     jira_story = jira_agent.generate_story(content)
#     with open("generated/jira_output.txt", "w", encoding="utf-8") as f:
#         f.write(jira_story)

#     await wait_for_approval("jira")

#     print("[INFO] Generating Code...")
#     code = coder_agent.generate_code(jira_story)
#     with open("generated/code_output.txt", "w", encoding="utf-8") as f:
#         f.write(code)

#     await wait_for_approval("code")

#     print("[INFO] Reviewing Code...")
#     review = review_agent.review_code(code)
#     with open("generated/review_output.txt", "w", encoding="utf-8") as f:
#         f.write(review)

#     await wait_for_approval("review")

#     print("[INFO] Creating GitLab Pipeline...")
#     pipeline = devops_agent.create_pipeline(code)
#     with open("generated/devops_output.txt", "w", encoding="utf-8") as f:
#         f.write(pipeline)

#     await wait_for_approval("devops")

#     # Optional: Mermaid diagram generation
#     mermaid = generate_mermaid_diagram(jira_story)
#     with open("generated/requirement_diagram.mmd", "w", encoding="utf-8") as f:
#         f.write(mermaid)

#     print("[INFO] Uploading diagram to Confluence...")
#     upload_to_confluence(mermaid)

#     print("✅ SDLC workflow completed!")

# # Used by app.py (NiceGUI)
# step_event_map = {}

# def pass_approval(step):
#     event = step_event_map.get(step)
#     if event:
#         event.set()

# def reset_approval_events():
#     global step_event_map
#     step_event_map = {step: asyncio.Event() for step in ['ba', 'jira', 'code', 'review', 'devops']}

# reset_approval_events()
