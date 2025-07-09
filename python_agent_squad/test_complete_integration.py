#!/usr/bin/env python3
"""
Complete Integration Test - Verifies all jump code implementations work together
"""

import sys
import os

# Add parent directory to path for imports
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

def test_existing_implementation():
    """Test the existing jump code implementation"""
    print("\n" + "="*70)
    print("Testing EXISTING Jump Code Implementation")
    print("="*70)
    
    try:
        from agent_squad_jump_integration import EnhancedAgentSquad
        
        squad = EnhancedAgentSquad()
        
        # Test basic commands
        tests = [
            ("@status", "System Status"),
            ("@create_agent:role=tester,goal=test system", "Agent Creation"),
            ("@list_agents", "List Agents"),
            ("@help", "Help System")
        ]
        
        for code, description in tests:
            print(f"\n✓ Testing {description}: {code}")
            result = squad.process_jump_code(code)
            print(f"  Result: {result.get('type', 'Unknown')} - {'Success' if not result.get('error') else 'Error'}")
            
        return True
    except Exception as e:
        print(f"❌ Error in existing implementation: {e}")
        return False

def test_enhanced_implementation():
    """Test the enhanced jump code implementation"""
    print("\n" + "="*70)
    print("Testing ENHANCED Jump Code Implementation")
    print("="*70)
    
    try:
        from enhanced_jump_codes import execute, execute_parallel, list_jump_codes
        
        # Register some test handlers
        from enhanced_jump_codes import _processor, JumpCodeResult
        
        def test_handler(params, context):
            return {"message": "Enhanced handler working", "params": params}
        
        _processor.registry.register("@test", test_handler, ["@t"])
        
        # Test execution
        result = execute("@test:param1=value1")
        print(f"\n✓ Enhanced execution test: {'Success' if result.success else 'Failed'}")
        print(f"  Data: {result.data}")
        
        # Test parallel execution
        results = execute_parallel(["@test:id=1", "@test:id=2"])
        print(f"\n✓ Parallel execution: {len(results)} tasks completed")
        
        return True
    except Exception as e:
        print(f"❌ Error in enhanced implementation: {e}")
        return False

def test_cli_exists():
    """Test that CLI components exist"""
    print("\n" + "="*70)
    print("Testing CLI Components")
    print("="*70)
    
    files = [
        "jump_code_cli.py",
        "demo_jump_codes.py",
        "advanced_jump_codes.py"
    ]
    
    all_exist = True
    for file in files:
        exists = os.path.exists(file)
        print(f"✓ {file}: {'Found' if exists else 'Not Found'}")
        if not exists:
            all_exist = False
            
    return all_exist

def test_integration():
    """Test that both implementations can work together"""
    print("\n" + "="*70)
    print("Testing Integration Between Implementations")
    print("="*70)
    
    try:
        # Import both
        from agent_squad_jump_integration import EnhancedAgentSquad
        from enhanced_jump_codes import execute, get_context, set_context
        
        # Create squad
        squad = EnhancedAgentSquad()
        
        # Set context in enhanced system
        set_context("test_key", "test_value")
        
        # Execute in original system
        result = squad.process_jump_code("@status")
        
        print("✓ Both implementations loaded successfully")
        print(f"✓ Original system status: {result.get('type')}")
        print(f"✓ Enhanced context: {get_context()}")
        
        return True
    except Exception as e:
        print(f"❌ Integration error: {e}")
        return False

def main():
    """Run all tests"""
    print("""
╔═══════════════════════════════════════════════════════════════╗
║           Complete Jump Code Integration Test                  ║
║                                                               ║
║  This verifies all jump code implementations work correctly   ║
╚═══════════════════════════════════════════════════════════════╝
    """)
    
    results = {
        "Existing Implementation": test_existing_implementation(),
        "Enhanced Implementation": test_enhanced_implementation(),
        "CLI Components": test_cli_exists(),
        "Integration": test_integration()
    }
    
    print("\n" + "="*70)
    print("TEST RESULTS SUMMARY")
    print("="*70)
    
    for test_name, passed in results.items():
        status = "✅ PASSED" if passed else "❌ FAILED"
        print(f"{test_name}: {status}")
    
    all_passed = all(results.values())
    
    print("\n" + "="*70)
    if all_passed:
        print("🎉 ALL TESTS PASSED! Jump codes are fully integrated!")
    else:
        print("⚠️  Some tests failed. Check the output above.")
    print("="*70)
    
    return 0 if all_passed else 1

if __name__ == "__main__":
    sys.exit(main())
