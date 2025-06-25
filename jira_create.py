from atlassian import jira
import os 
from dotenv import load_dotenv
import logging
from typing import Dict

logger = logging.getlogger(__name__)

load_dotenv()

def create_jira_story(input_dict:Dict) -> str:
  """ Create a Jira story with specifiied summary and description"
  logger.inof(f"recieved input : {input_dict}")
   try:
       jira_url = os.getenv("Jira_instance_url")
       jira_username = os.getenv("Jira_username")
       jira_api_token = os.getenv("Jira_api_token")

       if not jira_url:
          logger.error("JIRA_instance_url not set")
          raise ValueError("Jira_instance_url  not set")

      if not jira_username:
          logger.error("Jira_username not set")
          raise ValueError("Jira_username not set")


      if not jira_api_token:
          logger.error("JIRA_api_token not set")
          raise ValueError("Jira_api_token  not set")

      jira = jira(
url = jira_url,
username=Jira_username,
password=jira_aoi_token,
cloud-True
)

      project_key = os.getenv("Jira-project-key")
      fields:{
"project" : {"key": project_key},
"summary" :input_dict.get("summary","New user story"),
"description":input_dict.get("decription", ""),
"issue_type" : {'name":"story"}
}
return issue_key
   
