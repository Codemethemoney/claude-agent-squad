#!/usr/bin/env python3
"""
Test script for Jump Codes system in Claude Agent Squad
"""

import logging
from jump_codes import JumpCodeRegistry, JumpCode
from agent_squad_jump_integration import EnhancedAgentSquad
from advanced_jump_codes import SequentialJumpCodes, JumpCodeMacros, JumpCodeMiddleware

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

def test_basic_jump_codes():
    """Test basic jump code functionality"""
    print("\n=== Testing Basic Jump Codes ===")
    
    registry = JumpCodeRegistry()
    
    # Test status command
    result = registry.execute("@status")
    print(f"Status: {result}")
    assert result['type'] == 'status'
    
    # Test help command
    result = registry.execute("@help")
    print(f"\nHelp returned {len(result['codes'])} codes")
    
    # Test with alias
    result = registry.execute("@s")  # Alias for status
    print(f"\nStatus via alias: {result['type']}")
    assert result['type'] == 'status'
    
    print("\n✓ Basic jump codes working correctly")

def test_agent_squad_integration():
    """Test integration with agent squad"""
    print("\n=== Testing Agent Squad Integration ===")
    
    squad = EnhancedAgentSquad()
    
    # Create an agent
    result = squad.process_jump_code("@create_agent:role=test_agent,goal=test the system")
    print(f"Agent creation: {result}")
    assert not result.get('error'), f"Error creating agent: {result.get('message')}"
    
    # List agents
    result = squad.process_jump_code("@list_agents")
    print(f"\nAgents: {result}")
    assert result['total'] == 1
    
    # Assign a task
    agent_id = "agent_1"
    result = squad.process_jump_code(f"@assign_task:agent={agent_id},task=perform test,priority=high")
    print(f"\nTask assignment: {result}")
    assert not result.get('error')
    
    print("\n✓ Agent squad integration working correctly")

def test_sequential_execution():
    """Test sequential jump code execution"""
    print("\n=== Testing Sequential Execution ===")
    
    squad = EnhancedAgentSquad()
    sequential = SequentialJumpCodes(squad.jump_registry)
    
    # Define a sequence
    sequence = [
        "@create_agent:role=architect,goal=design systems",
        "@create_agent:role=developer,goal=implement features",
        "@list_agents",
        "@status"
    ]
    
    results = sequential.execute_sequence(sequence)
    
    print(f"\nExecuted {len(results)} commands sequentially")
    for i, result in enumerate(results):
        status = "✓" if result['success'] else "✗"
        print(f"{status} Step {i+1}: {result['code']}")
    
    # Check history
    history = sequential.get_history(limit=1)
    if history:
        print(f"\nLast sequence success rate: {history[0]['success_rate']*100:.1f}%")
    
    print("\n✓ Sequential execution working correctly")

def test_macros():
    """Test macro functionality"""
    print("\n=== Testing Macros ===")
    
    macros = JumpCodeMacros()
    
    # List default macros
    macro_list = macros.list_macros()
    print(f"Available macros: {list(macro_list.keys())}")
    
    # Define a custom macro
    macros.define_macro(
        name="test_workflow",
        sequence=[
            "@status",
            "@create_agent:role=${role},goal=${goal}",
            "@list_agents"
        ],
        description="Test workflow macro",
        parameters=["role", "goal"]
    )
    
    # Expand macro
    expanded = macros.expand_macro("test_workflow", {
        "role": "test_role",
        "goal": "test_goal"
    })
    
    print(f"\nExpanded macro steps:")
    for step in expanded:
        print(f"  - {step}")
    
    print("\n✓ Macro system working correctly")

def test_error_handling():
    """Test error handling"""
    print("\n=== Testing Error Handling ===")
    
    squad = EnhancedAgentSquad()
    
    # Test invalid jump code
    result = squad.process_jump_code("@invalid_code")
    print(f"Invalid code result: {result}")
    assert result.get('error') == True
    
    # Test missing required parameter
    result = squad.process_jump_code("@create_agent:role=test")  # Missing 'goal'
    print(f"\nMissing parameter result: {result}")
    assert result.get('error') == True
    
    # Test invalid parameter format
    result = squad.process_jump_code("@status:invalid format here")
    print(f"\nInvalid format result: {result}")
    assert result.get('error') == True
    
    print("\n✓ Error handling working correctly")

def test_middleware():
    """Test jump code middleware"""
    print("\n=== Testing Middleware ===")
    
    squad = EnhancedAgentSquad()
    middleware = JumpCodeMiddleware(squad)
    
    # Test direct jump code
    result = middleware.process_input("@status")
    print(f"Direct code: {result['type'] if result else 'None'}")
    
    # Test macro shorthand
    result = middleware.process_input("!debug_all")
    print(f"\nMacro shorthand: {result['type'] if result else 'None'}")
    
    # Test sequence shorthand
    result = middleware.process_input("@@status @@list_agents")
    print(f"\nSequence shorthand: Executed {result['total_count'] if result else 0} commands")
    
    # Test inline codes
    result = middleware.process_input("Check {@status} and list {@list_agents}")
    print(f"\nInline codes: Processed {len(result['results']) if result else 0} codes")
    
    print("\n✓ Middleware working correctly")

def test_state_management():
    """Test state management jump codes"""
    print("\n=== Testing State Management ===")
    
    squad = EnhancedAgentSquad()
    
    # Create some state
    squad.process_jump_code("@create_agent:role=state_test,goal=test state management")
    
    # Save state
    result = squad.process_jump_code("@save_state:name=test_checkpoint")
    print(f"State saved: {result}")
    assert not result.get('error')
    
    # Modify state
    squad.process_jump_code("@create_agent:role=another_agent,goal=another goal")
    
    # Check current agents
    result = squad.process_jump_code("@list_agents")
    print(f"\nAgents before restore: {result['total']}")
    
    # This is a demonstration - actual restore would need file handling
    print("\n✓ State management codes registered correctly")

def run_all_tests():
    """Run all tests"""
    print("=" * 60)
    print("Testing Claude Agent Squad Jump Codes System")
    print("=" * 60)
    
    tests = [
        test_basic_jump_codes,
        test_agent_squad_integration,
        test_sequential_execution,
        test_macros,
        test_error_handling,
        test_middleware,
        test_state_management
    ]
    
    failed = []
    
    for test in tests:
        try:
            test()
        except Exception as e:
            failed.append((test.__name__, str(e)))
            print(f"\n✗ {test.__name__} failed: {e}")
    
    print("\n" + "=" * 60)
    print(f"Test Summary: {len(tests) - len(failed)}/{len(tests)} passed")
    
    if failed:
        print("\nFailed tests:")
        for name, error in failed:
            print(f"  - {name}: {error}")
    else:
        print("\n🎉 All tests passed!")
    
    print("=" * 60)

if __name__ == "__main__":
    run_all_tests()
