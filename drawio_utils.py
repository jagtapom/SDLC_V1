import os
import json
import requests
import streamlit as st
from setting import get_bedrock_llm

def load_latest_story_file(stories_dir="stories") -> dict:
    """Load the most recent JSON file from the stories folder."""
    files = [f for f in os.listdir(stories_dir) if f.endswith(".json")]
    if not files:
        st.error("No story files found in the 'stories/' folder.")
        return None
    latest_file = max(files, key=lambda f: os.path.getmtime(os.path.join(stories_dir, f)))
    path = os.path.join(stories_dir, latest_file)
    with open(path, "r") as f:
        return json.load(f)

def generate_drawio_xml_via_llm(stories_json: dict) -> str:
    """Use Bedrock LLM to generate draw.io-compatible XML diagram from user stories."""
    llm = get_bedrock_llm()

    prompt = f"""
You are a draw.io diagram generator.

Given the following user stories in JSON format, generate a draw.io-compatible XML diagram that shows the flow and relationships between the stories. Each story should be a labeled node. Connect them based on dependencies or sequence.

Ensure the output is full draw.io XML inside <mxGraphModel> ... </mxGraphModel> tags.

JSON Input:
{json.dumps(stories_json, indent=2)}
"""

    response = llm(prompt)
    xml = response.strip()
    return xml

def publish_drawio_to_confluence(username, password, confluence_url, page_id, drawio_xml):
    """Publish draw.io diagram to Confluence page."""
    headers = {
        "Content-Type": "application/json"
    }

    # Step 1: Get current page version and title
    res = requests.get(
        f"{confluence_url}/rest/api/content/{page_id}?expand=body.storage,version",
        auth=(username, password),
        headers=headers
    )

    if res.status_code != 200:
        st.error(f"Failed to fetch page info: {res.text}")
        return False

    data = res.json()
    current_version = data["version"]["number"]
    title = data["title"]

    # Step 2: Create draw.io macro content
    content = f"""
<ac:structured-macro ac:name="drawio">
  <ac:parameter ac:name="layout">fit</ac:parameter>
  <ac:plain-text-body><![CDATA[
{drawio_xml}
  ]]></ac:plain-text-body>
</ac:structured-macro>
"""

    payload = {
        "id": page_id,
        "type": "page",
        "title": title,
        "version": {"number": current_version + 1},
        "body": {
            "storage": {
                "value": content,
                "representation": "storage"
            }
        }
    }

    update = requests.put(
        f"{confluence_url}/rest/api/content/{page_id}",
        auth=(username, password),
        headers=headers,
        json=payload
    )

    if update.status_code in [200, 201]:
        st.success("✅ Draw.io diagram published to Confluence.")
        return True
    else:
        st.error(f"❌ Failed to publish: {update.status_code} - {update.text}")
        return False
