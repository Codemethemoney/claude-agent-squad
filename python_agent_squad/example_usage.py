#!/usr/bin/env python3
"""
Example usage of Jump Codes in Claude Agent Squad
"""

from agent_squad_jump_integration import EnhancedAgentSquad
from advanced_jump_codes import SequentialJumpCodes, JumpCodeMacros

def example_basic_usage():
    """Basic jump code usage"""
    print("\n=== Basic Jump Code Usage ===")
    
    # Create enhanced squad
    squad = EnhancedAgentSquad()
    
    # Execute simple jump codes
    print("\n1. Creating an agent:")
    result = squad.process_jump_code("@create_agent:role=researcher,goal=find information")
    print(f"   Result: {result}")
    
    print("\n2. Listing agents:")
    result = squad.process_jump_code("@list_agents")
    print(f"   Agents: {result.get('agents', [])}")
    
    print("\n3. Checking status:")
    result = squad.process_jump_code("@status")
    print(f"   Status: Total codes={result.get('total_codes')}, Context keys={result.get('context_keys')}")

def example_task_management():
    """Task assignment and chaining"""
    print("\n=== Task Management ===")
    
    squad = EnhancedAgentSquad()
    
    # Create multiple agents
    agents_to_create = [
        ("analyst", "analyze data and find patterns"),
        ("writer", "create clear documentation"),
        ("reviewer", "review and improve quality")
    ]
    
    for role, goal in agents_to_create:
        squad.process_jump_code(f"@create_agent:role={role},goal={goal}")
    
    # Assign tasks
    print("\n1. Assigning individual tasks:")
    squad.process_jump_code("@assign_task:agent=agent_1,task=analyze user feedback data")
    squad.process_jump_code("@assign_task:agent=agent_2,task=write summary report")
    
    print("\n2. Chaining tasks:")
    result = squad.process_jump_code("@chain:tasks=agent_1:collect data,agent_2:process data,agent_3:generate report")
    print(f"   Chain result: {result}")

def example_sequential_execution():
    """Sequential jump code execution"""
    print("\n=== Sequential Execution ===")
    
    squad = EnhancedAgentSquad()
    sequential = SequentialJumpCodes(squad.jump_registry)
    
    # Define a workflow sequence
    workflow = [
        "@create_agent:role=developer,goal=write code",
        "@create_agent:role=tester,goal=test code",
        "@create_agent:role=deployer,goal=deploy code",
        "@list_agents",
        "@status"
    ]
    
    print("\nExecuting workflow sequence:")
    results = sequential.execute_sequence(workflow)
    
    for i, result in enumerate(results, 1):
        status = "✓" if result['success'] else "✗"
        print(f"  {status} Step {i}: {result['code']}")

def example_macros():
    """Using macros for complex workflows"""
    print("\n=== Macro Usage ===")
    
    squad = EnhancedAgentSquad()
    macros = JumpCodeMacros()
    
    # Define a custom macro
    print("\n1. Defining custom macro:")
    macros.define_macro(
        name="code_review_workflow",
        sequence=[
            "@create_agent:role=${reviewer_role},goal=review ${target} code",
            "@assign_task:agent=agent_1,task=review ${target} for ${criteria}",
            "@debug:agent=agent_1,verbose=true"
        ],
        description="Complete code review workflow",
        parameters=["reviewer_role", "target", "criteria"]
    )
    
    # Expand and execute macro
    print("\n2. Expanding macro:")
    expanded = macros.expand_macro("code_review_workflow", {
        "reviewer_role": "senior_reviewer",
        "target": "authentication module",
        "criteria": "security vulnerabilities"
    })
    
    print("   Expanded commands:")
    for cmd in expanded:
        print(f"     - {cmd}")
    
    # Execute the expanded sequence
    sequential = SequentialJumpCodes(squad.jump_registry)
    results = sequential.execute_sequence(expanded)
    print(f"\n   Execution complete: {len([r for r in results if r['success']])} successful")

