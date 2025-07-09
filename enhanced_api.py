"""
Enhanced Claude Agent Squad API with Full Jump Code Integration
Combines both the original and enhanced jump code implementations
"""

from fastapi import FastAPI, HTTPException, BackgroundTasks, WebSocket
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import Dict, List, Any, Optional
import asyncio
import json
from datetime import datetime

# Import both jump code implementations
from python_agent_squad.agent_squad_jump_integration import EnhancedAgentSquad
from python_agent_squad.enhanced_jump_codes import (
    execute, execute_async, execute_parallel, execute_sequential,
    list_jump_codes, get_execution_history, get_context,
    JumpCodeResult
)

app = FastAPI(
    title="Enhanced Claude Agent Squad API",
    description="REST API with both original and enhanced jump code systems",
    version="3.0.0"
)

# Enable CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize the squad
squad = EnhancedAgentSquad()

# Pydantic models
class JumpCodeRequest(BaseModel):
    code: str
    async_mode: bool = False
    use_enhanced: bool = True  # Toggle between implementations

class JumpCodeBatchRequest(BaseModel):
    codes: List[str]
    mode: str = "sequential"  # sequential, parallel
    use_enhanced: bool = True

class AgentCreateRequest(BaseModel):
    role: str
    goal: Optional[str] = ""
    backstory: Optional[str] = ""
    id: Optional[str] = None

# Health check
@app.get("/health")
async def health_check():
    """Health check endpoint with both jump code systems status"""
    # Get status from original implementation
    original_status = squad.process_jump_code("@status")
    
    # Get status from enhanced implementation  
    enhanced_status = execute("@status") if "@status" in list_jump_codes() else None
    
    return {
        "status": "healthy",
        "timestamp": datetime.now().isoformat(),
        "jump_codes": {
            "original": {
                "available": len(squad.jump_registry.codes),
                "status": original_status
            },
            "enhanced": {
                "available": len(list_jump_codes()),
                "executed": len(get_execution_history())
            } if enhanced_status else None
        }
    }

# Jump Code Endpoints
@app.post("/jump/execute")
async def execute_jump_code(request: JumpCodeRequest):
    """Execute a single jump code using either implementation"""
    try:
        if request.use_enhanced:
            # Use enhanced implementation
            if request.async_mode:
                result = await execute_async(request.code)
            else:
                result = execute(request.code)
            
            return {
                "implementation": "enhanced",
                "success": result.success,
                "data": result.data,
                "error": result.error,
                "execution_time": result.execution_time,
                "timestamp": result.timestamp.isoformat()
            }
        else:
            # Use original implementation
            result = squad.process_jump_code(request.code)
            return {
                "implementation": "original",
                "result": result
            }
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@app.post("/jump/batch")
async def execute_batch(request: JumpCodeBatchRequest):
    """Execute multiple jump codes"""
    try:
        if request.use_enhanced:
            if request.mode == "parallel":
                results = execute_parallel(request.codes)
            else:
                results = execute_sequential(request.codes)
            
            return {
                "implementation": "enhanced",
                "mode": request.mode,
                "total": len(results),
                "results": [
                    {
                        "code": request.codes[i],
                        "success": r.success,
                        "data": r.data,
                        "error": r.error,
                        "execution_time": r.execution_time
                    }
                    for i, r in enumerate(results)
                ]
            }
        else:
            # Use original implementation with sequential execution
            results = []
            for code in request.codes:
                result = squad.process_jump_code(code)
                results.append(result)
            
            return {
                "implementation": "original",
                "mode": "sequential",
                "total": len(results),
                "results": results
            }
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@app.get("/jump/codes")
async def list_codes(implementation: str = "both"):
    """List all available jump codes from one or both implementations"""
    result = {}
    
    if implementation in ["original", "both"]:
        # Get codes from original implementation
        original_codes = []
        for code_name in squad.jump_registry.codes:
            original_codes.append(code_name)
        result["original"] = {
            "total": len(original_codes),
            "codes": original_codes
        }
    
    if implementation in ["enhanced", "both"]:
        # Get codes from enhanced implementation
        enhanced_codes = list_jump_codes()
        result["enhanced"] = {
            "total": len(enhanced_codes),
            "codes": enhanced_codes
        }
    
    return result

@app.get("/jump/history")
async def get_history(limit: int = 100, implementation: str = "enhanced"):
    """Get jump code execution history"""
    if implementation == "enhanced":
        history = get_execution_history()
        return {
            "implementation": "enhanced",
            "total": len(history),
            "recent": history[-limit:],
            "success_rate": sum(1 for h in history if h['success']) / len(history) * 100 if history else 0
        }
    else:
        return {
            "implementation": "original",
            "message": "History not available for original implementation"
        }

# Agent Endpoints (using original implementation)
@app.post("/agents")
async def create_agent(agent: AgentCreateRequest):
    """Create a new agent using jump codes"""
    params = f"role={agent.role}"
    if agent.goal:
        params += f",goal={agent.goal}"
    if agent.backstory:
        params += f",backstory={agent.backstory}"
    
    result = squad.process_jump_code(f"@create_agent:{params}")
    if not result.get('error'):
        return result
    else:
        raise HTTPException(status_code=400, detail=result.get('message'))

@app.get("/agents")
async def list_agents():
    """List all agents"""
    result = squad.process_jump_code("@list_agents")
    if not result.get('error'):
        return result
    else:
        raise HTTPException(status_code=400, detail=result.get('message'))

# WebSocket endpoint for real-time jump code execution
@app.websocket("/ws/jump")
async def websocket_jump_codes(websocket: WebSocket):
    """WebSocket endpoint for real-time jump code execution"""
    await websocket.accept()
    
    try:
        while True:
            data = await websocket.receive_text()
            request = json.loads(data)
            
            if request.get("type") == "execute":
                code = request.get("code")
                use_enhanced = request.get("use_enhanced", True)
                
                if code:
                    if use_enhanced:
                        result = await execute_async(code)
                        await websocket.send_json({
                            "type": "result",
                            "implementation": "enhanced",
                            "code": code,
                            "success": result.success,
                            "data": result.data,
                            "error": result.error,
                            "execution_time": result.execution_time
                        })
                    else:
                        result = squad.process_jump_code(code)
                        await websocket.send_json({
                            "type": "result",
                            "implementation": "original",
                            "code": code,
                            "result": result
                        })
            elif request.get("type") == "list":
                codes = list_jump_codes()
                original_codes = list(squad.jump_registry.codes.keys())
                await websocket.send_json({
                    "type": "codes",
                    "enhanced_codes": codes,
                    "original_codes": original_codes
                })
    except Exception as e:
        await websocket.send_json({
            "type": "error",
            "error": str(e)
        })
    finally:
        await websocket.close()

# Demonstration endpoint
@app.get("/demo")
async def run_demo():
    """Run a demonstration of both jump code systems"""
    results = {
        "original_implementation": [],
        "enhanced_implementation": []
    }
    
    # Test original implementation
    original_tests = [
        "@status",
        "@create_agent:role=demo_agent,goal=demonstrate system",
        "@list_agents"
    ]
    
    for code in original_tests:
        result = squad.process_jump_code(code)
        results["original_implementation"].append({
            "code": code,
            "result": result
        })
    
    # Test enhanced implementation (if handlers are registered)
    enhanced_tests = [
        "@status",
        "@help"
    ]
    
    for code in enhanced_tests:
        if code.replace("@", "") in [c.replace("@", "") for c in list_jump_codes()]:
            result = execute(code)
            results["enhanced_implementation"].append({
                "code": code,
                "success": result.success,
                "data": result.data
            })
    
    return results

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
