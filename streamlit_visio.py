import streamlit as st
from tools.visio_utils import (
    load_latest_story_file,
    generate_visio_xml_via_llm,
    upload_visio_file,
    append_visio_link_macro
)
from setting import get_bedrock_llm

st.set_page_config(page_title="Visio Diagram Generator", layout="wide")
st.title("📘 Visio Diagram Generator from JSON User Stories")

stories = load_latest_story_file()
if stories:
    st.success("✅ Latest story file loaded.")

    llm = get_bedrock_llm()
    with st.spinner("Generating Visio XML using LLM..."):
        visio_path = generate_visio_xml_via_llm(stories, llm)

    with open(visio_path, "r") as f:
        xml_preview = f.read()

    st.subheader("🧾 Visio VDX XML Preview")
    with st.expander("Click to view raw VDX XML", expanded=False):
        st.code(xml_preview, language="xml")

    st.subheader("🔗 Upload & Link in Confluence")
    with st.form("publish_form"):
        confluence_url = st.text_input("Confluence Base URL")
        username = st.text_input("Username")
        password = st.text_input("Password", type="password")
        page_id = st.text_input("Confluence Page ID")

        submit = st.form_submit_button("📤 Upload Visio File")
        if submit:
            uploaded_file = upload_visio_file(confluence_url, page_id, username, password, visio_path)
            if uploaded_file:
                append_visio_link_macro(confluence_url, page_id, username, password, uploaded_file)
