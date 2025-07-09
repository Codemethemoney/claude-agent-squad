# Jump Code Registry

## Overview

Jump codes are the rapid command system at the heart of Claude Agent Squad. They enable quick execution of complex operations through simple, memorable commands.

## Syntax

### Basic Format
```
@code:param1=value1,param2=value2
```

### Examples
```
@create_agent:role=developer,goal=write code
@status
@help:filter=agent
```

## Core Jump Codes

### System Management

| Code | Aliases | Description | Parameters |
|------|---------|-------------|------------|
| `@init` | - | Initialize system | `load_defaults`, `verbose` |
| `@status` | `@s`, `@stat` | Show system status | - |
| `@reset` | - | Reset to clean state | - |
| `@help` | `@h`, `@?` | Show help | `filter` |
| `@list` | `@ls`, `@l` | List all codes | - |

### Agent Management

| Code | Aliases | Description | Parameters |
|------|---------|-------------|------------|
| `@create_agent` | `@ca`, `@new_agent` | Create new agent | `role`*, `goal`*, `backstory`, `tools` |
| `@list_agents` | `@la`, `@agents` | List all agents | - |
| `@remove_agent` | `@ra` | Remove an agent | `agent_id`* |

### Task Management

| Code | Aliases | Description | Parameters |
|------|---------|-------------|------------|
| `@assign_task` | `@at`, `@task` | Assign task to agent | `agent`*, `task`*, `priority` |
| `@chain` | `@ch`, `@sequence` | Chain tasks | `tasks`* |
| `@list_tasks` | `@lt`, `@tasks` | List pending tasks | - |

### Workflow Execution

| Code | Aliases | Description | Parameters |
|------|---------|-------------|------------|
| `@run_workflow` | `@rw`, `@exec` | Execute workflow | `workflow`*, `async` |
| `@parallel` | `@par` | Run tasks in parallel | `tasks`*, `timeout`, `fail_fast` |

### State Management

| Code | Aliases | Description | Parameters |
|------|---------|-------------|------------|
| `@save_state` | `@save`, `@checkpoint` | Save state | `name`, `include` |
| `@restore_state` | `@restore`, `@load` | Restore state | `name`*, `partial` |
| `@switch_context` | `@sc`, `@ctx` | Switch context | `context`*, `preserve_state` |

### Debug & Development

| Code | Aliases | Description | Parameters |
|------|---------|-------------|------------|
| `@debug` | `@dbg`, `@d` | Enable debug mode | `agent`, `verbose`, `save_logs` |
| `@trace` | `@tr` | Enable tracing | `level`, `output` |
| `@profile` | `@perf`, `@p` | Profile performance | - |

### Templates & Macros

| Code | Aliases | Description | Parameters |
|------|---------|-------------|------------|
| `@template` | `@tpl`, `@t` | Apply template | `name`*, `agents` |
| `@define_macro` | `@macro`, `@m` | Define macro | `name`*, `sequence`*, `description` |
| `@exec_macro` | `@em`, `@run_macro` | Execute macro | `name`*, `params` |
| `@list_macros` | `@lm`, `@macros` | List macros | - |

*Parameters marked with * are required

## Advanced Usage

### Sequential Execution
Execute multiple jump codes in sequence:
```
@@create_agent:role=tester @@assign_task:agent=tester,task=run tests @@run_workflow
```

### Inline Jump Codes
Embed jump codes in text:
```
Let me {@status} check the system and then {@list_agents} show available agents.
```

### Macro Execution
Quick macro execution syntax:
```
!macro_name(param1=value1, param2=value2)
```

Example:
```
!quick_review(task_description=Review authentication module)
```

## Built-in Macros

### init_project
Initialize a new project with standard agents
```
!init_project
```
Expands to:
1. Create project manager agent
2. Create developer agent
3. Create tester agent
4. Apply full code review template

