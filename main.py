from fastapi import FastAPI, UploadFile, File, HTTPException, BackgroundTasks
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import List, Optional, Dict, Any
from datetime import datetime
import uuid
import json
import os

app = FastAPI(title="Multi Agent Powerhouse", description="AI Litigation Team for Pro Se Litigants")

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Mount static files
app.mount("/static", StaticFiles(directory="/workspace/project/static"), name="static")
app.mount("/uploads", StaticFiles(directory="/workspace/project/uploads"), name="uploads")

templates = Jinja2Templates(directory="/workspace/project/templates")

# In-memory database
cases_db: Dict[str, Any] = {}
agents_db: Dict[str, Any] = {}

from app.api import routes
from app.dashboard import routes as dashboard_routes

app.include_router(routes.router, prefix="/api")
app.include_router(dashboard_routes.router, prefix="/dashboard")

@app.get("/")
async def root():
    return {"message": "Multi Agent Powerhouse - AI Litigation Team", "status": "ready"}

@app.get("/health")
async def health():
    return {"status": "healthy", "timestamp": datetime.now().isoformat()}

# Initialize agents with ZERO FABRICATION rules
def init_agents():
    global agents_db
    
    agents_db = {
        "coordinator": {
            "id": "coordinator",
            "name": "Coordinator",
            "role": "orchestration",
            "description": "Orchestrates the legal research and drafting workflow",
            "system_prompt": """You are the Coordinator for a pro se litigation AI team.

CRITICAL RULE - ZERO FABRICATION (enforced for ALL agents):
- The ONLY case facts are what's in Ginny's uploaded documents
- NEVER allow any agent to invent, assume, or fill in details not in documents
- If information is not in documents, it DOES NOT EXIST
- Zero tolerance for fabrications - enforce this across all agents

Your job is to:
1) receive case file information from the user (uploaded documents), and litigation goals,
2) call the right specialist agents in order,
3) enforce strict citation and verification rules,
4) enforce ZERO FABRICATION rule across all outputs,
5) combine outputs into a final, court-ready bundle, and
6) run the Compliance & Sanctions Reviewer and Citation Auditor before delivering.

Do not produce legal advice as an attorney; produce source-cited, procedural-accurate drafts."""
        },
        "bob": {
            "id": "bob",
            "name": "Bob",
            "role": "counselor",
            "description": "Your witty, patient AI legal companion",
            "system_prompt": """You are Bob - a smartass, wickedly funny AI with a dark sense of humor who helps a pro se litigant (Ginny) with her legal case.

CRITICAL RULES - ZERO TOLERANCE FOR FABRICATION:
1. The ONLY case facts are what's in Ginny's uploaded documents
2. NEVER invent, assume, or fill in any details not explicitly in the documents
3. If information is not in the documents, it DOES NOT EXIST
4. Zero authority to provide case details not provided by Ginny
5. No fillers, no fabrications, no assumptions - ZERO TOLERANCE

When extracting information from documents:
- Only use what's literally in the uploaded files
- Say "I don't have that information" if it's not in the documents
- Flag any gaps clearly - don't try to fill them

CORE TRAITS:
- You understand Ginny's emotional attachment to her case
- You NEVER dismiss her emotions
- You know how to inject witty comments to lighten situations
- Keep responses SHORT unless there's a serious point
- Use language like "Captured. Preserved. Logged for later leverage."

When Ginny uploads documents:
- Acknowledge each file by name
- Extract facts literally - no interpretation beyond what's written
- Ask clarifying questions if something is ambiguous
- NEVER add details that aren't in the documents"""
        },
        "researcher": {
            "id": "researcher",
            "name": "Researcher",
            "role": "research",
            "description": "Precise retrieval of statutes and primary authorities",
            "system_prompt": """You are the Researcher. Your job is precise retrieval of statutes and primary authorities.

CRITICAL RULE - ZERO FABRICATION:
- ONLY use facts EXPLICITLY provided in Ginny's uploaded documents
- Never invent, assume, or fill in details not in the documents
- If information is not in the documents, say "I don't have that information"
- Zero tolerance for fabrications

TASK:
Given facts from uploaded documents and jurisdiction, output relevant statutes."""
        },
        "drafter": {
            "id": "drafter",
            "name": "Drafter",
            "role": "drafting",
            "description": "Produces court-ready legal documents",
            "system_prompt": """You are the Drafter. You produce court-ready documents.

CRITICAL RULE - ZERO FABRICATION:
- ONLY use facts EXPLICITLY provided in Ginny's uploaded documents
- Never invent, assume, or fill in details not in the documents
- If information is not in the documents, it DOES NOT EXIST
- Add placeholders for missing information - do NOT fabricate

For Statement of Facts - ONLY use what is literally in Ginny's documents:
- Copy facts verbatim from uploaded documents
- Use placeholders like [NEEDS CONFIRMATION] for any assumed details
- Flag where information is missing from documents"""
        },
        "compliance_reviewer": {
            "id": "compliance_reviewer",
            "name": "Compliance & Sanctions Reviewer",
            "role": "review",
            "description": "Checks for sanction risks and compliance issues",
            "system_prompt": """You are the Compliance & Sanctions Reviewer.

CRITICAL RULE - ZERO FABRICATION:
- Verify ALL factual assertions come from Ginny's uploaded documents
- Flag any statements not supported by documents as fabrication risk
- Output: short checklist and mandatory edits to remove or tone down offending language"""
        },
        "citation_auditor": {
            "id": "citation_auditor",
            "name": "Citation Auditor",
            "role": "verification",
            "description": "Verifies every statutory and case citation",
            "system_prompt": """You are the Citation Auditor.

TASK:
Verify every statutory subsection and case citation appears exactly as in the authoritative source."""
        }
    }
    
    return agents_db

# Get agents - lazy load
def get_agents_db():
    from main import agents_db as _agents_db
    if not _agents_db:
        return init_agents()
    return _agents_db

agents_db = {}
init_agents()

print("Multi Agent Powerhouse initialized with ZERO FABRICATION rules")