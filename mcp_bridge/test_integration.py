#!/usr/bin/env python3
"""
MCP Bridge Integration Tests
Tests the real WebSocket connection to Claude Desktop MCP tools
"""

import asyncio
import json
import logging
from datetime import datetime
import sys
import os

# Add parent directory to path for imports
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from mcp_integration import MCPToolBridge, integrate_mcp_with_jump_codes

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

class MCPIntegrationTester:
    """Comprehensive test suite for MCP bridge"""
    
    def __init__(self):
        self.bridge = None
        self.results = []
        
    async def setup(self):
        """Initialize test environment"""
        logger.info("Setting up MCP integration tests...")
        self.bridge = MCPToolBridge()
        
    async def teardown(self):
        """Clean up test environment"""
        if self.bridge:
            await self.bridge.close()
        logger.info("Test cleanup complete")
        
    async def test_connection(self):
        """Test basic WebSocket connection"""
        test_name = "WebSocket Connection"
        try:
            await self.bridge._ensure_connection()
            self.results.append({
                'test': test_name,
                'status': 'PASSED',
                'message': 'Successfully connected to MCP server'
            })
        except Exception as e:
            self.results.append({
                'test': test_name,
                'status': 'FAILED',
                'error': str(e)
            })
            
    async def test_file_operations(self):
        """Test filesystem MCP tools"""
        # Test file write
        test_name = "File Write"
        test_path = "/tmp/mcp_test_" + datetime.now().strftime("%Y%m%d_%H%M%S") + ".txt"
        test_content = "MCP Bridge Test Content\n" + datetime.now().isoformat()
        
        try:
            result = await self.bridge.call_mcp_tool("filesystem.writeFile", {
                "path": test_path,
                "content": test_content
            })
            self.results.append({
                'test': test_name,
                'status': 'PASSED',
                'message': f'Successfully wrote to {test_path}',
                'result': result
            })
            
            # Test file read
            test_name = "File Read"
            result = await self.bridge.call_mcp_tool("filesystem.readFile", {
                "path": test_path
            })
            
            if result == test_content:
                self.results.append({
                    'test': test_name,
                    'status': 'PASSED',
                    'message': 'File content matches written content'
                })
            else:
                self.results.append({
                    'test': test_name,
                    'status': 'FAILED',
                    'message': 'File content mismatch',
                    'expected': test_content,
                    'actual': result
                })
                
        except Exception as e:
            self.results.append({
                'test': test_name,
                'status': 'FAILED',
                'error': str(e)
            })
            
    async def test_command_execution(self):
        """Test command runner MCP tool"""
        test_name = "Command Execution"
        
        try:
            result = await self.bridge.call_mcp_tool("command-runner.execute", {
                "command": "echo 'MCP Bridge Active'"
            })
            
            if result.get('exitCode') == 0:
                self.results.append({
                    'test': test_name,
                    'status': 'PASSED',
                    'message': 'Command executed successfully',
                    'output': result.get('output', '').strip()
                })
            else:
                self.results.append({
                    'test': test_name,
                    'status': 'FAILED',
                    'message': 'Command failed',
                    'result': result
                })
                
        except Exception as e:
            self.results.append({
                'test': test_name,
                'status': 'FAILED',
                'error': str(e)
            })
            
    async def test_cache_functionality(self):
        """Test response caching"""
        test_name = "Response Caching"
        test_path = "/etc/hosts"
        
        try:
            # First read (should hit MCP)
            start_time = asyncio.get_event_loop().time()
            result1 = await self.bridge.call_mcp_tool("filesystem.readFile", {
                "path": test_path
            })
            first_call_time = asyncio.get_event_loop().time() - start_time
            
            # Second read (should hit cache)
            start_time = asyncio.get_event_loop().time()
            result2 = await self.bridge.call_mcp_tool("filesystem.readFile", {
                "path": test_path
            })
            second_call_time = asyncio.get_event_loop().time() - start_time
            
            if result1 == result2 and second_call_time < first_call_time * 0.5:
                self.results.append({
                    'test': test_name,
                    'status': 'PASSED',
                    'message': 'Cache working correctly',
                    'first_call_ms': round(first_call_time * 1000, 2),
                    'cached_call_ms': round(second_call_time * 1000, 2)
                })
            else:
                self.results.append({
                    'test': test_name,
                    'status': 'WARNING',
                    'message': 'Cache may not be working optimally'
                })
                
        except Exception as e:
            self.results.append({
                'test': test_name,
                'status': 'FAILED',
                'error': str(e)
            })
            
    async def test_jump_code_integration(self):
        """Test jump code registration and execution"""
        test_name = "Jump Code Integration"
        
        try:
            # Create integrated squad
            squad = integrate_mcp_with_jump_codes()
            
            # Test jump code execution
            result = await squad.process_jump_code("@mcp_run_command:command=pwd")
            
            if result.get('type') == 'mcp_command_executed' and result.get('success'):
                self.results.append({
                    'test': test_name,
                    'status': 'PASSED',
                    'message': 'Jump code integration working',
                    'output': result.get('output', '').strip()
                })
            else:
                self.results.append({
                    'test': test_name,
                    'status': 'FAILED',
                    'message': 'Jump code execution failed',
                    'result': result
                })
                
        except Exception as e:
            self.results.append({
                'test': test_name,
                'status': 'FAILED',
                'error': str(e)
            })
            
    def print_results(self):
        """Print test results summary"""
        print("\n" + "="*60)
        print("MCP BRIDGE INTEGRATION TEST RESULTS")
        print("="*60 + "\n")
        
        passed = sum(1 for r in self.results if r['status'] == 'PASSED')
        failed = sum(1 for r in self.results if r['status'] == 'FAILED')
        warnings = sum(1 for r in self.results if r['status'] == 'WARNING')
        
        for result in self.results:
            status_symbol = {
                'PASSED': '✅',
                'FAILED': '❌',
                'WARNING': '⚠️'
            }.get(result['status'], '❓')
            
            print(f"{status_symbol} {result['test']}: {result['status']}")
            if 'message' in result:
                print(f"   {result['message']}")
            if 'error' in result:
                print(f"   Error: {result['error']}")
            if result['status'] == 'PASSED' and 'output' in result:
                print(f"   Output: {result['output']}")
            print()
            
        print("\n" + "-"*60)
        print(f"Total Tests: {len(self.results)}")
        print(f"Passed: {passed} | Failed: {failed} | Warnings: {warnings}")
        print(f"Success Rate: {(passed/len(self.results)*100):.1f}%")
        print("-"*60 + "\n")
        
        return failed == 0
        
    async def run_all_tests(self):
        """Run complete test suite"""
        await self.setup()
        
        # Run tests in sequence
        await self.test_connection()
        await self.test_file_operations()
        await self.test_command_execution()
        await self.test_cache_functionality()
        await self.test_jump_code_integration()
        
        await self.teardown()
        
        # Print results
        success = self.print_results()
        
        if success:
            print("🎉 All tests passed! MCP Bridge is fully operational.")
        else:
            print("⚠️  Some tests failed. Check the errors above.")
            
        return success

async def main():
    """Main test runner"""
    tester = MCPIntegrationTester()
    success = await tester.run_all_tests()
    
    # Exit with appropriate code
    sys.exit(0 if success else 1)

if __name__ == "__main__":
    print("\n🚀 Starting MCP Bridge Integration Tests...\n")
    print("Make sure Claude Desktop is running and MCP server is active.\n")
    
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\n\nTests interrupted by user.")
        sys.exit(1)
    except Exception as e:
        print(f"\n\nFatal error: {e}")
        sys.exit(1)
