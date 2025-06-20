# app.py (Enhanced UI Styling + Log Section Moved Right)
from nicegui import ui
import requests
import os
from datetime import datetime

file_path = None
log_box_tail = ""
approval_status = {'ba': False, 'jira': False, 'code': False, 'review': False, 'devops': False, 'supervisor': False}

ui.add_head_html("""
<style>
    .custom-button {
        background-color: #0072CE;
        color: white;
        padding: 10px 20px;
        border: none;
        border-radius: 6px;
        font-weight: bold;
        font-size: 14px;
        cursor: pointer;
        margin-top: 8px;
    }
    .custom-button:hover {
        background-color: #005999;
    }
    .log-container {
        background-color: #f9f9f9;
        border-left: 3px solid #0072CE;
        padding: 8px;
        border-radius: 6px;
    }
    .badge-row {
        display: flex;
        gap: 12px;
        flex-wrap: wrap;
        margin-bottom: 12px;
    }
</style>
""")

# === MAIN LAYOUT ===
with ui.row().style("width: 100%; gap: 24px"):

    # LEFT PANEL
    with ui.column().style("min-width: 300px; gap: 12px"):

        ui.image('https://upload.wikimedia.org/wikipedia/en/thumb/3/3e/Barclays_Logo.svg/1920px-Barclays_Logo.svg.png').style('width: 140px')
        status_label = ui.label('Status: Waiting for document upload...')

        uploaded_file = ui.upload(label='Upload PDF/DOCX/TXT', on_upload=lambda e: handle_upload(e))
        keyword_input = ui.input(label='Optional Keyword (e.g., loan, finance)')
        ui.button('🚀 Start SDLC Workflow', on_click=lambda: trigger_supervisor()).classes('custom-button')

        ui.separator()
        ui.label('📜 Timeline').style("font-weight: bold; margin-top: 8px")
        status_timeline = ui.column().style('height: 300px; overflow-y: auto;')

    # RIGHT PANEL
    with ui.column().style("flex: 1; gap: 14px"):

        # Status badges
        with ui.element("div").classes("badge-row"):
            status_badges = {}
            for step in approval_status:
                badge = ui.badge(f'{step.upper()}: ⏳ Pending...', color='orange')
                status_badges[step] = badge

        # Agent output expansions
        agent_outputs = {
            'ba': ui.expansion('📋 BA Agent Output', value=True),
            'jira': ui.expansion('📌 JIRA Story Output', value=False),
            'code': ui.expansion('🧠 Code Generation Output', value=False),
            'review': ui.expansion('🔍 Review Agent Feedback', value=False),
            'devops': ui.expansion('🔧 DevOps Pipeline Output', value=False),
        }

        agent_textareas = {}
        for step in agent_outputs:
            with agent_outputs[step]:
                agent_textareas[step] = ui.textarea(label=f'{step.upper()} Output', value='').props('rows=8')
                ui.button(f'✅ Approve {step.upper()}', on_click=lambda s=step: approve_step(s)).classes('custom-button')

        # Supervisor section
        with ui.expansion('🧠 Supervisor Decision Requires Human Approval', value=False):
            supervisor_panel = ui.textarea(label='Supervisor uncertainty - human decision required', value='').props('rows=4')
            ui.button('✅ Confirm Supervisor Decision', on_click=lambda: approve_step('supervisor')).classes('custom-button')

        # Mermaid diagram
        with ui.expansion('📊 Requirement Diagram (Mermaid)', value=False):
            diagram_box = ui.textarea(label='Mermaid Diagram Code', value='').props('rows=10')
            def download_diagram():
                try:
                    with open('generated/requirement_diagram.mmd', 'r') as f:
                        content = f.read()
                    ui.download(text=content, filename='requirement_diagram.mmd', mime_type='text/plain')
                except FileNotFoundError:
                    append_log("[WARN] Mermaid diagram not found.")
            ui.button('📥 Download Mermaid Diagram', on_click=download_diagram).classes('custom-button')

        # Log section now here
        ui.separator()
        ui.label('🪵 Agent Logs').style("font-weight: bold")
        with ui.element("div").classes("log-container"):
            log_box = ui.textarea(label='', value='').props('rows=10 auto-grow').style('width: 100%')

