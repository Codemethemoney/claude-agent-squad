import os
import json
import hashlib
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import List
import openai
from dotenv import load_dotenv

load_dotenv()

app = FastAPI(title="Agent Spec Generator", version="1.0.0")

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

CACHE_DIR = os.getenv("CACHE_DIR", "../agent_cache")
os.makedirs(CACHE_DIR, exist_ok=True)

# Initialize OpenAI client
client = openai.OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

class Spec(BaseModel):
    name: str
    role_description: str
    tools: List[str]

class GeneratedSpec(BaseModel):
    persona: str
    system_prompt: str
    agent_md: str

async def call_llm(prompt: str) -> str:
    """Call OpenAI API to generate agent specifications"""
    try:
        response = client.chat.completions.create(
            model="gpt-4",
            messages=[
                {"role": "system", "content": "You are an expert prompt generator following semantic engineering principles."},
                {"role": "user", "content": prompt}
            ],
            temperature=0.7,
            max_tokens=2000
        )
        return response.choices[0].message.content
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"LLM call failed: {str(e)}")

@app.post("/generate_agent", response_model=GeneratedSpec)
async def gen_agent(spec: Spec):
    """Generate agent specifications with caching"""
    # Create cache key from spec
    spec_dict = spec.dict()
    key = hashlib.sha256(json.dumps(spec_dict, sort_keys=True).encode()).hexdigest()
    cache_path = os.path.join(CACHE_DIR, f"{spec.name}_{key}.json")
    
    # Check cache first
    if os.path.exists(cache_path):
        with open(cache_path, 'r') as f:
            return GeneratedSpec(**json.load(f))
    
    # Generate prompt following semantic principles
    prompt = f"""
    You are an expert prompt generator applying semantic engineering principles.
    
    Generate specifications for an AI agent with these requirements:
    - Agent Name: {spec.name}
    - Role: {spec.role_description}
    - Available Tools: {', '.join(spec.tools)}
    
    Apply these principles:
    1. **Lexical Density**: Use precise, information-dense wording
    2. **Semantic Gravity**: Balance context-dependence with abstraction
    3. **Semantic Prosody**: Maintain appropriate tone and connotation
    
    Produce a JSON response with exactly these fields:
    {{
        "persona": "A 2-3 sentence character description capturing the agent's expertise and approach",
        "system_prompt": "A comprehensive system prompt defining the agent's behavior, constraints, and tool usage patterns",
        "agent_md": "A markdown specification document describing the agent's capabilities, workflows, and best practices"
    }}
    
    Ensure the system_prompt explicitly references available tools and defines clear decision boundaries.
    """
    
    # Get LLM response
    llm_response = await call_llm(prompt)
    
    # Parse JSON response
    try:
        # Clean up response if needed
        if llm_response.startswith("```json"):
            llm_response = llm_response[7:]
        if llm_response.endswith("```"):
            llm_response = llm_response[:-3]
        
        payload = json.loads(llm_response.strip())
        
        # Validate required fields
        if not all(key in payload for key in ["persona", "system_prompt", "agent_md"]):
            raise ValueError("Missing required fields in LLM response")
            
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Invalid JSON from LLM: {str(e)}")
    
    # Cache the result
    with open(cache_path, 'w') as f:
        json.dump(payload, f, indent=2)
    
    return GeneratedSpec(**payload)

@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {"status": "healthy", "service": "spec-generator"}

if __name__ == "__main__":
    import uvicorn
    port = int(os.getenv("GENERATOR_PORT", 8001))
    uvicorn.run(app, host="0.0.0.0", port=port)
