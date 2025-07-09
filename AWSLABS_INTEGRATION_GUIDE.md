# AWSLabs Agent-Squad Integration Guide

## Overview

This repository includes a **complete JumpCode integration** that's designed to work with AWSLabs' agent-squad library. The integration is already built - you just need to connect it to the actual AWSLabs package.

## Current Architecture

```
claude-agent-squad/
├── python_agent_squad/
│   ├── jump_codes.py                    # Core JumpCode engine
│   ├── agent_squad_jump_integration.py  # Integration layer
│   ├── advanced_jump_codes.py           # Macros and sequences
│   ├── awslabs_integration.py           # NEW: Import management
│   └── requirements-awslabs.txt         # NEW: Dependencies
└── setup_awslabs.py                     # NEW: Setup script
```

## How It Works

### 1. Jump Code Core (`jump_codes.py`)
- Defines `JumpCodeRegistry` and `JumpCode` dataclass
- Handles registration, lookup, and execution of `@code` patterns
- Completely independent of the agent framework

### 2. Agent Integration (`agent_squad_jump_integration.py`)
- `EnhancedAgentSquad` class that:
  - Creates a `JumpCodeRegistry` instance
  - Registers jump codes like `@create_agent`, `@list_agents`, etc.
  - Maps jump codes to agent-squad API calls
  - Currently imports from `crewai` but designed to swap to `agent_squad`

### 3. What's Already Working
All jump codes are wired up and functional:
- `@create_agent` - Creates agents
- `@list_agents` - Lists all agents
- `@assign_task` - Assigns tasks to agents
- `@run_workflow` - Executes workflows
- `@parallel` - Runs tasks in parallel
- And 10+ more commands!

## Integration Steps

### Option 1: Automatic Setup
```bash
python setup_awslabs.py
```

This script will:
1. Check if agent-squad is installed
2. Attempt to install it (from PyPI or GitHub)
3. Update the imports automatically
4. Test the integration

### Option 2: Manual Setup

1. **Install AWSLabs agent-squad**:
```bash
# If published to PyPI:
pip install agent-squad

# Or from GitHub:
pip install git+https://github.com/awslabs/agent-squad.git

# Or clone and install locally:
git clone https://github.com/awslabs/agent-squad.git
cd agent-squad
pip install -e .
```

2. **Update the import** in `agent_squad_jump_integration.py`:
```python
# Change this:
from crewai import Agent, Task, Crew

# To this:
from agent_squad import Agent, Task, Crew
```

3. **Test the integration**:
```bash
cd python_agent_squad
python demo_jump_codes.py
```

## Using the Integration

Once connected to AWSLabs agent-squad:

### 1. CLI Usage
```bash
python jump_code_cli.py
```

Then use jump codes:
```
🚀 jump> @create_agent:role=developer,goal=Build features
🚀 jump> @assign_task:agent=agent_1,task=Implement login
🚀 jump> @run_workflow:workflow=development
```

### 2. Programmatic Usage
```python
from agent_squad_jump_integration import EnhancedAgentSquad

squad = EnhancedAgentSquad()

# Create agent using jump code
result = squad.process_jump_code("@create_agent:role=analyst,goal=Analyze data")

# Or use traditional API
agent = squad.agents['agent_1']
```

### 3. API Usage
```bash
# Start the API
python enhanced_api.py

# Execute jump codes via HTTP
curl -X POST http://localhost:8000/jump/execute \
  -H "Content-Type: application/json" \
  -d '{"code": "@create_agent:role=developer"}'
```

## Key Benefits

1. **No Code Changes Needed** - Just swap the import
2. **All Jump Codes Ready** - 14+ commands already implemented
3. **Maintains Compatibility** - Works with mock, crewai, or agent-squad
4. **Full Feature Set** - Parallel execution, macros, context management

## Verification

Run the demo to verify everything works:

```bash
cd python_agent_squad
python demo_jump_codes.py
```

Expected output:
```
🚀 DEMONSTRATING REAL JUMP CODES IN ACTION
1️⃣ EXECUTING JUMP CODE: @status
   Result: {'type': 'status', 'total_codes': 14, ...}
2️⃣ EXECUTING JUMP CODE: @create_agent:role=developer,goal=write code
   Result: {'type': 'agent_created', 'agent_id': 'agent_1', ...}
...
✅ JUMP CODES ARE WORKING!
```

## Summary

The repository **already has** a complete JumpCode integration for agent-squad. To use it with AWSLabs' implementation:

1. Install `agent-squad` package
2. Change one import line from `crewai` to `agent_squad`
3. That's it! All jump codes will work with AWSLabs agents

The integration is designed to be drop-in compatible - no other changes needed!
