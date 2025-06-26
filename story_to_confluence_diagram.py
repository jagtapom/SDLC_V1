# #src/tools/story_to_confluence_diagram.py
import requests
import json

def publish_to_confluence(base_url, page_id, username, api_token, new_content):
    headers = {
        "Content-Type": "application/json"
    }

    # Get current page version
    res = requests.get(
        f"{base_url}/rest/api/content/{page_id}?expand=body.storage,version",
        auth=(username, api_token)
    )
    res.raise_for_status()
    data = res.json()
    current_version = data["version"]["number"]

    # Update page with new content
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
