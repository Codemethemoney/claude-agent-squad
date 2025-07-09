# Jump Codes vs MCP Tools - Understanding the Difference

## What You Have

### 1. Jump Codes (✅ Working)
- **What it is**: Your custom command system using `@` prefix
- **Where it runs**: In your Python application
- **Examples**: `@create_agent`, `@status`, `@parallel`
- **Status**: Fully functional and integrated

### 2. MCP Tools (✅ Available but ❌ Not Connected)
- **What it is**: Claude Desktop's Model Context Protocol tools
- **Where it runs**: In Claude Desktop environment
- **Examples**: `filesystem.readFile`, `command-runner.execute`
- **Status**: Referenced but not actually called by your code

## The Relationship

```
Your Computer
├── Claude Desktop
│   ├── MCP Tools (filesystem, command-runner, etc.)
│   └── This chat session (where I can use MCP tools)
│
└── Your Python Project (claude-agent-squad)
    ├── Jump Codes System (@commands)
    ├── Agent Squad
    └── mcp_bridge/ (empty - connection would go here)
```

## Current State

1. **Jump Codes** run in your Python app
2. **MCP Tools** run in Claude Desktop
3. They're **separate systems** that don't talk to each other
4. Your agents **reference** MCP tools but can't **use** them

## Example of the Disconnect

When your agent says it has tool `filesystem.readFile`:
```python
# In your code:
Agent(
    role="researcher",
    tools=["filesystem.readFile"]  # This is just a string!
)
```

This doesn't actually give the agent access to the MCP tool. It's like writing "I have a hammer" on a piece of paper - you've written it down, but you don't actually have the hammer.

## To Actually Connect Them

You would need:

1. **MCP Client Library**
   ```python
   from mcp_client import MCPConnection  # This doesn't exist yet
   mcp = MCPConnection("claude-desktop")
   ```

2. **Bridge in Jump Codes**
   ```python
   @jump_code("@read_via_mcp")
   def read_file_mcp(params, context):
       # Actually call MCP tool
       result = mcp.call("filesystem.readFile", {"path": params['path']})
       return result
   ```

3. **Agent Integration**
   ```python
   # Agents could then use jump codes that call MCP tools
   squad.process_jump_code("@read_via_mcp:path=/tmp/test.txt")
   ```

## Summary

- **Jump Codes**: Your working command system ✅
- **MCP Tools**: Claude Desktop's tools (I use them, your code doesn't) ⚠️
- **Connection**: Not implemented yet ❌

They're like having a TV (jump codes) and a cable box (MCP tools) that aren't connected with a cable yet!
