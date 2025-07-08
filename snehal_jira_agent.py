from autogen import ConversableAgent
from src.config.setting import LLM_CONFIG
impor tlogging
import json
from pathlib import Path
import os
from src.tools.jira_create_tool import import create_jira_story

logger = logging.getlogger(__name__)

llm_config_with_tool = LLM_CONFIG.copy()
llm_config_with_tool["tools] = [
{
"type": "function",
"function":{
  "name": "create_jira_stories",
  "description": "Create Jira Stories from a JSON file containing user stories.",
  "parameters":{
    "type":"object",
    "properties":{
      "stories_file_path":{
        "type"""string",
        "description": "the absolute path to the JSON fiel cntaining the stories."
      }
    },
    "required":["stories_file_path"]
  }
}
}
]

jira_agent = CoversableAgent(
  name='Jira_Agent",
  system message="""You are a jira agent responsible for creating and managing Jira tickets.When given a file path to stories,call teh create_jira_stories tool to create the tickets. Do not ask
  for confirmation. Call the tool direclty with the provided file path.""",
  llm_config=llm_config_with_tool,
  human_imnput_mode="NEVER",
  max_consecutive_auto_reply=1,
  code_execution_config=False)
