#!/usr/bin/env python3
"""
Jump Code CLI - Interactive command-line interface for Claude Agent Squad
"""

import os
import sys
import json
import yaml
from typing import Dict, Any
from agent_squad_jump_integration import EnhancedAgentSquad
from advanced_jump_codes import JumpCodeMiddleware
import logging
from datetime import datetime

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

class JumpCodeCLI:
    """Interactive CLI for Jump Codes"""
    
    def __init__(self):
        self.squad = EnhancedAgentSquad()
        self.middleware = JumpCodeMiddleware(self.squad)
        self.running = True
        self.command_history = []
        self._load_config()
        
    def _load_config(self):
        """Load configuration from YAML"""
        try:
            with open('jump_codes_config.yaml', 'r') as f:
                self.config = yaml.safe_load(f)
                logger.info("Loaded jump codes configuration")
        except FileNotFoundError:
            logger.warning("No jump_codes_config.yaml found, using defaults")
            self.config = {'jump_codes': {'enabled': True, 'prefix': '@'}}
    
    def display_welcome(self):
        """Display welcome message"""
        print("\n" + "="*60)
        print("🚀 Claude Agent Squad - Jump Code System")
        print("="*60)
        print("\nAvailable commands:")
        print("  @help              - Show available jump codes")
        print("  @list              - List all jump codes")
        print("  @status            - Show system status")
        print("  !macro_name(...)   - Execute a macro")
        print("  @@code1 @@code2    - Execute sequence")
        print("  /exit              - Exit the CLI")
        print("  /history           - Show command history")
        print("\nType any jump code to execute it!")
        print("="*60 + "\n")
    
    def format_result(self, result: Dict[str, Any]) -> str:
        """Format result for display"""
        if result.get('error'):
            return f"❌ Error: {result.get('message', 'Unknown error')}"
        
        result_type = result.get('type', 'unknown')
        
        # Format based on result type
        if result_type == 'help':
            lines = ["📚 Available Jump Codes:"]
            for code in result.get('codes', []):
                code_str = f"  @{code['code']}"
                if code.get('aliases'):
                    code_str += f" (aliases: {', '.join(code['aliases'])})"
                code_str += f" - {code['description']}"
                lines.append(code_str)
            return "\n".join(lines)
        
        elif result_type == 'list':
            lines = ["📋 Jump Code List:"]
            lines.extend(f"  {code}" for code in result.get('codes', []))
            return "\n".join(lines)
        
        elif result_type == 'status':
            return f"""📊 System Status:
  Total Codes: {result.get('total_codes', 0)}
  Total Aliases: {result.get('total_aliases', 0)}
  Context Keys: {', '.join(result.get('context_keys', []))}
  Timestamp: {result.get('timestamp', 'N/A')}"""
        
        elif result_type == 'agent_created':
            return f"✅ Agent '{result.get('role')}' created successfully (ID: {result.get('agent_id')})"
        
        elif result_type == 'task_assigned':
            return f"✅ Task assigned to {result.get('agent')}: {result.get('task')}"
        
        elif result_type == 'agents_list':
            lines = ["👥 Active Agents:"]
            for agent in result.get('agents', []):
                lines.append(f"  • {agent['id']}: {agent['role']} - {agent['goal']}")
            return "\n".join(lines)
        
        elif result_type == 'sequence_execution':
            lines = [f"🔄 Sequence Execution: {result.get('success_count')}/{result.get('total_count')} successful"]
            for res in result.get('results', []):
                status = "✓" if res['success'] else "✗"
                lines.append(f"  {status} {res['code']}")
            return "\n".join(lines)
        
        elif result_type == 'macro_executed':
            return f"🎯 Macro '{result.get('name')}' executed: {result.get('success_rate', 0)*100:.0f}% success"
        
        elif result_type == 'macros_list':
            lines = ["🎭 Available Macros:"]
            lines.extend(f"  {macro}" for macro in result.get('macros', []))
            return "\n".join(lines)
        
        else:
            # Generic formatting
            return f"✅ {result.get('message', json.dumps(result, indent=2))}"
    
    def process_command(self, command: str):
        """Process a single command"""
        command = command.strip()
        
        if not command:
            return
        
        # Add to history
        self.command_history.append({
            'command': command,
            'timestamp': datetime.now().isoformat()
        })
        
        # Check for special commands
        if command == '/exit':
            self.running = False
            print("👋 Goodbye!")
            return
        
        elif command == '/history':
            print("\n📜 Command History:")
            for i, entry in enumerate(self.command_history[-10:], 1):
                print(f"  {i}. [{entry['timestamp'].split('T')[1].split('.')[0]}] {entry['command']}")
            return
        
        elif command.startswith('/'):
            print(f"❓ Unknown command: {command}")
            return
        
        # Process through middleware
        try:
            result = self.middleware.process_input(command)
            
            if result:
                print(self.format_result(result))
            else:
                # Not a jump code, might be regular text
                print(f"💬 Input: {command}")
                print("   (Not recognized as a jump code)")
        
        except Exception as e:
            logger.error(f"Error processing command: {e}")
            print(f"❌ Error: {str(e)}")
    
    def run(self):
        """Main CLI loop"""
        self.display_welcome()
        
        while self.running:
            try:
                # Get user input
                command = input("\n🤖 > ").strip()
                
                if command:
                    self.process_command(command)
                    
            except KeyboardInterrupt:
                print("\n\n⚠️  Use '/exit' to quit properly")
            except EOFError:
                self.running = False
                print("\n👋 Goodbye!")
            except Exception as e:
                logger.error(f"Unexpected error: {e}")
                print(f"❌ Unexpected error: {str(e)}")

def main():
    """Main entry point"""
    try:
        cli = JumpCodeCLI()
        cli.run()
    except Exception as e:
        logger.error(f"Failed to start CLI: {e}")
        print(f"❌ Failed to start: {str(e)}")
        sys.exit(1)

if __name__ == "__main__":
    main()
