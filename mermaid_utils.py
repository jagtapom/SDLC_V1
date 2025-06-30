import json
import requests
from setting import get_bedrock_llm

def generate_mermaid_from_stories(stories):
    """
    Converts a list of user stories into a Mermaid diagram using a Bedrock-hosted LLM.
    """
    if not isinstance(stories, list):
        return "graph TD\nA[Invalid Story Format]"

    llm = get_bedrock_llm()
    prompt = (
        "You are a software analyst. Based on the following user stories, "
        "generate a Mermaid diagram in `graph TD` format that visually represents "
        "the flow or relationship between these stories.\n\n"
        f"{json.dumps(stories, indent=2)}"
    )

    response = llm.invoke(prompt)
    diagram = response.get("output", "graph TD\nA[No response from LLM]")
    return diagram

def preview_confluence_page(base_url, page_id, username, password):
    url = f"{base_url}/rest/api/content/{page_id}?expand=version,space"
    response = requests.get(url, auth=(username, password))

    if response.status_code == 200:
        data = response.json()
        return {
            "title": data.get("title"),
            "version": data.get("version", {}).get("number"),
            "space": data.get("space", {}).get("key")
        }
    return None

def publish_to_confluence(base_url, page_id, username, password, mermaid_code):
    headers = {
        "Content-Type": "application/json"
    }

    # Get current page info
    res = requests.get(
        f"{base_url}/rest/api/content/{page_id}?expand=body.storage,version,space,title",
        auth=(username, password)
    )
    res.raise_for_status()
    data = res.json()
    version = data["version"]["number"] + 1

    content = (
        "<ac:structured-macro ac:name='code' ac:schema-version='1' ac:macro-id='mermaid-diagram'>"
        f"<ac:parameter ac:name='language'>mermaid</ac:parameter>"
        f"<ac:plain-text-body><![CDATA[{mermaid_code}]]></ac:plain-text-body>"
        "</ac:structured-macro>"
    )

    payload = {
        "id": page_id,
        "type": "page",
        "title": data["title"],
        "space": {"key": data["space"]["key"]},
        "body": {
            "storage": {
                "value": content,
                "representation": "storage"
            }
        },
        "version": {"number": version}
    }

    put_res = requests.put(
        f"{base_url}/rest/api/content/{page_id}",
        auth=(username, password),
        headers=headers,
        json=payload
    )

    return put_res.status_code == 200
