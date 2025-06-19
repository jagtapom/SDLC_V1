# orchestrator.py (Updated: Skip Logic, Parallel Review + DevOps, HITL Override)
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
        'supervisor': asyncio.Event(),
    }
}

async def run_workflow_async(file_path: str, keyword: str):
    content = extract_text(file_path, keyword)

    await run_supervised_step('ba', ba_agent, content)
    await run_supervised_step('jira', jira_agent)

    # Check if Supervisor wants to skip coder_agent
    if await evaluate_supervisor_skip('code', content):
        print("Supervisor chose to SKIP coder_agent ✅")
    else:
        await run_supervised_step('code', coder_agent)

    # Parallel: Review and DevOps
    await run_parallel_steps([
        ('review', review_agent),
        ('devops', devops_agent)
    ])

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
    reply = await asyncio.to_thread(manager.run)
    last_msg = manager.chat.messages[-1]["content"].lower()

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
