# # supervisor_agent.py

# from autogen import AssistantAgent

# supervisor_agent = AssistantAgent(
#     name="supervisor_agent",
#     system_message=(
#         "You are a Supervisor Agent responsible for making intelligent decisions "
#         "about which agent to run next in an SDLC automation pipeline.\n\n"
#         "Your responsibilities:\n"
#         "- Receive a task and decide if the target agent should run, be skipped, or escalated to HITL (human-in-the-loop).\n"
#         "- Always reply with EXACT format: \n"
#         "    run agent_name\n"
#         "    skip agent_name\n"
#         "    ask hitl to confirm\n\n"
#         "Examples:\n"
#         "  run ba_agent\n"
#         "  skip coder_agent\n"
#         "  ask hitl to confirm\n\n"
#         "Use your judgment based on context passed from previous agents."
#     )
# )
# src/agents/supervisor_agent.py

# src/agents/supervisor_agent.py

from autogen.agentchat.contrib.supervisor_agent import SupervisorAgent
from src.config.settings import LLM_CONFIG
from src.agents.jira_agent import jira_agent
from src.agents.coder_agent import coder_agent
from src.agents.review_agent import review_agent
from src.agents.devops_agent import devops_agent

def build_supervisor(prompt: str = ""):
    return SupervisorAgent(
        name="Supervisor",
        llm_config=LLM_CONFIG,
        agents=[
            jira_agent,
            coder_agent,
            review_agent,
            devops_agent
        ],
        system_message="You are the SDLC supervisor. Based on the given context, decide whether to run or skip the specific agent, or defer to HITL."
    )

