from fastapi import FastAPI
from pydantic import BaseModel
from fastapi.middleware.cors import CORSMiddleware
import asyncio
from src.orchestrator import run_workflow_async, pass_approval

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

class DocumentInput(BaseModel):
    file_path: str
    keyword: str | None = None

@app.post("/start-workflow")
async def start(payload: DocumentInput):
    asyncio.create_task(run_workflow_async(payload.file_path, payload.keyword))
    return {"message": "✅ Workflow started with uploaded document."}

class ApprovalPayload(BaseModel):
    step: str

@app.post("/approve-step")
async def approve_step(payload: ApprovalPayload):
    step = payload.step.lower()
    pass_approval(step)
    return {"message": f"✅ Approval received for {step}"}
