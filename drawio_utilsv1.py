import os
import json
import requests
import streamlit as st

DRAWIO_FILENAME = "diagram.drawio"

def load_latest_story_file(stories_dir="stories") -> dict:
    files = [f for f in os.listdir(stories_dir) if f.endswith(".json")]
    if not files:
        st.error("No story files found in the 'stories/' folder.")
        return None
    latest_file = max(files, key=lambda f: os.path.getmtime(os.path.join(stories_dir, f)))
    path = os.path.join(stories_dir, latest_file)
    with open(path, "r") as f:
        return json.load(f)

def generate_drawio_file_via_llm(stories_json: dict, llm) -> str:
    """Use LLM to generate draw.io XML and save to file"""
    prompt = f"""
You are a draw.io diagram generator.

Given the following user stories in JSON format, generate a draw.io-compatible XML diagram.

Return only XML inside <mxGraphModel> ... </mxGraphModel> tags.

JSON Input:
{json.dumps(stories_json, indent=2)}
"""
    response = llm(prompt)
    xml = response.strip()

    file_path = os.path.join("output", DRAWIO_FILENAME)
    os.makedirs("output", exist_ok=True)
    with open(file_path, "w") as f:
        f.write(xml)

    return file_path

def upload_drawio_file(confluence_url, page_id, username, password, file_path):
    url = f"{confluence_url}/rest/api/content/{page_id}/child/attachment"
    headers = {"X-Atlassian-Token": "no-check"}

    with open(file_path, "rb") as f:
        files = {"file": (DRAWIO_FILENAME, f, "application/octet-stream")}
        res = requests.post(url, headers=headers, files=files, auth=(username, password))

    if res.status_code in [200, 201]:
        st.success("✅ Draw.io attachment uploaded successfully.")
        return True
    else:
        st.error(f"❌ Upload failed: {res.status_code} - {res.text}")
        return False

def append_drawio_macro(confluence_url, page_id, username, password):
    """Append draw.io macro to Confluence page content referencing the uploaded file"""
    headers = {"Content-Type": "application/json"}

    # Step 1: Get current page version/content
    res = requests.get(
        f"{confluence_url}/rest/api/content/{page_id}?expand=body.storage,version",
        auth=(username, password), headers=headers
    )

    if res.status_code != 200:
        st.error(f"❌ Failed to get page content: {res.status_code} - {res.text}")
        return False

    data = res.json()
    version = data["version"]["number"]
    title = data["title"]
    old_body = data["body"]["storage"]["value"]

    # Step 2: Append draw.io macro at the end
    drawio_macro = f"""
<ac:structured-macro ac:name="drawio">
  <ac:parameter ac:name="name">{DRAWIO_FILENAME}</ac:parameter>
  <ac:parameter ac:name="layout">fit</ac:parameter>
</ac:structured-macro>
"""

    new_body = old_body + "<hr/>" + drawio_macro

    # Step 3: Update page
    payload = {
        "version": {"number": version + 1},
        "type": "page",
        "title": title,
        "body": {
            "storage": {
                "value": new_body,
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
        st.success("✅ Draw.io macro appended to page.")
        return True
    else:
        st.error(f"❌ Failed to update page: {update.status_code} - {update.text}")
        return False
