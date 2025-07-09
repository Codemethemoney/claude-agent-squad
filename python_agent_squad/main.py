import os
import json
import httpx
import logging
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import List, Dict, Optional, Any
from dotenv import load_dotenv
import asyncio
from datetime import datetime
from agent_squad import ClaudeAgent, AgentSquad, SupervisorAgent as BaseSupAgent

load_dotenv()

app = FastAPI(title="Agent Squad API", version="1.0.0")

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Agent Squad configuration
AGENT_MODELS = {
    "Researcher": os.getenv("RESEARCHER_MODEL", "claude-3-sonnet-20240229"),
    "Writer": os.getenv("WRITER_MODEL", "claude-3-opus-20240229"),
    "Coder": os.getenv("CODER_MODEL", "claude-3-haiku-20240307")
}

# Squad instance using agent_squad library
squad = AgentSquad()

class SpecValidationError(Exception):
    """Raised when agent spec validation fails"""
    pass

class AgentCreationError(Exception):
    """Raised when agent creation fails"""
    pass

class AgentConfig(BaseModel):
    name: str
    role: str
    tools: List[str]

class Request(BaseModel):
    query: str
    session_id: str = "default"

async def add_agent_with_profile(
    name: str, 
    role: str, 
    tools: List[str],
    api_key: Optional[str] = None,
    model: Optional[str] = None
) -> Dict[str, Any]:
    """
    Add an agent to the squad with complete profile generation and error handling.
    
    Args:
        name: Agent name
        role: Agent role description
        tools: List of tool names the agent can use
        api_key: Optional API key override for this agent
        model: Optional model override for this agent
    
    Returns:
        Dict containing agent creation status and details
    
    Raises:
        AgentCreationError: If agent creation fails after retries
    """
    logger.info(f"Creating agent profile for {name}")
    
    # Determine API key and model
    if not api_key:
        api_key = os.getenv(f"OPENAI_API_KEY_{name.upper()}", os.getenv("OPENAI_API_KEY"))
    if not api_key:
        raise AgentCreationError(f"No API key available for agent {name}")
    
    if not model:
        model = AGENT_MODELS.get(name, "claude-3-sonnet-20240229")
    
    # Fetch or generate spec with retries
    spec = None
    generator_url = f"http://localhost:{os.getenv('GENERATOR_PORT', 8001)}/generate_agent"
    
    for attempt in range(3):
        try:
            async with httpx.AsyncClient(timeout=30.0) as client:
                logger.info(f"Fetching spec from generator (attempt {attempt + 1}/3)")
                response = await client.post(
                    generator_url,
                    json={"name": name, "role_description": role, "tools": tools}
                )
                response.raise_for_status()
                spec = response.json()
                
                # Validate spec structure
                required_keys = ["persona", "system_prompt", "agent_md"]
                missing_keys = [k for k in required_keys if k not in spec]
                if missing_keys:
                    raise SpecValidationError(f"Missing required spec keys: {missing_keys}")
                
                # Validate spec content
                if not all(isinstance(spec[k], str) and spec[k].strip() for k in required_keys):
                    raise SpecValidationError("Spec contains empty or invalid values")
                
                logger.info(f"Successfully fetched valid spec for {name}")
                break
                
        except httpx.HTTPError as e:
            logger.warning(f"HTTP error fetching spec (attempt {attempt + 1}): {e}")
            if attempt == 2:
                logger.error(f"Failed to fetch spec after 3 attempts, using fallback")
        except SpecValidationError as e:
            logger.warning(f"Spec validation error (attempt {attempt + 1}): {e}")
            if attempt == 2:
                logger.error(f"Invalid spec after 3 attempts, using fallback")
        except Exception as e:
            logger.error(f"Unexpected error fetching spec: {e}")
            
        await asyncio.sleep(2 ** attempt)  # Exponential backoff
    
    # Fallback spec if all attempts failed
    if not spec:
        logger.warning(f"Using fallback spec for {name}")
        spec = {
            "persona": f"{name} is a specialized AI agent with expertise in {role}. "
                      f"This agent leverages {len(tools)} tools to accomplish complex tasks efficiently.",
            "system_prompt": f"""You are {name}, an expert agent specialized in {role}.

Your available tools are: {', '.join(tools)}

Core Principles:
1. Lexical Density: Use precise, information-dense language
2. Semantic Gravity: Balance concrete details with conceptual clarity
3. Semantic Prosody: Maintain professional, solution-oriented tone
4. Tool Usage: Leverage your tools efficiently to accomplish tasks

Always provide clear, actionable responses that directly address the user's needs.""",
            "agent_md": f"""# {name} Agent Specification

## Role
{role}

## Available Tools
{chr(10).join(f'- {tool}' for tool in tools)}

## Capabilities
- Expert analysis and execution within domain
- Tool orchestration for complex workflows
- Collaborative work with other squad agents

## Best Practices
1. Always validate inputs before processing
2. Use appropriate tools for each subtask
3. Provide clear status updates during execution
4. Handle errors gracefully with informative messages
"""
        }
    
    # Create agent directory structure
    try:
        agent_dir = f"./agents/{name}"
        os.makedirs(agent_dir, exist_ok=True)
        os.makedirs(f"{agent_dir}/logs", exist_ok=True)
        os.makedirs(f"{agent_dir}/cache", exist_ok=True)
        
        # Save agent markdown spec
        spec_path = f"{agent_dir}/agent.md"
        with open(spec_path, "w", encoding="utf-8") as f:
            f.write(spec["agent_md"])
        
        # Save full profile as JSON
        profile_path = f"{agent_dir}/profile.json"
        profile_data = {
            "name": name,
            "role": role,
            "tools": tools,
            "model": model,
            "persona": spec["persona"],
            "system_prompt": spec["system_prompt"],
            "created_at": datetime.now().isoformat()
        }
        with open(profile_path, "w", encoding="utf-8") as f:
            json.dump(profile_data, f, indent=2)
            
    except IOError as e:
        raise AgentCreationError(f"Failed to create agent directory structure: {e}")
    
    # Create and configure ClaudeAgent instance
    try:
        agent = ClaudeAgent(
            name=name,
            api_key=api_key,
            model=model,
            system_prompt=spec["system_prompt"],
            tools=tools,
            max_retries=3,
            temperature=0.7
        )
        
        # Configure agent with additional metadata
        agent.persona = spec["persona"]
        agent.role = role
        agent.profile_path = profile_path
        
        # Add agent to squad
        squad.add_agent(agent)
        logger.info(f"Successfully added {name} agent to squad")
        
        return {
            "success": True,
            "agent": {
                "name": name,
                "role": role,
                "model": model,
                "tools": tools,
                "profile_path": profile_path
            },
            "message": f"Agent {name} created successfully"
        }
        
    except Exception as e:
        logger.error(f"Failed to instantiate ClaudeAgent: {e}")
        # Clean up on failure
        try:
            import shutil
            shutil.rmtree(agent_dir)
        except:
            pass
        raise AgentCreationError(f"Failed to create agent instance: {e}")

