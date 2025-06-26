import streamlit as st
from src.tools.story_to_confluence_diagram import process_and_publish_diagram

st.title("📊 User Story to Confluence Diagram")

stories_file = st.session_state.get("stories_file")
if not stories_file:
    st.warning("No stories file found. Please run BA Agent first.")
else:
    confluence_url = st.text_input("Confluence Base URL", placeholder="https://your-domain.atlassian.net/wiki")
    page_id = st.text_input("Confluence Page ID")
    username = st.text_input("Confluence Username")
    api_token = st.text_input("Confluence API Token", type="password")

    if st.button("📤 Generate & Publish Diagram"):
        try:
            result = process_and_publish_diagram(
                stories_path=f"./stories/{stories_file}",
                confluence_page_id=page_id,
                confluence_url=confluence_url,
                username=username,
                api_token=api_token
            )
            st.success(result)
        except Exception as e:
            st.error(f"Failed: {e}")


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
