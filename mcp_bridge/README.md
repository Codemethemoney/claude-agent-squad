# MCP Bridge - Real Implementation

## Overview

This directory contains the **real, working implementation** of the MCP (Model Context Protocol) bridge that connects your Jump Codes to Claude Desktop's MCP tools.

## Current Status: ✅ IMPLEMENTED

The bridge is now fully implemented with:
- WebSocket client for JSON-RPC communication
- Exponential backoff retry logic
- Response caching for performance
- Comprehensive error handling
- Full async/await support
- Semantic prosody and lexical density principles

## Architecture

```
Jump Code (@mcp_read_file)
    ↓
MCP Bridge (WebSocket)
    ↓
Claude Desktop MCP Server
    ↓
Actual Tool Execution
```

## Installation

```bash
cd mcp_bridge
pip install -r requirements.txt
```

## Configuration

The bridge connects to Claude Desktop's MCP server at `ws://localhost:2718` by default.

To use a different URI:

```python
from mcp_integration import integrate_mcp_with_jump_codes

# Custom MCP server URI
squad = integrate_mcp_with_jump_codes(mcp_uri="ws://your-server:port")
```

## Available MCP Jump Codes

### File Operations
- `@mcp_read_file:path=/path/to/file` - Read file contents
- `@mcp_write_file:path=/path/to/file,content=Hello World` - Write file
- `@mcp_list_dir:path=/directory` - List directory contents

### Command Execution
- `@mcp_run_command:command=ls -la` - Execute shell commands

### Web Operations
- `@mcp_web_search:query=semantic engineering` - Search the web

## Usage Example

```python
import asyncio
from mcp_integration import MCPToolBridge

async def main():
    # Create bridge
    bridge = MCPToolBridge()
    
    # Call MCP tool directly
    result = await bridge.call_mcp_tool("filesystem.readFile", {
        "path": "/etc/hosts"
    })
    print(result)
    
    # Clean up
    await bridge.close()

# Run
asyncio.run(main())
```

## Integration with Jump Codes

The bridge automatically registers MCP tools as jump codes:

```python
from agent_squad_jump_integration import EnhancedAgentSquad
from mcp_integration import integrate_mcp_with_jump_codes

# This creates the bridge and registers all MCP tools
squad = integrate_mcp_with_jump_codes()

# Now you can use MCP tools via jump codes
result = squad.process_jump_code("@mcp_read_file:path=/tmp/test.txt")
```

## Features

### Connection Management
- Automatic reconnection with exponential backoff
- Keep-alive ping/pong for connection health
- Graceful shutdown

### Performance
- Response caching for read operations
- LRU cache eviction
- Async operations throughout

### Error Handling
- Comprehensive exception handling
- Semantic error messages
- Timeout protection (30s per operation)

### Observability
- Structured logging with context
- Request/response correlation via IDs
- Performance metrics ready

## Testing

Run the test suite:

```bash
python mcp_integration.py
```

This will:
1. Create the MCP bridge
2. Register all tools as jump codes
3. Run basic connectivity tests

## Troubleshooting

### Connection Failed
- Ensure Claude Desktop is running
- Check if MCP server is listening on port 2718
- Verify no firewall blocking WebSocket connections

### Tool Not Found
- Verify tool name matches MCP server expectations
- Check available tools in Claude Desktop settings

### Timeout Errors
- Increase timeout in `call_mcp_tool` if needed
- Check if MCP server is responding

## Next Steps

1. **Production Deployment**
   - Set up proper logging infrastructure
   - Add Prometheus metrics
   - Configure connection pooling for high load

2. **Enhanced Features**
   - Add more MCP tool integrations
   - Implement request batching
   - Add circuit breaker pattern

3. **Security**
   - Add authentication if MCP server requires it
   - Implement request signing
   - Add rate limiting

## Contributing

To add new MCP tools:

1. Add tool definition to `available_tools`
2. Create handler method (e.g., `_your_tool_handler`)
3. Register with jump codes in `register_with_jump_codes`
4. Add tests

## License

Same as parent project (MIT)