# Backwards compatibility wrapper
async def add_agent(name: str, role: str, tools: List[str]):
    """Legacy function wrapper for backwards compatibility"""
    return await add_agent_with_profile(name, role, tools)

@app.on_event("startup")
async def startup():
    """Initialize the agent squad on startup"""
    logger.info("Initializing Agent Squad...")
    
    # Set up supervisor
    supervisor = BaseSupAgent("PM", api_key=os.getenv("OPENAI_API_KEY"))
    squad.set_supervisor(supervisor)
    
    # Add default agents with error handling
    agents_config = [
        {
            "name": "Researcher",
            "role": "analyzing data and summarizing information from various sources",
            "tools": ["filesystem.readFile", "rag-web-browser", "web_search"]
        },
        {
            "name": "Writer",
            "role": "crafting high-quality prose, documentation, and creative content",
            "tools": ["filesystem.writeFile", "filesystem.readFile"]
        },
        {
            "name": "Coder",
            "role": "writing clean, efficient code and implementing technical solutions",
            "tools": ["command-runner", "filesystem.writeFile", "filesystem.readFile"]
        }
    ]
    
    for config in agents_config:
        try:
            result = await add_agent_with_profile(**config)
            logger.info(f"Agent creation result: {result}")
        except AgentCreationError as e:
            logger.error(f"Failed to create {config['name']} agent: {e}")
            # Continue with other agents even if one fails
        except Exception as e:
            logger.error(f"Unexpected error creating {config['name']} agent: {e}")
    
    logger.info(f"Squad initialized with {len(squad.agents)} agents")

@app.post("/run_squad")
async def run_squad(request: Request):
    """Execute a request through the agent squad"""
    try:
        logger.info(f"Processing squad request: {request.query[:100]}...")
        result = await squad.route_request(
            request.query, 
            session_id=request.session_id
        )
        return {"success": True, "result": result}
    except Exception as e:
        logger.error(f"Squad execution error: {e}")
        return {"success": False, "error": str(e), "error_type": type(e).__name__}

@app.get("/agents")
async def get_agents():
    """Get information about all agents"""
    agents_info = []
    for agent in squad.agents:
        agents_info.append({
            "name": agent.name,
            "role": getattr(agent, 'role', 'Unknown'),
            "tools": agent.tools,
            "model": agent.model,
            "persona": getattr(agent, 'persona', 'No persona defined')
        })
    return {"agents": agents_info, "supervisor": squad.supervisor.name if squad.supervisor else None}

@app.post("/add_agent")
async def add_agent_endpoint(config: AgentConfig):
    """API endpoint to dynamically add new agents"""
    try:
        result = await add_agent_with_profile(
            name=config.name,
            role=config.role,
            tools=config.tools
        )
        return result
    except AgentCreationError as e:
        raise HTTPException(status_code=500, detail=str(e))
    except Exception as e:
        logger.error(f"Unexpected error in add_agent endpoint: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")

@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {
        "status": "healthy",
        "service": "agent-squad-api",
        "agents": len(squad.agents),
        "supervisor": squad.supervisor.name if squad.supervisor else "Not configured",
        "generator_url": f"http://localhost:{os.getenv('GENERATOR_PORT', 8001)}",
        "uptime": datetime.now().isoformat()
    }

if __name__ == "__main__":
    import uvicorn
    port = int(os.getenv("SQUAD_API_PORT", 8000))
    uvicorn.run(app, host="0.0.0.0", port=port)
