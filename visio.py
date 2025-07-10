import os
import json
import requests
import streamlit as st
from setting import get_bedrock_llm

def load_latest_story_file(stories_dir="stories"):
    files = [f for f in os.listdir(stories_dir) if f.endswith(".json")]
    if not files:
        st.error("No JSON story files found.")
        return None
    latest_file = max(files, key=lambda f: os.path.getmtime(os.path.join(stories_dir, f)))
    path = os.path.join(stories_dir, latest_file)
    with open(path, "r") as f:
        return json.load(f)

def generate_visio_xml_via_llm(stories_json: dict, llm) -> str:
    prompt = f"""
You are a Visio diagram generator.

Given the following JSON user stories, generate a Visio-compatible VDX XML diagram representing the logical flow. Use shapes like rectangles for tasks, arrows for flow, and organize them visually in left-to-right or top-down layout.

Return the full VDX file contents.

JSON Input:
{json.dumps(stories_json, indent=2)}
"""
    response = llm(prompt)
    xml = response.strip()
    output_path = os.path.join("stories", "diagram.vdx")
    with open(output_path, "w") as f:
        f.write(xml)
    return output_path

def upload_visio_file(confluence_url, page_id, username, password, file_path):
    filename = os.path.basename(file_path)
    url = f"{confluence_url}/rest/api/content/{page_id}/child/attachment"
    files = {
        'file': (filename, open(file_path, 'rb'), 'application/vnd.visio')
    }
    headers = {
        "X-Atlassian-Token": "no-check"
    }
    res = requests.post(url, auth=(username, password), headers=headers, files=files)

    if res.status_code in [200, 201]:
        st.success("✅ Visio file uploaded to Confluence.")
        return filename
    else:
        st.error(f"❌ Upload failed: {res.status_code} - {res.text}")
        return None

def append_visio_link_macro(confluence_url, page_id, username, password, filename):
    res = requests.get(f"{confluence_url}/rest/api/content/{page_id}?expand=body.storage,version", auth=(username, password))
    if res.status_code != 200:
        st.error(f"Error fetching page: {res.text}")
        return False

    data = res.json()
    current_version = data["version"]["number"]
    title = data["title"]
    existing_body = data["body"]["storage"]["value"]

    attachment_link = f"""<p>📎 <ac:link><ri:attachment ri:filename="{filename}" /></ac:link></p>"""
    updated_body = existing_body + "<p></p>" + attachment_link

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

    update = requests.put(f"{confluence_url}/rest/api/content/{page_id}", auth=(username, password), headers={"Content-Type": "application/json"}, json=payload)

    if update.status_code in [200, 201]:
        st.success("✅ Visio file link appended to Confluence page.")
        return True
    else:
        st.error(f"❌ Failed to update page: {update.status_code} - {update.text}")
        return False
