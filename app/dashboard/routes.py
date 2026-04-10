from fastapi import APIRouter, Request, HTTPException
from fastapi.responses import HTMLResponse
from jinja2 import Environment, FileSystemLoader, select_autoescape
import os

router = APIRouter()

# Create a fresh Jinja2 environment for each request to avoid caching issues
def get_env():
    return Environment(
        loader=FileSystemLoader("/workspace/project/templates"),
        autoescape=select_autoescape(['html', 'xml'])
    )

@router.get("", response_class=HTMLResponse)
async def dashboard(request: Request):
    """Main dashboard page - Bob is front and center"""
    from main import cases_db, agents_db
    
    cases_list = [{"id": k, **v} for k, v in cases_db.items()]
    agents_list = [{"id": k, **v} for k, v in agents_db.items()]
    
    template = get_env().get_template("bob_home.html")
    return HTMLResponse(template.render(
        request=request,
        cases=cases_list,
        agents=agents_list
    ))

@router.get("/case/{case_id}", response_class=HTMLResponse)
async def case_detail(request: Request, case_id: str):
    """Case detail page"""
    from main import cases_db
    
    if case_id not in cases_db:
        raise HTTPException(status_code=404, detail="Case not found")
    
    template = get_env().get_template("case_detail.html")
    return HTMLResponse(template.render(
        request=request,
        case=cases_db[case_id],
        case_id=case_id
    ))

@router.get("/evidence", response_class=HTMLResponse)
async def evidence_vault(request: Request):
    """Evidence vault page"""
    template = get_env().get_template("evidence.html")
    return HTMLResponse(template.render(request=request))

@router.get("/research", response_class=HTMLResponse)
async def research_page(request: Request):
    """Research page"""
    template = get_env().get_template("research.html")
    return HTMLResponse(template.render(request=request))

@router.get("/documents", response_class=HTMLResponse)
async def documents_page(request: Request):
    """Documents page"""
    template = get_env().get_template("documents.html")
    return HTMLResponse(template.render(request=request))

@router.get("/chat", response_class=HTMLResponse)
async def chat_page(request: Request):
    """Chat with Bob"""
    template = get_env().get_template("chat.html")
    return HTMLResponse(template.render(request=request))

@router.get("/devil-advocate", response_class=HTMLResponse)
async def devil_advocate(request: Request):
    """Devil's Advocate - safe space for Ginny"""
    template = get_env().get_template("devil_advocate.html")
    return HTMLResponse(template.render(request=request))