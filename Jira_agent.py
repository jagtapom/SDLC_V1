from autogen import AssistantAgent

jira_agent = AssistantAgent(
    name="jira_agent",
    system_message="You are a JIRA story generator. Convert the approved software requirements into JIRA story format with title, description, and acceptance criteria."
)
