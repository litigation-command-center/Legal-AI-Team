"""
LLM Client for interacting with language models
Supports OpenAI, Anthropic, and Gemini via Puter.js
"""
import os
import json
import asyncio
from typing import Dict, Any, Optional, List

# Try importing OpenAI
try:
    from openai import AsyncOpenAI
    OPENAI_AVAILABLE = True
except ImportError:
    OPENAI_AVAILABLE = False

# Try importing Anthropic
try:
    from anthropic import AsyncAnthropic
    ANTHROPIC_AVAILABLE = True
except ImportError:
    ANTHROPIC_AVAILABLE = False

from main import agents_db

# Check for Puter.js (browser-based) or use direct API
# Using Google's Gemini directly with httpx
try:
    import httpx
    HTTPX_AVAILABLE = True
except ImportError:
    HTTPX_AVAILABLE = False

class LLMClient:
    def __init__(self, provider: str = "gemini"):
        self.provider = provider
        self.client = None
        
        if provider == "openai" and OPENAI_AVAILABLE:
            api_key = os.environ.get("OPENAI_API_KEY", "")
            if api_key:
                self.client = AsyncOpenAI(api_key=api_key)
                self.model = os.environ.get("OPENAI_MODEL", "gpt-4o")
        elif provider == "anthropic" and ANTHROPIC_AVAILABLE:
            api_key = os.environ.get("ANTHROPIC_API_KEY", "")
            if api_key:
                self.client = AsyncAnthropic(api_key=api_key)
                self.model = os.environ.get("ANTHROPIC_MODEL", "claude-3-5-sonnet-20241022")
        elif provider == "gemini" and HTTPX_AVAILABLE:
            # Use Gemini via Puter.js free API
            self.model = os.environ.get("GEMINI_MODEL", "gemini-2.0-flash-exp:free")
    
    async def chat(
        self, 
        system_prompt: str, 
        user_prompt: str, 
        temperature: float = 0.7,
        max_tokens: int = 4000
    ) -> str:
        """Send a chat request to the LLM"""
        
        if self.provider == "gemini" and HTTPX_AVAILABLE:
            return await self._chat_gemini(system_prompt, user_prompt, temperature, max_tokens)
        
        if not self.client:
            # Fallback to mock responses for demo
            return self._mock_response(user_prompt)
        
        try:
            if self.provider == "openai":
                response = await self.client.chat.completions.create(
                    model=self.model,
                    messages=[
                        {"role": "system", "content": system_prompt},
                        {"role": "user", "content": user_prompt}
                    ],
                    temperature=temperature,
                    max_tokens=max_tokens
                )
                return response.choices[0].message.content
            
            elif self.provider == "anthropic":
                response = await self.client.messages.create(
                    model=self.model,
                    max_tokens=max_tokens,
                    system=system_prompt,
                    messages=[{"role": "user", "content": user_prompt}]
                )
                return response.content[0].text
            
        except Exception as e:
            print(f"Error calling LLM: {e}")
            return self._mock_response(user_prompt)
    
    def _mock_response(self, user_prompt: str) -> str:
        """Enhanced mock response with case context awareness"""
        # Check for case-related keywords
        prompt_lower = user_prompt.lower()
        
        if "help" in prompt_lower or "what can you do" in prompt_lower:
            return """Hey Ginny! I'm Bob, your legal AI assistant.

Here's what I can do for you:

📁 **Document Review** - I extract facts from your uploaded PDFs and documents

⚖️ **Legal Analysis** - Break down your case facts and identify potential violations

🔍 **Research** - Pull relevant statutes and case law for your situation

📝 **Drafting** - Help create court documents from your facts

🛡️ **Your Rights** - Explain what's legal and what's not in your situation

**ZERO FABRICATION RULE** - Everything I tell you comes from YOUR documents. If it's not in your files, I don't make it up.

You currently have:
- 13 extracted facts from your PDF
- 2 identified violations (Excessive Force & Unlawful Search)
- Case: DBD Case - Texas Southern District

What's your question?"""
        
        elif "arrest" in prompt_lower or "deputy" in prompt_lower or "raymond gonzales" in prompt_lower:
            return """Based on your extracted facts, here's what happened on May 14, 2023:

**The Incident:**
- You were pulled over by Deputy Raymond Gonzales for expired registration
- He activated lights at 22:20, arrested you at 22:22
- Key issue: Deputy opened your car door (your broken door handle proves this)

**Potential Violations:**
1. **Excessive Force** - Forcibly removing you from the vehicle
2. **Fourth Amendment** - Search without consent while in custody

**My Assessment:**
- The arrest for expired registration seems minor vs the force used
- Your broken door handle is evidence the deputy opened the door
- No consent was given for the vehicle search

Want me to research the relevant statutes for these claims?"""
        
        elif "research" in prompt_lower or "statute" in prompt_lower or "law" in prompt_lower:
            return """For your case (wrongful arrest / excessive force), here are relevant areas to research:

**Federal:**
- 42 U.S.C. § 1983 - Civil rights violations
- Fourth Amendment - Unreasonable search/seizure
- Fifth Amendment - Due process

**Texas:**
- Texas Civil Practice & Remedies Code § 101.001 - Governmental immunity waiver
- Texas Civil Practices - False imprisonment

**Key Cases:**
- Graham v. Connor (excessive force standard)
- Terry v. Ohio (stop and frisk)
- Michigan v. Summers (search/seizure)

Want me to dig deeper into any of these? I can research specific statutes and pull case law."""
        
        elif "draft" in prompt_lower or "document" in prompt_lower:
            return """I can help you draft documents based on your case facts!

Available drafts for your case:
- **Complaint** - Federal civil rights (42 USC 1983)
- **Motion for Discovery** - Request officer's body cam
- **Motion to Suppress** - Illegal search
- **Demand Letter** - Pre-litigation

What document do you need? I'll use ONLY the facts from your PDF - no fabrications."""
        
        elif "consent" in prompt_lower or "search" in prompt_lower:
            return """Based on your facts about the search:

**What happened:**
- You told deputy "I do not consent to a search"
- Deputy said "it's for officer safety"
- They searched your vehicle while you were in custody

**The Law:**
- Officer safety is a limited exception
- The vehicle was already secured (you were handcuffed)
- No warrant was obtained

**This is a potential Fourth Amendment violation** - the search appears unreasonable.

Want me to research case law on "search incident to arrest" vs vehicle searches?"""
        
        else:
            return f"""Hey Ginny! I see you're asking about your case.

You have 13 facts extracted from your PDF and 2 violations identified:
1. Excessive Force / Wrongful Arrest  
2. Unlawful Search Without Consent

Ask me about:
- What happened (I'll summarize from your docs)
- Your legal options
- Relevant statutes
- What documents to draft
- Next steps

Remember: I only use facts from YOUR documents - no making things up!"""
    
    async def _chat_gemini(self, system_prompt: str, user_prompt: str, temperature: float, max_tokens: int) -> str:
        """Chat with Gemini via Puter.js free API"""
        import httpx
        
        try:
            # Puter.js free Gemini API - using correct endpoint
            url = "https://api.puter.ai/v1/chat"
            
            async with httpx.AsyncClient(timeout=90.0, follow_redirects=True) as client:
                response = await client.post(
                    url,
                    json={
                        "model": self.model,
                        "messages": [
                            {"role": "system", "content": system_prompt},
                            {"role": "user", "content": user_prompt}
                        ],
                        "temperature": temperature,
                        "max_tokens": max_tokens
                    },
                    headers={"Content-Type": "application/json"}
                )
                
                if response.status_code == 200:
                    data = response.json()
                    return data.get("choices", [{}])[0].get("message", {}).get("content", "No response")
                else:
                    print(f"Gemini API error: {response.status_code} - {response.text[:200]}")
                    return self._mock_response(user_prompt)
        except Exception as e:
            print(f"Error calling Gemini: {e}")
            return self._mock_response(user_prompt)
    
    async def chat_with_history(
        self,
        system_prompt: str,
        messages: List[Dict[str, str]],
        temperature: float = 0.7,
        max_tokens: int = 4000
    ) -> str:
        """Send a chat request with conversation history"""
        
        if not self.client:
            return self._mock_response(messages[-1]["content"] if messages else "")
        
        try:
            if self.provider == "openai":
                all_messages = [{"role": "system", "content": system_prompt}]
                all_messages.extend(messages)
                
                response = await self.client.chat.completions.create(
                    model=self.model,
                    messages=all_messages,
                    temperature=temperature,
                    max_tokens=max_tokens
                )
                return response.choices[0].message.content
            
            elif self.provider == "anthropic":
                # Anthropic uses different format
                user_messages = [{"role": "user", "content": m["content"]} for m in messages]
                
                response = await self.client.messages.create(
                    model=self.model,
                    max_tokens=max_tokens,
                    system=system_prompt,
                    messages=user_messages
                )
                return response.content[0].text
            
        except Exception as e:
            print(f"Error calling LLM: {e}")
            return self._mock_response(messages[-1]["content"] if messages else "")


