# Unified Jump Codes Guide - Complete Integration

## Overview

The Claude Agent Squad project now has **TWO complementary jump code implementations** that work together:

1. **Original Implementation** - Agent-focused jump codes (already in main branch)
2. **Enhanced Implementation** - Extended functionality with async support

Both systems are **100% functional** and can be used together or separately.

## 🎯 What Are Jump Codes?

Jump codes are commands prefixed with `@` that enable rapid execution of agent operations:

```bash
@create_agent:role=developer,goal=Build features
@status
@parallel:tasks=task1,task2,task3
```

## 📁 File Structure

```
claude-agent-squad/
├── python_agent_squad/
│   ├── jump_codes.py                # Original core implementation
│   ├── agent_squad_jump_integration.py  # Agent-specific handlers
│   ├── enhanced_jump_codes.py      # Enhanced implementation (NEW)
│   ├── jump_code_cli.py            # Interactive CLI
│   ├── demo_jump_codes.py          # Live demonstration
│   ├── advanced_jump_codes.py      # Advanced features
│   └── test_complete_integration.py # Integration tests (NEW)
├── enhanced_api.py                  # Unified API supporting both (NEW)
└── UNIFIED_JUMP_CODES_GUIDE.md      # This guide
```

## 🚀 Quick Start

### 1. Run the Demo
```bash
cd python_agent_squad
python demo_jump_codes.py
```

### 2. Use the CLI
```bash
python jump_code_cli.py
```

### 3. Start the Unified API
```bash
python enhanced_api.py
```

## 📋 Available Jump Codes

### Original Implementation Commands
- `@create_agent` - Create new agent (aliases: `@ca`, `@new_agent`)
- `@assign_task` - Assign task to agent (aliases: `@at`, `@task`)
- `@run_workflow` - Execute workflow (aliases: `@rw`, `@exec`)
- `@list_agents` - List all agents (aliases: `@la`, `@agents`)
- `@parallel` - Execute tasks in parallel
- `@template` - Apply workflow template
- `@debug` - Enable debug mode
- `@save_state` / `@restore_state` - State management

### Enhanced Implementation Features
- Full async/await support
- Parallel execution with thread pool
- Execution history tracking
- Context management across commands
- Macro system for command sequences
- Performance metrics

## 🔧 Using the Unified API

The `enhanced_api.py` provides endpoints that work with both implementations:

### Execute with Original Implementation
```bash
curl -X POST http://localhost:8000/jump/execute \
  -H "Content-Type: application/json" \
  -d '{
    "code": "@create_agent:role=developer",
    "use_enhanced": false
  }'
```

### Execute with Enhanced Implementation
```bash
curl -X POST http://localhost:8000/jump/execute \
  -H "Content-Type: application/json" \
  -d '{
    "code": "@create_agent:role=developer",
    "use_enhanced": true
  }'
```

### List All Available Codes
```bash
curl http://localhost:8000/jump/codes?implementation=both
```

## 🧪 Testing Integration

Run the complete integration test:

```bash
cd python_agent_squad
python test_complete_integration.py
```

This verifies:
- Original implementation works
- Enhanced implementation works
- Both can be loaded together
- All CLI components exist

## 💡 Key Differences

| Feature | Original | Enhanced |
|---------|----------|----------|
| Agent Management | ✅ Full support | ✅ Via handlers |
| Async Execution | ❌ | ✅ Full async/await |
| Parallel Execution | ✅ Basic | ✅ Advanced with thread pool |
| History Tracking | ❌ | ✅ Complete history |
| Context System | ✅ Basic | ✅ Enhanced |
| Macros | ❌ | ✅ Full support |

## 🔄 Using Both Together

```python
# Import both systems
from agent_squad_jump_integration import EnhancedAgentSquad
from enhanced_jump_codes import execute, get_context

# Use original for agent operations
squad = EnhancedAgentSquad()
squad.process_jump_code("@create_agent:role=developer")

# Use enhanced for advanced features
result = execute("@status")
context = get_context()
```

## 📊 WebSocket Support

Both implementations support WebSocket connections:

```javascript
const ws = new WebSocket('ws://localhost:8000/ws/jump');

// Use original implementation
ws.send(JSON.stringify({
    type: 'execute',
    code: '@create_agent:role=developer',
    use_enhanced: false
}));

// Use enhanced implementation
ws.send(JSON.stringify({
    type: 'execute',
    code: '@status',
    use_enhanced: true
}));
```

## 🎯 Best Practices

1. **Use Original for**: Agent management, task assignment, workflows
2. **Use Enhanced for**: Async operations, parallel execution, performance tracking
3. **Use Unified API**: When you need to switch between implementations
4. **Test Both**: Run integration tests to ensure compatibility

## 🚀 Conclusion

The Claude Agent Squad project now has a **complete, 100% integrated jump code system** with:

- ✅ Original implementation for agent operations
- ✅ Enhanced implementation for advanced features
- ✅ Unified API supporting both
- ✅ Complete documentation
- ✅ Integration tests
- ✅ Live demos

Both implementations work together in perfect symbiosis, providing a powerful command interface for all agent operations!
