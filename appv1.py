# app.py (NiceGUI Frontend with Timeline, Auto-Scroll, and Live Updates)
from nicegui import ui
import requests
import os
import base64
from datetime import datetime

status_label = ui.label('Status: Waiting for document upload...')
log_box = ui.textarea(label='Logs', value='').props('rows=15 auto-grow')
log_box_tail = ""
keyword_input = ui.input(label='Optional Keyword (e.g., loan, finance)')
file_path = None
status_timeline = ui.column().style('margin-top: 12px')

approval_status = {'ba': False, 'jira': False, 'code': False, 'review': False, 'devops': False, 'supervisor': False}

# Branding
ui.image('https://upload.wikimedia.org/wikipedia/en/thumb/3/3e/Barclays_Logo.svg/1920px-Barclays_Logo.svg.png').style('width: 160px')
ui.separator()

# Status Badges
status_badges = {
    'ba': ui.badge('BA: ⏳ Waiting...', color='grey'),
    'jira': ui.badge('JIRA: ⏳ Waiting...', color='grey'),
    'code': ui.badge('Code: ⏳ Waiting...', color='grey'),
    'review': ui.badge('Review: ⏳ Waiting...', color='grey'),
    'devops': ui.badge('DevOps: ⏳ Waiting...', color='grey'),
    'supervisor': ui.badge('Supervisor: ⏳ Waiting...', color='grey'),
}

# Upload Widget

def handle_upload(e):
    global file_path
    try:
        upload_dir = "uploaded_files"
        if not os.path.exists(upload_dir):
            os.makedirs(upload_dir)

        file_path = os.path.join(upload_dir, e.name)
        append_log(f"[DEBUG] Uploading: {file_path}")

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

uploaded_file = ui.upload(label='Upload PDF/DOCX/TXT', on_upload=handle_upload)

# Timeline Helper

def append_timeline(message, error=False):
    now = datetime.now().strftime('%H:%M:%S')
    color = 'red' if error else 'black'
    with status_timeline:
        ui.label(f"[{now}] {message}").style(f'color: {color}; font-size: 13px')

# Log Helper

def append_log(msg):
    global log_box_tail
    log_box_tail += f"\n{msg}"
    log_box.value = log_box_tail

# Trigger Backend

def trigger_supervisor():
    global file_path
    if not file_path or not os.path.exists(file_path):
        append_log(f"[ERROR] File not found: {file_path}")
        status_label.text = '⚠️ Please upload a valid file first.'
        append_timeline("❌ File missing. Upload first.", error=True)
        return

    try:
        append_log(f"📡 Calling backend with file: {file_path}")
        response = requests.post('http://localhost:8000/start-workflow', json={
            'file_path': file_path,
            'keyword': keyword_input.value or ""
        })
        response.raise_for_status()
        msg = response.json().get('message')
        append_log(f"✅ Workflow started: {msg}")
        status_label.text = 'Status: Workflow triggered.'
        append_timeline("🚀 Workflow triggered.")
        ui.timer(2.0, lambda: fetch_outputs(), once=False)
    except Exception as e:
        append_log(f"[ERROR] Backend call failed: {e}")
        status_label.text = 'Status: Trigger failed.'
        append_timeline(f"❌ Trigger failed: {e}", error=True)

ui.button('🚀 Start SDLC Workflow', on_click=trigger_supervisor)

# Output Sections
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
        agent_textareas[step] = ui.textarea(label=f'{step.upper()} Output', value='').props('rows=10')
        ui.button(f'✅ Approve {step.upper()}', on_click=lambda s=step: approve_step(s))

# Supervisor HITL
with ui.expansion('🧠 Supervisor Decision Requires Human Approval', value=False):
    supervisor_panel = ui.textarea(label='Supervisor uncertainty - human decision required', value='').props('rows=4')
    ui.button('✅ Confirm Supervisor Decision', on_click=lambda: approve_step('supervisor'))

# Mermaid Diagram
with ui.expansion('📊 Requirement Diagram (Mermaid)', value=False):
    diagram_box = ui.textarea(label='Mermaid Diagram Code', value='').props('rows=15')

    def download_diagram():
        try:
            with open('generated/requirement_diagram.mmd', 'r') as f:
                content = f.read()
            ui.download(text=content, filename='requirement_diagram.mmd', mime_type='text/plain')
        except FileNotFoundError:
            append_log("[WARN] Mermaid diagram not found.")

    ui.button('📥 Download Mermaid Diagram', on_click=download_diagram)

# HITL Approval

def approve_step(step):
    try:
        requests.post('http://localhost:8000/approve-step', json={'step': step})
        approval_status[step] = True
        status_label.text = f'Status: {step.upper()} step approved.'
        status_badges[step].text = f"{step.upper()}: ✅ Approved"
        status_badges[step].props('color=green')
        append_log(f"✅ Approved: {step.upper()}")
        append_timeline(f"✅ {step.upper()} approved.")
    except Exception as e:
        append_log(f"[ERROR] Approval failed for {step}: {e}")
        append_timeline(f"❌ Approval error: {e}", error=True)

# Poll for Output Updates

async def fetch_outputs():
    try:
        for step in agent_textareas:
            file = f"generated/{step}_output.txt"
            if os.path.exists(file):
                content = open(file, 'r', encoding='utf-8').read()
                if content.strip():
                    agent_textareas[step].value = content
                    append_timeline(f"📥 {step.upper()} output loaded.")

        if os.path.exists("generated/requirement_diagram.mmd"):
            with open("generated/requirement_diagram.mmd", "r") as df:
                diagram_box.value = df.read()
                append_timeline("📊 Mermaid diagram loaded.")
    except Exception as e:
        append_log(f"[ERROR] While fetching outputs: {e}")
        append_timeline(f"❌ Fetching error: {e}", error=True)

# Run the app
ui.run()
