# src/diagram_generator.py

import json
import re

def generate_mermaid_diagram(jira_stories_text: str) -> str:
    """
    Generate Mermaid flowchart from formatted JIRA stories markdown text.

    Args:
        jira_stories_text (str): Markdown-formatted list of JIRA stories.

    Returns:
        str: Mermaid flowchart code.
    """

    if not jira_stories_text:
        return "flowchart TD\n    A[No stories found]"

    # Initialize diagram
    diagram = ["flowchart TD"]

    # Extract story titles (assuming headers like ### User Story N or **Title**)
    story_blocks = re.split(r"(?=### User Story|\*\*Title\*\*)", jira_stories_text)

    previous_node = None
    node_ids = []

    for idx, block in enumerate(story_blocks):
        lines = block.strip().splitlines()
        title = None

        for line in lines:
            if line.strip().lower().startswith("title") or "Title" in line:
                title = line.split(":")[-1].strip()
                break
            elif line.strip().startswith("###"):
                title = line.replace("###", "").strip()
                break

        if not title:
            title = f"Step {idx+1}"

        node_id = f"step{idx+1}"
        node_ids.append(node_id)
        diagram.append(f"    {node_id}[{title}]")

        if previous_node:
            diagram.append(f"    {previous_node} --> {node_id}")
        previous_node = node_id

    return "\n".join(diagram)



# # diagram_generator.py

# def generate_mermaid_from_requirements(requirement_text: str) -> str:
#     """
#     Converts a list of requirements (from BA or JIRA output)
#     into a Mermaid diagram in flowchart format.

#     Parameters:
#         requirement_text (str): multi-line requirement/story text.

#     Returns:
#         str: Mermaid-formatted graph (graph TD)
#     """
#     lines = [
#         line.strip() for line in requirement_text.strip().split("\n")
#         if line.strip()
#     ]

#     if not lines:
#         return "graph TD\n    A[No valid requirements found]"

#     nodes = [f"R{i}[{line}]" for i, line in enumerate(lines)]
#     diagram = ["graph TD"]
#     diagram.append(f"    Start([Start]) --> {nodes[0]}")

#     for i in range(len(nodes) - 1):
#         diagram.append(f"    {nodes[i]} --> {nodes[i+1]}")

#     diagram.append(f"    {nodes[-1]} --> End([End])")

#     return "\n".join(diagram)


# # Optional test
# if __name__ == "__main__":
#     test_requirements = """
#     User logs into the portal
#     User uploads a document
#     Document is analyzed by BA agent
#     Requirements are sent to JIRA
#     CI/CD pipeline is generated
#     """
#     diagram = generate_mermaid_from_requirements(test_requirements)
#     print(diagram)