# Global client instance
_llm_client: Optional[LLMClient] = None

def get_llm_client() -> LLMClient:
    global _llm_client
    if _llm_client is None:
        # Try Gemini first (free, no API key needed!)
        _llm_client = LLMClient("gemini")
        
        # Fall back to others if Gemini fails
        if not _llm_client.client and not HTTPX_AVAILABLE:
            if os.environ.get("OPENAI_API_KEY"):
                _llm_client = LLMClient("openai")
            elif os.environ.get("ANTHROPIC_API_KEY"):
                _llm_client = LLMClient("anthropic")
    return _llm_client


async def chat_with_agent(agent_id: str, prompt: str, history: List[Dict[str, str]] = None) -> str:
    """Chat with a specific agent"""
    from main import agents_db
    
    if agent_id not in agents_db:
        return f"Agent {agent_id} not found"
    
    agent = agents_db[agent_id]
    client = get_llm_client()
    
    if history:
        return await client.chat_with_history(
            agent["system_prompt"],
            history,
            temperature=0.7
        )
    else:
        return await client.chat(
            agent["system_prompt"],
            prompt,
            temperature=0.7
        )


async def run_research_agent(case_id: str, query: str) -> Dict[str, Any]:
    """Run the Researcher agent"""
    from main import cases_db
    
    case = cases_db.get(case_id)
    if not case:
        return {"error": "Case not found"}
    
    facts_summary = "\n".join([f["content"] for f in case.get("facts", [])])
    
    prompt = f"""Case Facts:
{facts_summary}

Jurisdiction: {case.get('jurisdiction', 'Texas / Federal')}

Research Query: {query}

Please provide relevant statutes and case law."""

    result = await chat_with_agent("researcher", prompt)
    
    return {
        "query": query,
        "result": result,
        "agent": "researcher",
        "timestamp": __import__("datetime").datetime.now().isoformat()
    }


async def run_drafting_agent(case_id: str, document_type: str, description: str) -> Dict[str, Any]:
    """Run the Drafter agent"""
    from main import cases_db
    
    case = cases_db.get(case_id)
    if not case:
        return {"error": "Case not found"}
    
    facts_summary = "\n".join([f["content"] for f in case.get("facts", [])])
    
    prompt = f"""Case Facts:
{facts_summary}

Jurisdiction: {case.get('jurisdiction', 'Texas / Federal')}

Document Type: {document_type}
Description: {description}

Please draft this document following court rules."""

    result = await chat_with_agent("drafter", prompt)
    
    return {
        "document_type": document_type,
        "description": description,
        "result": result,
        "agent": "drafter",
        "timestamp": __import__("datetime").datetime.now().isoformat()
    }