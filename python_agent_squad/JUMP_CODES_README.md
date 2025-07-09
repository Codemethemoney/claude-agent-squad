# Jump Codes System for Claude Agent Squad

## 🚀 Quick Start

The Jump Codes system provides rapid command execution for agent and task management in Claude Agent Squad.

### Running the Interactive CLI

```bash
cd python_agent_squad
python jump_code_cli.py
```

### Basic Commands

```bash
# Create an agent
@create_agent:role=developer,goal=write clean code

# List all agents
@list_agents

# Assign a task
@assign_task:agent=agent_1,task=implement authentication

# Run workflow
@run_workflow:workflow=development

# Check status
@status
```

## 📚 Jump Code Reference

### System Commands
- `@init` - Initialize system
- `@status` or `@s` - Show system status
- `@help` or `@h` - Show available commands
- `@list` or `@ls` - List all jump codes

### Agent Management
- `@create_agent` or `@ca` - Create new agent
- `@list_agents` or `@la` - List all agents
- `@remove_agent` or `@ra` - Remove an agent

### Task Management
- `@assign_task` or `@at` - Assign task to agent
- `@chain` or `@ch` - Chain multiple tasks
- `@parallel` or `@par` - Execute tasks in parallel

### State Management
- `@save_state` or `@save` - Save current state
- `@restore_state` or `@restore` - Restore saved state
- `@switch_context` or `@sc` - Switch context

### Debug & Development
- `@debug` or `@dbg` - Enable debug mode
- `@template` or `@tpl` - Apply workflow template

## 🎯 Advanced Features

### Sequential Execution
Execute multiple commands in sequence:
```bash
@@create_agent:role=tester @@assign_task:agent=tester,task=run tests @@run_workflow
```

### Macros
Execute predefined workflows:
```bash
!quick_review(task_description=Review PR #123)
```

### Inline Jump Codes
Embed commands in text:
```bash
Let me {@status} and then {@list_agents} to see what's available.
```

## 📝 Examples

### Complete Workflow Example
```python
# 1. Initialize
@init

# 2. Create team
@create_agent:role=architect,goal=design system
@create_agent:role=developer,goal=implement features
@create_agent:role=tester,goal=ensure quality

# 3. Assign tasks
@chain:tasks=architect:design API,developer:implement endpoints,tester:write tests

# 4. Run workflow
@run_workflow:workflow=api_development

# 5. Save checkpoint
@save_state:name=api_v1_complete
```

### Parallel Testing Example
```python
@parallel:tasks=agent_1:test auth;agent_2:test UI;agent_3:test database,timeout=300
```

## 🛠️ Running Examples

```bash
# Run all examples
python example_usage.py

# Run specific example
python example_usage.py basic
python example_usage.py tasks
python example_usage.py sequential
python example_usage.py macros
python example_usage.py parallel
```

## 🧪 Testing

```bash
python test_jump_codes.py
```

## 📁 File Structure

```
python_agent_squad/
├── jump_codes.py                    # Core jump code engine
├── agent_squad_jump_integration.py  # Agent squad integration
├── advanced_jump_codes.py           # Advanced features (macros, sequences)
├── jump_codes_config.yaml          # Configuration file
├── jump_code_cli.py                # Interactive CLI
├── example_usage.py                # Usage examples
└── test_jump_codes.py              # Test suite
```

## ⚙️ Configuration

Edit `jump_codes_config.yaml` to:
- Add custom jump codes
- Define new macros
- Modify execution settings
- Customize interface options

## 🎨 Creating Custom Jump Codes

```python
from jump_codes import JumpCode

# Register a custom jump code
squad.jump_registry.register(JumpCode(
    code="my_custom_code",
    description="Does something special",
    handler=my_handler_function,
    parameters={"param1": "default"},
    aliases=["mcc"]
))
```

## 🚨 Troubleshooting

1. **"Unknown jump code" error** - Check spelling or use `@list` to see available codes
2. **"Missing required parameter"** - Check required parameters with `@help:filter=code_name`
3. **"No agents available"** - Create agents first with `@create_agent`

## 📖 Full Documentation

See the knowledge base in `claude-agent-squad-knowledge/05_jump_codes/` for:
- Complete jump code registry
- Implementation guide
- Architecture details
