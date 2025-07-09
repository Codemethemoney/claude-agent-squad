#!/usr/bin/env python3
"""
Test script for the enhanced add_agent_with_profile function.
Demonstrates error handling and robust agent creation.
"""

import asyncio
import os
import sys
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Add current directory to path to import main
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from main import add_agent_with_profile, AgentCreationError, squad

async def test_agent_creation():
    """Test the enhanced agent creation with various scenarios"""
    
    print("Testing Agent Creation with Enhanced Error Handling\n")
    print("=" * 50)
    
    # Test 1: Normal agent creation
    print("\n1. Testing normal agent creation...")
    try:
        result = await add_agent_with_profile(
            name="DataAnalyst",
            role="performing complex data analysis and visualization",
            tools=["filesystem.readFile", "python.execute", "matplotlib.plot"]
        )
        print(f"✓ Success: {result['message']}")
        print(f"  Agent details: {result['agent']}")
    except Exception as e:
        print(f"✗ Error: {e}")
    
    # Test 2: Agent with custom model
    print("\n2. Testing agent with custom model...")
    try:
        result = await add_agent_with_profile(
            name="Translator",
            role="translating text between multiple languages",
            tools=["translate.detect", "translate.convert"],
            model="claude-3-opus-20240229"
        )
        print(f"✓ Success: {result['message']}")
        print(f"  Model: {result['agent']['model']}")
    except Exception as e:
        print(f"✗ Error: {e}")
    
    # Test 3: Agent with missing API key (should fail)
    print("\n3. Testing agent creation without API key...")
    # Temporarily clear API keys
    original_key = os.environ.get("OPENAI_API_KEY", "")
    os.environ.pop("OPENAI_API_KEY", None)
    os.environ.pop("OPENAI_API_KEY_TESTER", None)
    
    try:
        result = await add_agent_with_profile(
            name="Tester",
            role="testing software applications",
            tools=["test.run", "test.report"]
        )
        print(f"✗ Unexpected success: {result}")
    except AgentCreationError as e:
        print(f"✓ Expected error caught: {e}")
    except Exception as e:
        print(f"✗ Unexpected error type: {type(e).__name__}: {e}")
    finally:
        # Restore API key
        if original_key:
            os.environ["OPENAI_API_KEY"] = original_key
    
    # Test 4: List all created agents
    print("\n4. Checking squad agents...")
    print(f"Total agents in squad: {len(squad.agents)}")
    for agent in squad.agents:
        print(f"  - {agent.name}: {getattr(agent, 'role', 'No role defined')}")
    
    # Test 5: Verify agent directories
    print("\n5. Verifying agent directories...")
    agents_dir = "./agents"
    if os.path.exists(agents_dir):
        for agent_name in os.listdir(agents_dir):
            agent_path = os.path.join(agents_dir, agent_name)
            if os.path.isdir(agent_path):
                files = os.listdir(agent_path)
                print(f"  {agent_name}/: {', '.join(files)}")
    
    print("\n" + "=" * 50)
    print("Test completed!")

if __name__ == "__main__":
    asyncio.run(test_agent_creation())
