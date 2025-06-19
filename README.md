# SDLC Automation with GenAI, HITL, and AWS Bedrock (Claude)

This project automates the Software Development Life Cycle (SDLC) using a multi-agent GenAI framework with HITL (Human-in-the-Loop) checkpoints. Built with NiceGUI (frontend), AutoGen agents, AWS Bedrock (Claude), and FastAPI backend.

---

## 📂 Project Structure
```
project_root/
├── frontend/
│   └── app.py                  # NiceGUI frontend (file upload, HITL approval, status)
├── src/
│   ├── agents/                # AutoGen agents
│   │   ├── ba_agent.py        # Extracts requirements
│   │   ├── jira_agent.py      # Creates JIRA stories
│   │   ├── coder_agent.py     # Generates code
│   │   ├── review_agent.py    # Reviews code
│   │   ├── devops_agent.py    # Builds GitLab CI/CD pipeline
│   │   ├── supervisor_agent.py# Delegates steps
│   │   └── hitl_agent.py      # HITL agent for approvals
│   ├── orchestrator.py        # Runs the multi-step async workflow
│   ├── document_processor.py  # Extracts and filters document input
│   ├── diagram_generator.py   # Generates Mermaid diagrams from text
│   ├── confluence_uploader.py # Publishes diagrams to Confluence via REST API
│   └── config/
│       └── settings.py        # LLM_CONFIG: model="bedrock.claude-v2"
└── main.py                    # FastAPI backend (used for workflow endpoints)
```

---

## 🚀 How It Works
1. User uploads a PDF/DOCX/TXT document in the UI.
2. `orchestrator.py` extracts content & runs agents step-by-step:
   - **BA Agent** extracts requirements
   - **HITL** must approve
   - **JIRA Agent** creates stories → updates Jira board
   - **Diagram** auto-generated from JIRA text (Mermaid)
   - **Published to Confluence** using macro
   - **Coder Agent** generates code (optional skip)
   - **Review + DevOps** run in parallel
   - All steps await **HITL approval** via frontend

---

## 🤖 Technologies Used
- **LLM**: Claude via AWS Bedrock (`LLM_CONFIG` in `settings.py`)
- **Frontend**: NiceGUI (Python UI)
- **Backend**: FastAPI (agent coordination)
- **Multi-Agent**: AutoGen framework
- **Document Parsing**: PyMuPDF, python-docx, plain text
- **Diagram**: Mermaid syntax → optionally exportable to draw.io / PNG
- **Confluence API**: For publishing diagrams as documentation

---

## ✅ Setup Instructions
1. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

2. Set environment variables:
   ```bash
   export CONFLUENCE_BASIC_AUTH="<base64 email:token>"
   export CONFLUENCE_API_TOKEN="..."
   export CONFLUENCE_USER_EMAIL="you@example.com"
   ```

3. Start the FastAPI backend:
   ```bash
   uvicorn main:app --reload
   ```

4. Run the frontend:
   ```bash
   python frontend/app.py
   ```

---

## 📥 Output Files (Auto-populated)
- `generated/ba_output.txt`
- `generated/jira_output.txt`
- `generated/code_output.txt`
- `generated/review_output.txt`
- `generated/devops_output.txt`
- `generated/requirement_diagram.mmd`

---

## 💡 Notes
- Workflow is async: multiple agents can run in parallel (e.g., review & devops)
- All agents are Claude-powered using the model configured in `settings.py`
- All steps can be reviewed and approved by a human via UI before proceeding

---

## 🔐 Security
- HITL prevents unreviewed AI content from deploying automatically
- Confluence token usage is via Basic Auth with encoded token (never exposed in logs)

---

## 📞 Support
For architecture help or feature support, contact [Omkar Jagtap](mailto:Omkarragtapp@gmail.com).

> _This is an enterprise-grade POC for intelligent SDLC acceleration._
