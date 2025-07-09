#!/usr/bin/env python3
"""
Setup script for AWSLabs agent-squad integration
This script helps configure the jump codes to work with AWSLabs' agent-squad
"""

import os
import sys
import subprocess

def check_agent_squad():
    """Check if agent-squad is installed"""
    try:
        import agent_squad
        return True, agent_squad.__version__ if hasattr(agent_squad, '__version__') else 'unknown'
    except ImportError:
        return False, None

def install_agent_squad():
    """Attempt to install agent-squad"""
    print("\n🔧 Installing AWSLabs agent-squad...")
    
    # Try different installation methods
    methods = [
        ("pip install agent-squad", "PyPI"),
        ("pip install git+https://github.com/awslabs/agent-squad.git", "GitHub"),
    ]
    
    for cmd, source in methods:
        print(f"\nTrying to install from {source}: {cmd}")
        try:
            subprocess.run(cmd.split(), check=True)
            return True
        except subprocess.CalledProcessError:
            print(f"❌ Failed to install from {source}")
    
    return False

def update_imports():
    """Update the import statements to use agent-squad"""
    file_path = "python_agent_squad/agent_squad_jump_integration.py"
    
    print(f"\n📝 Updating imports in {file_path}...")
    
    try:
        with open(file_path, 'r') as f:
            content = f.read()
        
        # Replace the import statement
        old_import = "from crewai import Agent, Task, Crew"
        new_import = "from agent_squad import Agent, Task, Crew"
        
        if old_import in content:
            content = content.replace(old_import, new_import)
            
            with open(file_path, 'w') as f:
                f.write(content)
            
            print("✅ Import statements updated successfully!")
            return True
        else:
            print("ℹ️  Import statements already updated or using mock implementation")
            return True
            
    except Exception as e:
        print(f"❌ Error updating imports: {e}")
        return False

def test_integration():
    """Test the integration"""
    print("\n🧪 Testing integration...")
    
    try:
        # Change to the correct directory
        os.chdir('python_agent_squad')
        
        # Try to import and test
        from awslabs_integration import get_agent_squad_status, Agent, Task, Crew
        
        status = get_agent_squad_status()
        print(f"\n✅ Integration Status:")
        print(f"   - Available: {status['agent_squad_available']}")
        print(f"   - Implementation: {status['implementation']}")
        print(f"   - Import Source: {status['import_source']}")
        
        # Try to create an agent
        agent = Agent(
            role="test_agent",
            goal="test integration",
            backstory="Test agent for integration"
        )
        print(f"\n✅ Successfully created test agent: {agent.role}")
        
        return True
        
    except Exception as e:
        print(f"\n❌ Integration test failed: {e}")
        return False
    finally:
        os.chdir('..')

def main():
    """Main setup process"""
    print("""
╔═══════════════════════════════════════════════════════════════╗
║        AWSLabs Agent-Squad Integration Setup                  ║
╚═══════════════════════════════════════════════════════════════╝
    """)
    
    # Check current status
    installed, version = check_agent_squad()
    
    if installed:
        print(f"✅ agent-squad is already installed (version: {version})")
    else:
        print("❌ agent-squad is not installed")
        
        response = input("\nWould you like to install agent-squad? (y/n): ").lower()
        if response == 'y':
            if install_agent_squad():
                print("\n✅ agent-squad installed successfully!")
                installed = True
            else:
                print("\n⚠️  Could not install agent-squad automatically.")
                print("\nPlease install manually using one of these methods:")
                print("1. pip install agent-squad")
                print("2. pip install git+https://github.com/awslabs/agent-squad.git")
                print("3. Clone the repo and install locally")
    
    if installed:
        # Update imports
        if update_imports():
            # Test the integration
            if test_integration():
                print("\n🎉 AWSLabs agent-squad integration is ready!")
                print("\nYou can now use jump codes with AWSLabs' agent-squad:")
                print("  python python_agent_squad/demo_jump_codes.py")
                print("  python python_agent_squad/jump_code_cli.py")
            else:
                print("\n⚠️  Integration test failed. Please check the error messages above.")
        else:
            print("\n⚠️  Could not update imports. Please update manually.")
    
    print("\n" + "="*60)
    print("Setup complete!")
    print("="*60)

if __name__ == "__main__":
    main()