### quick_review
Quick code review workflow
```
!quick_review(task_description=Review PR #123)
```

### debug_all
Enable full debugging
```
!debug_all
```

### save_and_switch
Save state and switch context
```
!save_and_switch(checkpoint_name=before_deploy, new_context=production)
```

## Creating Custom Jump Codes

### Using the Decorator
```python
from jump_codes import create_jump_code_decorator

jump_code = create_jump_code_decorator(registry)

@jump_code(
    code="custom_code",
    description="My custom jump code",
    aliases=["cc"],
    context_required=["agents"],
    default_param="value"
)
def custom_handler(context, **kwargs):
    # Implementation
    return {"result": "success"}
```

### Direct Registration
```python
from jump_codes import JumpCode

registry.register(JumpCode(
    code="another_code",
    description="Another custom code",
    handler=my_handler_function,
    parameters={"param1": "default"},
    aliases=["ac"]
))
```

## Best Practices

### 1. Naming Conventions
- Use descriptive, action-oriented names
- Keep codes short but meaningful
- Use underscores for multi-word codes
- Provide intuitive aliases

### 2. Parameter Design
- Required parameters should be essential
- Provide sensible defaults for optional parameters
- Use consistent parameter names across codes
- Document parameter types and formats

### 3. Error Handling
- Validate all inputs
- Provide clear error messages
- Include recovery suggestions
- Log errors for debugging

### 4. Context Management
- Specify required context clearly
- Preserve context between related operations
- Clean up context when switching
- Document context dependencies

## Troubleshooting

### Common Issues

1. **"Unknown jump code" error**
   - Check spelling and syntax
   - Use `@list` to see available codes
   - Ensure code is registered

2. **"Missing required parameter" error**
   - Check parameter names
   - Provide all required parameters
   - Use `@help:filter=code_name` for details

3. **"Missing required context" error**
   - Ensure prerequisite operations completed
   - Check context requirements
   - Use `@status` to inspect context

### Debug Mode
Enable debug mode for detailed execution logs:
```
@debug:verbose=true,save_logs=true
```

### Execution Trace
Trace jump code execution:
```
@trace:level=debug,output=console
```

## Examples

### Complete Workflow Example
```bash
# Initialize system
@init

# Create agents
@create_agent:role=architect,goal=design system architecture
@create_agent:role=developer,goal=implement features
@create_agent:role=tester,goal=ensure quality

# Assign tasks
@chain:tasks=architect:design API,developer:implement endpoints,tester:write tests

# Run workflow
@run_workflow:workflow=api_development

# Save state
@save_state:name=api_v1_complete

# Check results
@status
```

### Error Recovery Example
```bash
# Save current state before risky operation
@save_state:name=before_migration

# Attempt operation
@run_workflow:workflow=database_migration

# If error occurs, restore state
@restore_state:name=before_migration
```

### Parallel Execution Example
```bash
# Run multiple analyses in parallel
@parallel:tasks=analyze_security;check_performance;validate_schema,timeout=300
```

## Performance Tips

1. **Use macros for repeated sequences**
   - Define common workflows as macros
   - Reduces typing and errors
   - Improves consistency

2. **Batch operations when possible**
   - Use `@chain` for sequential tasks
   - Use `@parallel` for independent tasks
   - Minimize context switches

3. **Monitor performance**
   - Use `@profile` for bottleneck identification
   - Check `@status` for resource usage
   - Enable selective debugging

## Security Considerations

1. **Parameter Validation**
   - All inputs are sanitized
   - Path traversal prevented
   - Command injection blocked

2. **Access Control**
   - Context-based permissions
   - Operation confirmation for destructive actions
   - Audit logging enabled

3. **State Protection**
   - Encrypted state storage
   - Versioned checkpoints
   - Rollback capabilities

---

*For more information, see the [Implementation Guide](./implementation_guide.md) or consult the main [Project Overview](../00_project_overview.md).*
