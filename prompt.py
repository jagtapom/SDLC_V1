def generate_drawio_file_via_llm(stories_json: dict, llm) -> str:
    """Generates a styled draw.io-compatible XML diagram using the Bedrock LLM."""
    prompt = f"""
You are a draw.io diagram generator.

Your goal is to create a professional **flowchart-style diagram** that visualizes the following user stories and their relationships.

### Requirements:
- Each user story should be represented as a **rectangle shape** using `shape=rectangle`.
- Include clear **labels** for each node (e.g., story summary or ID).
- Use **color styling** to differentiate categories if available (e.g., UI, backend, infrastructure).
- Draw **arrows (edges)** between tasks based on logical flow or dependency.
- Use **draw.io-compatible XML** with proper structure:
  - Each node must be a `<mxCell>` with `vertex="1"`, and edges with `edge="1"`.
  - Wrap the content inside a single `<mxGraphModel>...</mxGraphModel>` tag.

### Example structure:
```xml
<mxGraphModel>
  <root>
    <mxCell id="0"/>
    <mxCell id="1" parent="0"/>
    <mxCell id="2" value="Login Page" style="shape=rectangle;fillColor=#DAE8FC;" vertex="1" parent="1">
      <mxGeometry x="40" y="80" width="120" height="60" as="geometry"/>
    </mxCell>
    <mxCell id="3" value="Authenticate" style="shape=rectangle;fillColor=#F8CECC;" vertex="1" parent="1">
      <mxGeometry x="220" y="80" width="120" height="60" as="geometry"/>
    </mxCell>
    <mxCell id="4" style="endArrow=block;" edge="1" source="2" target="3" parent="1">
      <mxGeometry relative="1" as="geometry"/>
    </mxCell>
  </root>
</mxGraphModel>
