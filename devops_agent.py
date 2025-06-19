from autogen import AssistantAgent

devops_agent = AssistantAgent(
    name="devops_agent",
    system_message="You are a DevOps engineer. Generate GitLab CI/CD pipeline YAML code to deploy and test the application automatically."
)
