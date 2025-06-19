# SDLC_V1
SDLC V1 version
# 🧠 SDLC Automation with AutoGen + HITL + NiceGUI

This project is a fully asynchronous, human-in-the-loop (HITL), document-driven SDLC automation system using AutoGen agents and a NiceGUI frontend.

---

## 📦 Project Structure

```
project_root/
├── frontend/
│   └── app.py                      # NiceGUI frontend with real-time status + HITL UI
├── src/
│   ├── agents/
│   │   ├── ba_agent.py            # Business Analyst
│   │   ├── jira_agent.py          # JIRA Story Generator
│   │   ├── coder_agent.py         # Code Generator
│   │   ├── review_agent.py        # Code Reviewer
│   │   ├── devops_agent.py        # GitLab CI/CD YAML Generator
│   │   ├── supervisor_agent.py    # Supervises agent delegation
│   │   └── hitl_agent.py          # Human-in-the-loop agent
│   ├── orchestrator.py            # Main orchestration logic
│   └── document_processor.py      # Extracts and filters uploaded document content
└── main.py                        # FastAPI backend (NiceGUI interacts with this)
```

---

## ⚙️ Setup Instructions

### 1. 🐍 Create virtual environment and install packages
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

pip install fastapi uvicorn nicegui autogen python-docx pdfplumber docx2txt
```

### 2. ✅ Start FastAPI backend
```bash
uvicorn main:app --reload --port 8000
```

### 3. 🖥️ Start NiceGUI frontend
```bash
cd frontend
python app.py
```
Access UI at: `http://localhost:8080`

---

## 🚀 How It Works

1. **Upload a document** (`.pdf`, `.docx`, `.txt`) and optionally enter a keyword (e.g., "loan").
2. Content is extracted and passed to the **BA Agent**.
3. Each agent step (JIRA, Code, Review, DevOps) is executed **only after HITL approval**.
4. A **Supervisor Agent** controls delegation and sends commands like `run ba_agent`.
5. Results appear in expandable panels for human review.
6. Once `✅ Approved`, the next agent is triggered automatically.

---

## 🎨 Customizations
- 🔒 Secure HITL approvals using Auth (future)
- 🧠 Replace Claude with OpenAI/Bedrock/LLM of choice
- 📤 Add download buttons to export generated code

---

## 📸 Frontend Features
- Barclays Logo (add image path to `ui.image()`)
- Real-time stepwise status update (coming via `ui.badge()`)
- HITL Approvals with `Approve` buttons
- Upload + Filter + Launch Workflow in one interface

---

## 📞 Questions or Issues?
Open an issue or ping in your team chat with tag `#sdlc-autogen`

---

Built with ❤️ using AutoGen, FastAPI, and NiceGUI

