from autogen import AssistantAgent

review_agent = AssistantAgent(
    name="review_agent",
    system_message="You are a code reviewer. Provide feedback on the generated code and suggest improvements or confirm it is ready for production."
)
