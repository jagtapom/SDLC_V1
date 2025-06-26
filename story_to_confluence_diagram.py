# #src/tools/story_to_confluence_diagram.py
import json
import os
import requests
from typing import List, Dict
from pathlib import Path

def load_user_stories(stories_path: str) -> List[Dict]:
    """Load user stories from a JSON file."""
    if not os.path.exists(stories_path):
        raise FileNotFoundError(f"Stories file not found: {stories_path}")
    with open(stories_path, 'r') as f:
        return json.load(f)

def generate_mermaid_from_stories(stories: List[Dict]) -> str:
    """Generate Mermaid diagram content from user stories."""
    nodes = []
    links = []

    for i, story in enumerate(stories):
        node_id = f"N{i}"
        summary = story["summary"].replace('"', "'")
        nodes.append(f'{node_id}["{summary}"]')
        if i > 0:
            links.append(f"N{i-1} --> {node_id}")

    diagram_lines = ["graph TD"] + nodes + links
    return "\n".join(diagram_lines)

def wrap_mermaid_as_confluence_macro(mermaid_code: str) -> str:
    """Wrap Mermaid code in Confluence-compatible storage format."""
    return f"""
<ac:structured-macro ac:name="mermaid">
  <ac:plain-text-body><![CDATA[
{mermaid_code}
  ]]></ac:plain-text-body>
</ac:structured-macro>
"""

def publish_to_confluence(base_url, page_id, username, api_token, new_content):
    """Publish updated content to a Confluence page using REST API."""
    headers = {
        "Content-Type": "application/json"
    }

    res = requests.get(
        f"{base_url}/rest/api/content/{page_id}?expand=body.storage,version",
        auth=(username, api_token)
    )
    res.raise_for_status()
    data = res.json()
    current_version = data["version"]["number"]

    payload = {
        "id": page_id,
        "type": "page",
        "title": data["title"],
        "version": {"number": current_version + 1},
        "body": {
            "storage": {
                "value": new_content,
                "representation": "storage"
            }
        }
    }

    update_res = requests.put(
        f"{base_url}/rest/api/content/{page_id}",
        data=json.dumps(payload),
        headers=headers,
        auth=(username, api_token)
    )
    update_res.raise_for_status()
    return update_res.status_code == 200

def process_and_publish_diagram(stories_path: str, confluence_url: str, confluence_page_id: str,
                                username: str, api_token: str) -> str:
    """High-level function to convert stories to diagram and publish to Confluence."""
    stories = load_user_stories(stories_path)
    mermaid_code = generate_mermaid_from_stories(stories)
    wrapped = wrap_mermaid_as_confluence_macro(mermaid_code)
    success = publish_to_confluence(confluence_url, confluence_page_id, username, api_token, wrapped)
    if success:
        return "Diagram successfully published to Confluence ✅"
    else:
        raise RuntimeError("Failed to publish to Confluence")


# import os
# import json
# import logging
# import requests
# from pathlib import Path
# from typing import List, Dict
# import streamlit as st

# logger = logging.getLogger(__name__)

# def generate_mermaid_from_stories(stories: List[Dict]) -> str:
#     """Generate a Mermaid flowchart diagram based on user stories."""
#     diagram = ["flowchart TD"]
#     for i, story in enumerate(stories):
#         summary = story.get("summary", f"Story {i+1}")
#         node = f"STORY_{i+1}[\"{summary}\"]"
#         diagram.append(node)
#         if i > 0:
#             diagram.append(f"STORY_{i} --> STORY_{i+1}")

#     return "\n".join(diagram)

# def save_mermaid_to_file(mermaid_code: str, output_path: str) -> None:
#     """Save Mermaid code to a .mmd file."""
#     with open(output_path, "w") as f:
#         f.write(mermaid_code)
#     logger.info(f"Saved Mermaid diagram to {output_path}")

# def export_mermaid_to_drawio_image(mermaid_path: str, output_image: str) -> None:
#     """Use the Draw.io CLI to convert .mmd to .png (requires CLI setup)."""
#     result = os.system(f"draw.io --export --format png --output \"{output_image}\" \"{mermaid_path}\"")
#     if result != 0:
#         raise RuntimeError("Draw.io export failed")
#     logger.info(f"Exported Mermaid to image: {output_image}")

# def upload_to_confluence(confluence_url: str, page_id: str, image_path: str, auth: tuple) -> None:
#     """Upload the diagram to a Confluence page."""
#     with open(image_path, 'rb') as img:
#         image_data = img.read()

#     # 1. Attach image
#     attach_url = f"{confluence_url}/rest/api/content/{page_id}/child/attachment"
#     files = {
#         'file': (os.path.basename(image_path), image_data, 'image/png')
#     }
#     headers = {
#         'X-Atlassian-Token': 'no-check'
#     }

#     attach_response = requests.post(attach_url, auth=auth, headers=headers, files=files)
#     if not attach_response.ok:
#         raise Exception(f"Failed to upload image to Confluence: {attach_response.text}")

#     logger.info("Diagram uploaded to Confluence successfully.")

# def process_and_publish_diagram(stories_path: str, confluence_page_id: str, confluence_url: str, username: str, api_token: str):
#     """End-to-end processing from user stories to Confluence diagram."""
#     # Read stories from file
#     with open(stories_path, 'r') as f:
#         stories = json.load(f)

#     # Generate mermaid and save to .mmd
#     mermaid_code = generate_mermaid_from_stories(stories)
#     mermaid_path = os.path.join(Path(stories_path).parent, "user_flow.mmd")
#     save_mermaid_to_file(mermaid_code, mermaid_path)

#     # Export to PNG via draw.io
#     image_path = mermaid_path.replace(".mmd", ".png")
#     export_mermaid_to_drawio_image(mermaid_path, image_path)

#     # Upload to Confluence
#     upload_to_confluence(
#         confluence_url=confluence_url,
#         page_id=confluence_page_id,
#         image_path=image_path,
#         auth=(username, api_token)
#     )

#     return image_path
