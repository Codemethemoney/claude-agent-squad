"""
AWSLabs Agent-Squad Integration for Jump Codes
This file properly integrates the jump code system with AWSLabs' agent-squad library
"""

# First, let's create a configuration that properly imports from agent-squad
try:
    # Try to import from the actual AWSLabs agent-squad library
    from agent_squad import Agent, Task, Crew
    AGENT_SQUAD_AVAILABLE = True
except ImportError:
    try:
        # Fallback to crewai if installed
        from crewai import Agent, Task, Crew
        AGENT_SQUAD_AVAILABLE = False
        print("Warning: Using crewai as fallback. Install agent-squad for full AWSLabs integration:")
        print("pip install agent-squad")
    except ImportError:
        # Use mock classes if neither is available
        AGENT_SQUAD_AVAILABLE = False
        print("Warning: Neither agent-squad nor crewai found. Using mock implementation.")
        
        class Agent:
            def __init__(self, role, goal, backstory, tools=None, verbose=True, allow_delegation=False):
                self.role = role
                self.goal = goal
                self.backstory = backstory
                self.tools = tools or []
                self.verbose = verbose
        
        class Task:
            def __init__(self, description, agent, expected_output):
                self.description = description
                self.agent = agent
                self.expected_output = expected_output
        
        class Crew:
            def __init__(self, agents, tasks, verbose=True, process="sequential"):
                self.agents = agents
                self.tasks = tasks
                self.verbose = verbose
                self.process = process
            
            def kickoff(self):
                return "Mock execution completed"

def get_agent_squad_status():
    """Return the current agent-squad integration status"""
    return {
        "agent_squad_available": AGENT_SQUAD_AVAILABLE,
        "implementation": "AWSLabs agent-squad" if AGENT_SQUAD_AVAILABLE else "Mock/Fallback",
        "import_source": "agent_squad" if AGENT_SQUAD_AVAILABLE else "mock"
    }

# Export the classes for use in jump code integration
__all__ = ['Agent', 'Task', 'Crew', 'AGENT_SQUAD_AVAILABLE', 'get_agent_squad_status']
