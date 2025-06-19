from autogen import AssistantAgent

coder_agent = AssistantAgent(
    name="coder_agent",
    system_message="You are a Python developer. Generate clean, functional Python code based on the approved requirements or JIRA story."
)
