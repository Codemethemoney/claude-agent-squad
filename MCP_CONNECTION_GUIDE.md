# Connecting Jump Codes to Claude Desktop MCP Tools

## Current Situation

Your Claude Agent Squad has:
- ✅ Jump code system (working)
- ✅ Agent management (working)
- ✅ References to MCP tools in agent configs
- ❌ Actual connection to Claude Desktop MCP tools

## MCP Tools Your Agents Want to Use

Based on your code, agents are configured for these MCP tools:

1. **filesystem**
   - `readFile` - Read files from disk
   - `writeFile` - Write files to disk

2. **command-runner**
   - Execute shell commands

3. **rag-web-browser**
   - Browse web pages

4. **web_search**
   - Search the web

## How to Connect

### Option 1: Direct MCP Integration

If you have access to MCP protocol/API:

```python
# In mcp_bridge/mcp_client.py
import mcp_client  # hypothetical MCP client library

class MCPConnection:
    def __init__(self):
        self.client = mcp_client.connect("claude-desktop")
    
    async def call_tool(self, tool_name, params):
        return await self.client.invoke(tool_name, params)
```

### Option 2: Use Jump Codes as MCP Tool Wrappers

Since you can use MCP tools in this Claude Desktop session, you could:

1. Create jump codes that map to MCP tool calls
2. When a jump code is executed, it triggers the corresponding MCP tool
3. Results flow back through the jump code system

Example integration:

```python
@jump_code("@mcp_read", aliases=["@read"])
def mcp_read_file(params, context):
    """Use Claude Desktop's filesystem.readFile"""
    path = params.get('path')
    # This would call the actual MCP tool
    # For now, it's a placeholder
    return {
        'tool': 'filesystem.readFile',
        'path': path,
        'content': 'Would read from MCP'
    }
```

### Option 3: HTTP Bridge

Create an HTTP server that:
1. Receives jump code commands
2. Translates them to MCP tool calls
3. Returns results

```python
# api_mcp_bridge.py
@app.post("/mcp/tool")
async def call_mcp_tool(tool: str, params: dict):
    # Forward to MCP
    result = await mcp_connection.call(tool, params)
    return result
```

## Current Workaround

Since MCP tools aren't connected yet, the agents currently:
- Reference MCP tools in their configuration
- But don't actually call them
- Would need the bridge to be implemented

## What You'd Need

To complete the connection:

1. **MCP Client Library** or API documentation
2. **Authentication** method for Claude Desktop
3. **Network details** (if MCP uses sockets/HTTP)
4. **Tool schemas** for proper parameter passing

## Quick Test

To see if MCP connection is possible, you could:

```python
# In jump_code_cli.py, add:
@jump_code("@test_mcp")
def test_mcp_connection(params, context):
    """Test if we can call MCP tools"""
    try:
        # Attempt to use filesystem.readFile
        # This would need actual MCP client code
        result = "MCP connection not implemented yet"
    except Exception as e:
        result = f"MCP error: {e}"
    
    return {'test': 'mcp_connection', 'result': result}
```

## Summary

Your jump codes system is **ready** to connect to MCP tools, but needs:
- The actual MCP client/protocol implementation
- Authentication setup
- Network configuration

The infrastructure is there - it just needs the connection layer to be implemented!