def example_state_management():
    """State saving and restoration"""
    print("\n=== State Management ===")
    
    squad = EnhancedAgentSquad()
    
    # Create initial state
    print("\n1. Creating initial state:")
    squad.process_jump_code("@create_agent:role=stateful_agent,goal=maintain state")
    squad.process_jump_code("@assign_task:agent=agent_1,task=process initial data")
    
    # Save state
    print("\n2. Saving state:")
    result = squad.process_jump_code("@save_state:name=checkpoint_alpha")
    print(f"   Save result: {result.get('message')}")
    
    # Modify state
    print("\n3. Modifying state:")
    squad.process_jump_code("@create_agent:role=temporary_agent,goal=temporary work")
    squad.process_jump_code("@assign_task:agent=agent_2,task=risky operation")
    
    # Show current state
    result = squad.process_jump_code("@list_agents")
    print(f"   Current agents: {len(result.get('agents', []))}")
    
    # Restore if needed (demonstration)
    print("\n4. State can be restored with: @restore_state:name=checkpoint_alpha")

def example_parallel_execution():
    """Parallel task execution"""
    print("\n=== Parallel Execution ===")
    
    squad = EnhancedAgentSquad()
    
    # Create agents for parallel work
    squad.process_jump_code("@create_agent:role=api_tester,goal=test APIs")
    squad.process_jump_code("@create_agent:role=ui_tester,goal=test UI")
    squad.process_jump_code("@create_agent:role=db_tester,goal=test database")
    
    # Execute tasks in parallel
    print("\n1. Running tests in parallel:")
    result = squad.process_jump_code(
        "@parallel:tasks=agent_1:test authentication API;agent_2:test login UI;agent_3:test user database,timeout=60"
    )
    
    if result.get('error'):
        print(f"   Error: {result.get('message')}")
    else:
        print(f"   Completed: {result.get('completed')}/{result.get('total')} tasks")
        print(f"   Results: {result.get('message')}")

def example_error_handling():
    """Error handling examples"""
    print("\n=== Error Handling ===")
    
    squad = EnhancedAgentSquad()
    
    # Test various error conditions
    print("\n1. Invalid jump code:")
    result = squad.process_jump_code("@invalid_code")
    print(f"   Result: {result}")
    
    print("\n2. Missing required parameter:")
    result = squad.process_jump_code("@create_agent:role=incomplete")  # Missing 'goal'
    print(f"   Result: {result}")
    
    print("\n3. Invalid parameter format:")
    result = squad.process_jump_code("@assign_task:this is not valid format")
    print(f"   Result: {result}")
    
    print("\n4. Non-existent agent:")
    result = squad.process_jump_code("@assign_task:agent=ghost_agent,task=impossible task")
    print(f"   Result: {result}")

def run_all_examples():
    """Run all example demonstrations"""
    print("="*70)
    print("Claude Agent Squad - Jump Code Examples")
    print("="*70)
    
    examples = [
        ("Basic Usage", example_basic_usage),
        ("Task Management", example_task_management),
        ("Sequential Execution", example_sequential_execution),
        ("Macros", example_macros),
        ("State Management", example_state_management),
        ("Parallel Execution", example_parallel_execution),
        ("Error Handling", example_error_handling)
    ]
    
    for name, example_func in examples:
        try:
            example_func()
        except Exception as e:
            print(f"\n❌ Error in {name}: {str(e)}")
    
    print("\n" + "="*70)
    print("Examples completed!")
    print("="*70)

if __name__ == "__main__":
    # Run specific example or all
    import sys
    
    if len(sys.argv) > 1:
        example_name = sys.argv[1]
        examples_map = {
            'basic': example_basic_usage,
            'tasks': example_task_management,
            'sequential': example_sequential_execution,
            'macros': example_macros,
            'state': example_state_management,
            'parallel': example_parallel_execution,
            'errors': example_error_handling
        }
        
        if example_name in examples_map:
            examples_map[example_name]()
        else:
            print(f"Unknown example: {example_name}")
            print(f"Available: {', '.join(examples_map.keys())}")
    else:
        run_all_examples()
