from autogen import UserProxyAgent

hitl_agent = UserProxyAgent(
    name="hitl_agent",
    human_input_mode="ALWAYS",
    system_message="You are a Human-in-the-Loop agent. Review the content from previous agents and respond with 'approved by human' or 'rejected'.",
    is_termination_msg=lambda msg: 'approved by human' in msg.get('content', '').lower()
)
