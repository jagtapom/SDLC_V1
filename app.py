# app.py (NiceGUI Frontend with Barclays Logo, Status Badges, HITL UI)
from nicegui import ui
import requests

status_label = ui.label('Status: Waiting for document upload...')
log_box = ui.textarea(label='Logs', value='', rows=15)

approval_status = {'ba': False, 'jira': False, 'code': False, 'review': False, 'devops': False}
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
    except Exception as e:
        log_box.value += f"\nError: {str(e)}"
        status_label.text = 'Status: Failed to trigger.'

# HITL Panels
with ui.expansion('📋 BA Agent Output', value=True):
    ba_output = ui.textarea(label='Requirements Extracted', value='', rows=10)
    ui.button('✅ Approve BA Output', on_click=lambda: approve_step('ba'))

with ui.expansion('📌 JIRA Story Output', value=False):
    jira_output = ui.textarea(label='JIRA Story', value='', rows=10)
    ui.button('✅ Approve JIRA Story', on_click=lambda: approve_step('jira'))

with ui.expansion('🧠 Code Generation Output', value=False):
    code_output = ui.textarea(label='Generated Code', value='', rows=10)
    ui.button('✅ Approve Code', on_click=lambda: approve_step('code'))

with ui.expansion('🔍 Review Agent Feedback', value=False):
    review_output = ui.textarea(label='Review Comments', value='', rows=10)
    ui.button('✅ Approve Review', on_click=lambda: approve_step('review'))

with ui.expansion('🔧 DevOps Pipeline Output', value=False):
    devops_output = ui.textarea(label='GitLab CI/CD YAML', value='', rows=10)
    ui.button('✅ Approve DevOps Pipeline', on_click=lambda: approve_step('devops'))

def approve_step(step):
    try:
        requests.post('http://localhost:8000/approve-step', json={'step': step})
        approval_status[step] = True
        status_label.text = f'Status: {step.upper()} step approved.'
        status_badges[step].text = f"{step.upper()}: ✅ Approved"
        status_badges[step].props('color=green')
    except Exception as e:
        log_box.value += f"\n[ERROR] Approving {step}: {e}"

ui.run()
