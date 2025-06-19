from autogen import AssistantAgent

ba_agent = AssistantAgent(
    name="ba_agent",
    system_message="You are a Business Analyst. Extract clear, concise software requirements or user stories from the given input text."
)
