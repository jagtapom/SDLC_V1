import streamlit as st
from tools.drawio_utils import (
    load_latest_story_file,
    generate_drawio_xml_via_llm,
    publish_drawio_to_confluence
)

st.set_page_config(page_title="Draw.io Diagram Generator", layout="wide")
st.title("📈 Draw.io Diagram Generator from User Stories")

# Step 1: Load the latest story file
stories = load_latest_story_file()
if stories:
    st.success("✅ Latest story file loaded from 'stories/' folder")

    # Step 2: Generate diagram
    with st.spinner("Generating draw.io XML using Bedrock LLM..."):
        drawio_xml = generate_drawio_xml_via_llm(stories)

    st.subheader("📄 Draw.io XML Preview")
    with st.expander("Click to view draw.io XML", expanded=False):
        st.code(drawio_xml, language="xml")

    # Step 3: Confluence publishing
    st.subheader("🔗 Publish to Confluence")
    with st.form("publish_form"):
        confluence_url = st.text_input("Confluence Base URL", placeholder="https://your-domain.atlassian.net/wiki")
        username = st.text_input("Confluence Username (Email)", placeholder="your-email@company.com")
        password = st.text_input("Confluence Password", type="password")
        page_id = st.text_input("Confluence Page ID", placeholder="123456")

        submit = st.form_submit_button("📤 Publish to Confluence")
        if submit:
            publish_drawio_to_confluence(username, password, confluence_url, page_id, drawio_xml)
