from autogen import GroupChatManager, GroupChat
from src.agents.ba_agent import ba_agent
from src.agents.coder_agent import coder_agent
from src.agents.jira_agent import jira_agent
from src.agents.supervisor_agent import supervisor_agent
from src.agents.hitl_agent import hitl_agent
from src.agents.review_agent import review_agent
from src.agents.devops_agent import devops_agent

from src.document_processor import extract_text
import asyncio

state = {
    'approvals': {
        'ba': asyncio.Event(),
        'jira': asyncio.Event(),
        'code': asyncio.Event(),
        'review': asyncio.Event(),
        'devops': asyncio.Event(),
    }
}

async def run_workflow_async(file_path: str, keyword: str):
    content = extract_text(file_path, keyword)

    await run_supervised_step('ba', ba_agent, content)
    await run_supervised_step('jira', jira_agent)
    await run_supervised_step('code', coder_agent)
    await run_supervised_step('review', review_agent)
    await run_supervised_step('devops', devops_agent)

async def run_supervised_step(step: str, target_agent, user_input: str = None):
    print(f"[SUPERVISOR] Triggering {step.upper()} via supervisor agent")
    supervisor_prompt = f"Please delegate the {step} task to the respective agent with command like 'run {step}_agent'."
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

def pass_approval(step):
    if step in state['approvals']:
        state['approvals'][step].set()
