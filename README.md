# Multi Agent Powerhouse - AI Litigation Team

A working AI litigation team for pro se litigants, built according to your vision document.

## Features

### AI Team Members
- **Bob** - Your witty, patient AI companion who filters emotional content and keeps responses short
- **Coordinator** - Orchestrates the research → analysis → drafting workflow
- **Researcher** - Finds relevant statutes and case law
- **Statutory Analyst** - Applies rules of construction
- **Case Law Synthesizer** - Finds controlling precedent
- **Drafter** - Creates court-ready documents
- **Strategy Lead** - Produces litigation roadmap
- **Plain-Language Explainer** - Converts legalese to plain English
- **Compliance Reviewer** - Checks for sanction risks
- **Citation Auditor** - Verifies every citation

### Dashboard
- Case management with facts, violations, research, documents
- Evidence vault with upload and OCR
- Timeline with events
- AI team status

### Chat System
- Chat with Bob about your case
- Devil's Advocate mode for emotional/sensitive discussions
- Everything stays private in that tab

## Quick Start

1. Set your API key (optional but recommended for full functionality):
   ```bash
   export OPENAI_API_KEY=your_key_here
   # or
   export ANTHROPIC_API_KEY=your_key_here
   ```

2. Run the server:
   ```bash
   cd /workspace/project
   python3 -m uvicorn main:app --host 0.0.0.0 --port 8000
   ```

3. Access the dashboard at: http://localhost:8000/dashboard

## API Endpoints

- `GET /` - Health check
- `GET /dashboard` - Main dashboard
- `GET /dashboard/chat` - Chat with Bob
- `GET /dashboard/devil-advocate` - Devil's Advocate mode
- `GET /api/cases` - List all cases
- `POST /api/cases` - Create a new case
- `GET /api/agents` - List all AI agents
- `POST /api/chat/bob` - Chat with Bob

## Current Status

The system is running in **demo mode** without an API key. To enable full AI functionality:

1. Get an API key from OpenAI (https://platform.openai.com) or Anthropic (https://www.anthropic.com)
2. Set the environment variable
3. Restart the server

The AI agents will then be able to:
- Research statutes from official sources (statutes.capitol.texas.gov for Texas)
- Find case law from official court databases
- Draft court-ready documents
- Run compliance checks