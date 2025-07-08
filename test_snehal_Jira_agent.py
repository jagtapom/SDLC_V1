# tests/agents/test_jira_agent.py

import pytest
from unittest.mock import patch, MagicMock
from src.agents import jira_agent as agent_module

def test_jira_agent_instantiation():
    assert agent_module.jira_agent.name == "Jira_Agent"
    assert agent_module.jira_agent.human_input_mode == "NEVER"
    assert agent_module.jira_agent.max_consecutive_auto_reply == 1
    assert agent_module.jira_agent.code_execution_config is False

def test_llm_config_structure():
    tools = agent_module.jira_agent.llm_config.get("tools", [])
    assert isinstance(tools, list)
    assert tools[0]["type"] == "function"
    assert tools[0]["function"]["name"] == "create_jira_stories"
    assert "stories_file_path" in tools[0]["function"]["parameters"]["properties"]

@patch("src.agents.jira_agent.ConversableAgent")
def test_agent_creation_with_mock(mock_conversable_agent):
    mock_agent_instance = MagicMock()
    mock_conversable_agent.return_value = mock_agent_instance

    from importlib import reload
    reload(agent_module)  # Re-import the module to trigger agent creation

    mock_conversable_agent.assert_called_once()
    assert mock_conversable_agent.call_args[1]["name"] == "Jira_Agent"
