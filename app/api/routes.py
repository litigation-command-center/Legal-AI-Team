from fastapi import APIRouter, HTTPException, UploadFile, File, BackgroundTasks
from pydantic import BaseModel
from typing import List, Optional, Dict, Any
from datetime import datetime
import uuid
import json
import os

router = APIRouter()

# Case models
class CaseCreate(BaseModel):
    title: str
    jurisdiction: str = "Texas Southern District - Galveston Division"
    description: Optional[str] = ""

class CaseUpdate(BaseModel):
    title: Optional[str] = None
    description: Optional[str] = None
    status: Optional[str] = None

class FactCreate(BaseModel):
    case_id: str
    content: str
    source_evidence_id: Optional[str] = None
    verified: bool = False

class ViolationCreate(BaseModel):
    case_id: str
    title: str
    description: str
    incident_date: Optional[str] = None
    suggested_statute: Optional[str] = None

class ResearchRequest(BaseModel):
    case_id: str
    query: str
    violation_id: Optional[str] = None

class DraftRequest(BaseModel):
    case_id: str
    document_type: str
    description: str

class ChatMessage(BaseModel):
    message: str
    case_id: Optional[str] = None

# Evidence storage - defined here for now (will be moved to main)
_evidence_db: Dict[str, Any] = {}

def get_evidence_db():
    return _evidence_db

# Chat history storage
_chat_histories: Dict[str, List[Dict[str, str]]] = {}

@router.get("/cases")
async def list_cases():
    """List all cases"""
    from main import cases_db
    return [{"id": k, **v} for k, v in cases_db.items()]

@router.post("/cases")
async def create_case(case: CaseCreate):
    """Create a new case"""
    from main import cases_db
    
    case_id = f"CASE-{datetime.now().strftime('%Y%m%d')}-{str(uuid.uuid4())[:8]}"
    case_data = {
        "id": case_id,
        "title": case.title,
        "description": case.description,
        "jurisdiction": case.jurisdiction,
        "status": "active",
        "created_at": datetime.now().isoformat(),
        "updated_at": datetime.now().isoformat(),
        "facts": [],
        "violations": [],
        "research_results": [],
        "documents": []
    }
    cases_db[case_id] = case_data
    return case_data

@router.get("/cases/{case_id}")
async def get_case(case_id: str):
    """Get case by ID"""
    from main import cases_db
    if case_id not in cases_db:
        raise HTTPException(status_code=404, detail="Case not found")
    return cases_db[case_id]

@router.put("/cases/{case_id}")
async def update_case(case_id: str, case: CaseUpdate):
    """Update case"""
    from main import cases_db
    if case_id not in cases_db:
        raise HTTPException(status_code=404, detail="Case not found")
    
    if case.title:
        cases_db[case_id]["title"] = case.title
    if case.description:
        cases_db[case_id]["description"] = case.description
    if case.status:
        cases_db[case_id]["status"] = case.status
    cases_db[case_id]["updated_at"] = datetime.now().isoformat()
    
    return cases_db[case_id]

@router.delete("/cases/{case_id}")
async def delete_case(case_id: str):
    """Delete case"""
    from main import cases_db
    if case_id not in cases_db:
        raise HTTPException(status_code=404, detail="Case not found")
    del cases_db[case_id]
    return {"message": "Case deleted"}

# Facts endpoints
@router.post("/cases/{case_id}/facts")
async def add_fact(case_id: str, fact: FactCreate):
    """Add a fact to a case"""
    from main import cases_db
    if case_id not in cases_db:
        raise HTTPException(status_code=404, detail="Case not found")
    
    fact_id = f"FACT-{str(uuid.uuid4())[:8]}"
    fact_data = {
        "id": fact_id,
        "content": fact.content,
        "source_evidence_id": fact.source_evidence_id,
        "verified": fact.verified,
        "created_at": datetime.now().isoformat()
    }
    cases_db[case_id]["facts"].append(fact_data)
    return fact_data

@router.get("/cases/{case_id}/facts")
async def list_facts(case_id: str):
    """List all facts for a case"""
    from main import cases_db
    if case_id not in cases_db:
        raise HTTPException(status_code=404, detail="Case not found")
    return cases_db[case_id]["facts"]

