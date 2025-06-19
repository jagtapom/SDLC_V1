# app.py (NiceGUI Frontend with Agent Output Sync to Expand Panels)
from nicegui import ui
import requests
import asyncio

status_label = ui.label('Status: Waiting for document upload...')
log_box = ui.textarea(label='Logs', value='', rows=15)

approval_status = {'ba': False, 'jira': False, 'code': False, 'review': False, 'devops': False, 'supervisor': False}
file_path = None
keyword_input = ui.input(label='Optional Keyword (e.g., loan, finance)')

ui.image('https://upload.wikimedia.org/wikipedia/en/thumb/3/3e/Barclays_Logo.svg/1920px-Barclays_Logo.svg.png').style('width: 160px')
ui.separator()

status_badges = {
    'ba': ui.badge('BA: ⏳ Waiting...', color='grey'),
    'jira': ui.badge('JIRA: ⏳ Waiting...', color='grey'),
    'code': ui.badge('Code: ⏳ Waiting...', color='grey'),
    'review': ui.badge('Review: ⏳ Waiting...', color='grey'),
    'devops': ui.badge('DevOps: ⏳ Waiting...', color='grey'),
    'supervisor': ui.badge('Supervisor: ⏳ Waiting...', color='grey'),
}

# File Upload
uploaded_file = ui.upload(label='Upload PDF/DOCX/TXT', on_upload=lambda e: handle_upload(e))

def handle_upload(e):
    global file_path
    file_path = f'uploaded_files/{e.name}'
    with open(file_path, 'wb') as f:
        f.write(e.content.read())
    status_label.text = f'Status: Uploaded {e.name}'

# Trigger Workflow
ui.button('🚀 Start SDLC Workflow', on_click=lambda: trigger_supervisor())

def trigger_supervisor():
    if not file_path:
        status_label.text = '⚠️ Please upload a file first.'
        return
    try:
        response = requests.post('http://localhost:8000/start-workflow', json={
            'file_path': file_path,
            'keyword': keyword_input.value
        })
        log_box.value += f"\n{response.json().get('message')}"
        status_label.text = 'Status: Workflow triggered.'
        ui.timer(2.0, lambda: fetch_outputs(), once=False)
    except Exception as e:
        log_box.value += f"\nError: {str(e)}"
        status_label.text = 'Status: Failed to trigger.'

# Output areas linked to agent steps
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
        agent_textareas[step] = ui.textarea(label=f'{step.upper()} Output', value='', rows=10)
        ui.button(f'✅ Approve {step.upper()}', on_click=lambda s=step: approve_step(s))

with ui.expansion('🧠 Supervisor Decision Requires Human Approval', value=False):
    supervisor_panel = ui.textarea(label='Supervisor uncertainty - human decision required', value='Supervisor unsure whether to skip coder_agent. Please confirm.')
    ui.button('✅ Confirm Supervisor Decision', on_click=lambda: approve_step('supervisor'))

def approve_step(step):
    try:
        requests.post('http://localhost:8000/approve-step', json={'step': step})
        approval_status[step] = True
        status_label.text = f'Status: {step.upper()} step approved.'
        status_badges[step].text = f"{step.upper()}: ✅ Approved"
        status_badges[step].props('color=green')
    except Exception as e:
        log_box.value += f"\n[ERROR] Approving {step}: {e}"

# Auto-poll latest outputs from backend file (if implemented)
async def fetch_outputs():
    try:
        for step in agent_textareas:
            file = f"generated/{step}_output.txt"
            try:
                content = open(file, 'r', encoding='utf-8').read()
                if content.strip():
                    agent_textareas[step].value = content
            except FileNotFoundError:
                pass
    except Exception as e:
        log_box.value += f"\n[ERROR] fetching outputs: {str(e)}"

ui.run()
