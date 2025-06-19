# diagram_generator.py

def generate_mermaid_from_requirements(requirement_text: str) -> str:
    """
    Converts a list of requirements (from BA or JIRA output)
    into a Mermaid diagram in flowchart format.

    Parameters:
        requirement_text (str): multi-line requirement/story text.

    Returns:
        str: Mermaid-formatted graph (graph TD)
    """
    lines = [
        line.strip() for line in requirement_text.strip().split("\n")
        if line.strip()
    ]

    if not lines:
        return "graph TD\n    A[No valid requirements found]"

    nodes = [f"R{i}[{line}]" for i, line in enumerate(lines)]
    diagram = ["graph TD"]
    diagram.append(f"    Start([Start]) --> {nodes[0]}")

    for i in range(len(nodes) - 1):
        diagram.append(f"    {nodes[i]} --> {nodes[i+1]}")

    diagram.append(f"    {nodes[-1]} --> End([End])")

    return "\n".join(diagram)


# Optional test
if __name__ == "__main__":
    test_requirements = """
    User logs into the portal
    User uploads a document
    Document is analyzed by BA agent
    Requirements are sent to JIRA
    CI/CD pipeline is generated
    """
    diagram = generate_mermaid_from_requirements(test_requirements)
    print(diagram)