# Evidence endpoints
@router.post("/cases/{case_id}/evidence")
async def upload_evidence(case_id: str, background_tasks: BackgroundTasks, file: UploadFile = File(...)):
    """Upload evidence to a case"""
    from main import cases_db
    
    if case_id not in cases_db:
        raise HTTPException(status_code=404, detail="Case not found")
    
    # Save file
    evidence_id = f"EVID-{datetime.now().strftime('%Y%m%d')}-{str(uuid.uuid4())[:8]}"
    upload_dir = f"/workspace/project/uploads/{case_id}"
    os.makedirs(upload_dir, exist_ok=True)
    
    file_path = f"{upload_dir}/{evidence_id}_{file.filename}"
    with open(file_path, "wb") as f:
        content = await file.read()
        f.write(content)
    
    evidence_data = {
        "id": evidence_id,
        "filename": file.filename,
        "file_path": file_path,
        "uploaded_at": datetime.now().isoformat(),
        "case_id": case_id,
        "ocr_text": None,
        "entities": [],
        "redacted": False
    }
    
    get_evidence_db()[evidence_id] = evidence_data
    return evidence_data

@router.get("/cases/{case_id}/evidence")
async def list_evidence(case_id: str):
    """List all evidence for a case"""
    return [e for e in get_evidence_db().values() if e["case_id"] == case_id]

# Violations endpoints
@router.post("/cases/{case_id}/violations")
async def add_violation(case_id: str, violation: ViolationCreate):
    """Add a violation to a case"""
    from main import cases_db
    if case_id not in cases_db:
        raise HTTPException(status_code=404, detail="Case not found")
    
    violation_id = f"VIOL-{str(uuid.uuid4())[:8]}"
    violation_data = {
        "id": violation_id,
        "title": violation.title,
        "description": violation.description,
        "incident_date": violation.incident_date,
        "suggested_statute": violation.suggested_statute,
        "research_status": "pending",
        "created_at": datetime.now().isoformat()
    }
    cases_db[case_id]["violations"].append(violation_data)
    return violation_data

@router.get("/cases/{case_id}/violations")
async def list_violations(case_id: str):
    """List all violations for a case"""
    from main import cases_db
    if case_id not in cases_db:
        raise HTTPException(status_code=404, detail="Case not found")
    return cases_db[case_id]["violations"]

# Research endpoints
@router.post("/cases/{case_id}/research")
async def request_research(case_id: str, request: ResearchRequest):
    """Request research for a case"""
    from main import cases_db
    if case_id not in cases_db:
        raise HTTPException(status_code=404, detail="Case not found")
    
    research_id = f"RES-{str(uuid.uuid4())[:8]}"
    research_data = {
        "id": research_id,
        "query": request.query,
        "violation_id": request.violation_id,
        "status": "queued",
        "created_at": datetime.now().isoformat(),
        "results": []
    }
    cases_db[case_id]["research_results"].append(research_data)
    return research_data

# Documents endpoints
@router.get("/cases/{case_id}/documents")
async def list_documents(case_id: str):
    """List all documents for a case"""
    from main import cases_db
    if case_id not in cases_db:
        raise HTTPException(status_code=404, detail="Case not found")
    return cases_db[case_id].get("documents", [])

# Agents endpoints
@router.get("/agents")
async def list_agents():
    """List all available agents"""
    from main import agents_db
    return list(agents_db.values())

@router.get("/agents/{agent_id}")
async def get_agent(agent_id: str):
    """Get agent details"""
    from main import agents_db
    if agent_id not in agents_db:
        raise HTTPException(status_code=404, detail="Agent not found")
    return agents_db[agent_id]

# Chat with Bob
@router.post("/chat/bob")
async def chat_with_bob(chat: ChatMessage):
    """Chat with Bob AI assistant"""
    from main import agents_db, cases_db
    from app.agents.llm_client import chat_with_agent
    
    # Get case context if provided
    context = ""
    case_id = chat.case_id
    if case_id and case_id in cases_db:
        case = cases_db[case_id]
        context = f"Case: {case['title']}\nJurisdiction: {case['jurisdiction']}\n"
        if case.get('facts'):
            context += "Facts:\n" + "\n".join([f["content"] for f in case['facts'][:5]]) + "\n"
    
    full_prompt = f"{agents_db['bob']['system_prompt']}\n\nContext:\n{context}\n\nGinny says: {chat.message}"
    
    response = await chat_with_agent("bob", full_prompt)
    return {"response": response}

# Get chat history
@router.get("/chat/history/{case_id}")
async def get_chat_history(case_id: str):
    """Get chat history for a case"""
    return _chat_histories.get(case_id, [])

# Clear chat history
@router.delete("/chat/history/{case_id}")
async def clear_chat_history(case_id: str):
    """Clear chat history for a case"""
    if case_id in _chat_histories:
        del _chat_histories[case_id]
    return {"message": "Chat history cleared"}