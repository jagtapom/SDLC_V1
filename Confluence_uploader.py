# confluence_uploader.py

import requests
import os

# Environment-based config for security
CONFLUENCE_BASE_URL = "https://your-company.atlassian.net/wiki"
CONFLUENCE_SPACE_KEY = "ENG"  # e.g., Engineering space
CONFLUENCE_TOKEN = os.getenv("CONFLUENCE_API_TOKEN")
CONFLUENCE_USER = os.getenv("CONFLUENCE_USER_EMAIL")

def publish_to_confluence(title: str, mermaid_code: str):
    """
    Publishes a Mermaid diagram to a new Confluence page using storage format.
    The diagram is wrapped in a <structured-macro> compatible with Confluence.
    """

    if not CONFLUENCE_TOKEN or not CONFLUENCE_USER:
        print("❌ Confluence credentials not set in environment.")
        return

    headers = {
        "Authorization": f"Basic {os.getenv('CONFLUENCE_BASIC_AUTH')}",
        "Content-Type": "application/json"
    }

    macro = f"""
        <ac:structured-macro ac:name="code" ac:schema-version="1" ac:macro-id="mermaid-graph">
            <ac:parameter ac:name="language">mermaid</ac:parameter>
            <ac:plain-text-body><![CDATA[{mermaid_code}]]></ac:plain-text-body>
        </ac:structured-macro>
    """

    payload = {
        "type": "page",
        "title": title,
        "space": { "key": CONFLUENCE_SPACE_KEY },
        "body": {
            "storage": {
                "value": macro,
                "representation": "storage"
            }
        }
    }

    url = f"{CONFLUENCE_BASE_URL}/rest/api/content"
    response = requests.post(url, json=payload, headers=headers)

    if response.status_code in [200, 201]:
        print(f"✅ Mermaid diagram successfully published to Confluence page: {title}")
    else:
        print(f"❌ Failed to publish to Confluence: {response.status_code}")
        print(response.text)
