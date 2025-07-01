import os
import json
import requests
import streamlit as st
from setting import get_bedrock_llm


def load_latest_story_file(stories_dir="stories") -> dict:
    """Loads the latest JSON story file from the 'stories/' directory."""
    files = [f for f in os.listdir(stories_dir) if f.endswith(".json")]
    if not files:
        st.error("No story files found in the 'stories/' folder.")
        return None
    latest_file = max(files, key=lambda f: os.path.getmtime(os.path.join(stories_dir, f)))
    path = os.path.join(stories_dir, latest_file)
    with open(path, "r") as f:
        return json.load(f)


def ensure_drawio_file_exists(file_path="stories/diagram.drawio") -> bool:
    """Create a minimal valid blank draw.io diagram if it doesn't exist."""
    if not os.path.exists(file_path):
        blank_xml = """<mxfile host="app.diagrams.net">
  <diagram name="Page-1" id="blank">
    <mxGraphModel>
      <root>
        <mxCell id="0"/>
        <mxCell id="1" parent="0"/>
      </root>
    </mxGraphModel>
  </diagram>
</mxfile>"""
        os.makedirs(os.path.dirname(file_path), exist_ok=True)
        with open(file_path, "w") as f:
            f.write(blank_xml)
        return True
    return False


def generate_drawio_file_via_llm(stories_json: dict, llm) -> str:
    """Generates a draw.io-compatible XML diagram using the Bedrock LLM."""
    prompt = f"""
You are a draw.io diagram generator.
Given the following user stories in JSON format, generate a draw.io-compatible XML diagram.
Each story should be a labeled node connected based on sequence or dependency.
Wrap the output inside <mxGraphModel> ... </mxGraphModel> tags.

JSON Input:
{json.dumps(stories_json, indent=2)}
"""
    response = llm(prompt)
    xml = response.strip()

    output_path = os.path.join("stories", "diagram.drawio")
    with open(output_path, "w") as f:
        f.write(xml)
    return output_path


def upload_drawio_file(confluence_url, page_id, username, password, file_path):
    """Uploads the draw.io .drawio file as a Confluence attachment."""
    filename = os.path.basename(file_path)
    url = f"{confluence_url}/rest/api/content/{page_id}/child/attachment"

    headers = {"X-Atlassian-Token": "no-check"}
    files = {
        'file': (filename, open(file_path, 'rb'), 'application/vnd.jgraph.mxfile')
    }

    # Check if already exists
    check = requests.get(
        f"{url}?filename={filename}&expand=version",
        auth=(username, password),
        headers=headers
    )

    if check.status_code == 200 and check.json()['results']:
        existing_id = check.json()['results'][0]['id']
        version = check.json()['results'][0]['version']['number'] + 1
        upload_url = f"{url}/{existing_id}/data"
        params = {"minorEdit": "true"}
    else:
        upload_url = url
        params = {}

    res = requests.post(
        upload_url,
        auth=(username, password),
        headers=headers,
        files=files,
        params=params
    )

    if res.status_code in [200, 201]:
        st.success(f"✅ Diagram '{filename}' uploaded to Confluence.")
        return filename
    else:
        st.error(f"❌ Upload failed: {res.status_code} - {res.text}")
        return None


def append_drawio_macro(confluence_url, page_id, username, password, drawio_filename):
    """Appends a draw.io macro referencing the uploaded file at the end of the Confluence page."""
    page_url = f"{confluence_url}/rest/api/content/{page_id}?expand=body.storage,version"
    res = requests.get(page_url, auth=(username, password))

    if res.status_code != 200:
        st.error(f"Failed to fetch Confluence page: {res.status_code} - {res.text}")
        return False

    data = res.json()
    current_version = data["version"]["number"]
    title = data["title"]
    existing_body = data["body"]["storage"]["value"]

    # Macro to append
    macro = f"""
<ac:structured-macro ac:name="drawio">
  <ac:parameter ac:name="name">{drawio_filename}</ac:parameter>
  <ac:parameter ac:name="layout">fit</ac:parameter>
</ac:structured-macro>
"""

    if macro.strip() in existing_body:
        st.info("ℹ️ Draw.io macro already exists on page. Skipping re-append.")
        return True

    updated_body = existing_body + "<p></p>" + macro

    payload = {
        "id": page_id,
        "type": "page",
        "title": title,
        "version": {"number": current_version + 1},
        "body": {
            "storage": {
                "value": updated_body,
                "representation": "storage"
            }
        }
    }

    update = requests.put(
        f"{confluence_url}/rest/api/content/{page_id}",
        auth=(username, password),
        headers={"Content-Type": "application/json"},
        json=payload
    )

    if update.status_code in [200, 201]:
        st.success("✅ Draw.io macro appended to Confluence page.")
        return True
    else:
        st.error(f"❌ Failed to update page: {update.status_code} - {update.text}")
        return False
