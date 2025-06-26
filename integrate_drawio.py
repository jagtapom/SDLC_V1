import streamlit as st
from src.tools.story_to_confluence_macro import generate_mermaid_code_from_stories, publish_to_confluence

st.title("📈 Publish Mermaid Diagram to Confluence")

stories_file = st.session_state.get("stories_file")
if not stories_file:
    st.warning("No stories file found. Run BA agent first.")
else:
    # Auth & Config
    confluence_url = st.text_input("Confluence Base URL")
    page_id = st.text_input("Confluence Page ID")
    username = st.text_input("Confluence Username")
    api_token = st.text_input("Confluence API Token", type="password")

    if st.button("📤 Publish Mermaid Diagram"):
        with open(f"./stories/{stories_file}", "r") as f:
            stories = json.load(f)

        mermaid_code = generate_mermaid_code_from_stories(stories)

        macro_body = f"""
<ac:structured-macro ac:name="mermaid">
  <ac:plain-text-body><![CDATA[
{mermaid_code}
  ]]></ac:plain-text-body>
</ac:structured-macro>
"""

        try:
            ok = publish_to_confluence(
                confluence_url,
                page_id,
                username,
                api_token,
                macro_body
            )
            if ok:
                st.success("✅ Mermaid diagram published to Confluence.")
            else:
                st.error("❌ Failed to publish.")
        except Exception as e:
            st.error(f"Error: {e}")

# import streamlit as st
# from src.tools.story_to_confluence_diagram import process_and_publish_diagram

# st.title("📊 User Story to Confluence Diagram")

# stories_file = st.session_state.get("stories_file")
# if not stories_file:
#     st.warning("No stories file found. Please run BA agent first.")
# else:
#     confluence_url = st.text_input("Confluence Base URL", placeholder="https://your-domain.atlassian.net/wiki")
#     page_id = st.text_input("Confluence Page ID")
#     username = st.text_input("Confluence Username")
#     api_token = st.text_input("Confluence API Token", type="password")

#     if st.button("📤 Generate & Publish Diagram"):
#         try:
#             diagram_path = process_and_publish_diagram(
#                 stories_path=f"./stories/{stories_file}",
#                 confluence_page_id=page_id,
#                 confluence_url=confluence_url,
#                 username=username,
#                 api_token=api_token
#             )
#             st.success(f"Diagram published to Confluence! ✅")
#             st.image(diagram_path, caption="Generated Diagram")
#         except Exception as e:
#             st.error(f"Failed: {e}")