# === HELPERS ===
def append_log(msg):
    global log_box_tail
    log_box_tail += f"\n{msg}"
    log_box.value = log_box_tail

def append_timeline(message, error=False):
    now = datetime.now().strftime('%H:%M:%S')
    color = 'red' if error else 'black'
    with status_timeline:
        ui.label(f"[{now}] {message}").style(f'color: {color}; font-size: 13px')

def handle_upload(e):
    global file_path
    try:
        upload_dir = "uploaded_files"
        os.makedirs(upload_dir, exist_ok=True)
        file_path = os.path.join(upload_dir, e.name)
        with open(file_path, 'wb') as f:
            content = e.content if isinstance(e.content, bytes) else e.content.read()
            f.write(content)
        append_log(f"✅ File saved: {file_path}")
        status_label.text = f'Status: Uploaded {e.name}'
        append_timeline(f"📄 File uploaded: {e.name}")
    except Exception as err:
        append_log(f"[ERROR] Upload failed: {err}")
        status_label.text = 'Status: Upload failed.'
        append_timeline(f"❌ Upload failed: {err}", error=True)

def trigger_supervisor():
    global file_path
    if not file_path or not os.path.exists(file_path):
        append_log(f"[ERROR] File not found: {file_path}")
        status_label.text = '⚠️ Please upload a valid file first.'
        append_timeline("❌ File missing. Upload first.", error=True)
        return
    try:
        response = requests.post('http://localhost:8000/start-workflow', json={'file_path': file_path, 'keyword': keyword_input.value or ""})
        response.raise_for_status()
        append_log("✅ Workflow triggered")
        status_label.text = 'Status: Workflow triggered.'
        append_timeline("🚀 Workflow triggered.")
        ui.timer(2.0, lambda: fetch_outputs(), once=False)
    except Exception as e:
        append_log(f"[ERROR] Backend call failed: {e}")
        ui.notify(f"Trigger failed: {e}", type='negative')
        status_label.text = 'Status: Trigger failed.'
        append_timeline(f"❌ Trigger failed: {e}", error=True)

def approve_step(step):
    try:
        requests.post('http://localhost:8000/approve-step', json={'step': step})
        approval_status[step] = True
        status_label.text = f'Status: {step.upper()} step approved.'
        status_badges[step].text = f"{step.upper()}: ✅ Approved"
        status_badges[step].props('color=green')
        ui.notify(f"✅ {step.upper()} approved.", type='positive')
        append_log(f"✅ Approved: {step.upper()}")
        append_timeline(f"✅ {step.upper()} approved.")
    except Exception as e:
        append_log(f"[ERROR] Approval failed for {step}: {e}")
        ui.notify(f"Approval error: {e}", type='negative')
        append_timeline(f"❌ Approval error: {e}", error=True)

async def fetch_outputs():
    try:
        for step in agent_textareas:
            file = f"generated/{step}_output.txt"
            if os.path.exists(file):
                content = open(file, 'r', encoding='utf-8').read()
                if content.strip():
                    agent_textareas[step].value = content
                    status_badges[step].text = f"{step.upper()}: 📝 Ready"
                    status_badges[step].props('color=blue')
                    append_timeline(f"📥 {step.upper()} output loaded.")
        if os.path.exists("generated/requirement_diagram.mmd"):
            with open("generated/requirement_diagram.mmd", "r") as df:
                diagram_box.value = df.read()
                append_timeline("📊 Mermaid diagram loaded.")
    except Exception as e:
        append_log(f"[ERROR] While fetching outputs: {e}")
        ui.notify(f"Fetching failed: {e}", type='negative')
        append_timeline(f"❌ Fetching error: {e}", error=True)

ui.run()
