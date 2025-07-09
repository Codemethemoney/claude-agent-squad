# Jump Codes Implementation Guide

## Overview

This guide provides detailed instructions for implementing and extending the Jump Codes system in Claude Agent Squad.

## Core Components

### 1. JumpCode Class
The fundamental building block representing a single jump code.

```python
@dataclass
class JumpCode:
    code: str                    # Unique identifier
    description: str             # Human-readable description
    handler: Callable           # Function to execute
    parameters: Dict[str, Any]  # Default parameters
    aliases: List[str] = None   # Alternative names
    context_required: List[str] = None  # Required context keys
```

### 2. JumpCodeRegistry
Central registry managing all jump codes.

```python
class JumpCodeRegistry:
    def __init__(self):
        self.codes: Dict[str, JumpCode] = {}
        self.aliases: Dict[str, str] = {}
        self._initialize_core_codes()
    
    def register(self, jump_code: JumpCode):
        # Registration logic
    
    def execute(self, code_string: str, context: Dict[str, Any] = None):
        # Execution logic
```

### 3. EnhancedAgentSquad
Integration layer connecting jump codes with the agent system.

```python
class EnhancedAgentSquad:
    def __init__(self):
        self.jump_registry = JumpCodeRegistry()
        self.agents = {}
        self.current_context = {}
        self._register_squad_jump_codes()
```

## Implementation Steps

### Step 1: Basic Jump Code Creation

```python
# Simple jump code without parameters
def hello_handler(context: Dict[str, Any], **kwargs):
    return {
        'type': 'greeting',
        'message': 'Hello from jump code!'
    }

hello_code = JumpCode(
    code="hello",
    description="Simple greeting",
    handler=hello_handler,
    parameters={}
)
registry.register(hello_code)
```

### Step 2: Jump Code with Parameters

```python
def greet_handler(context: Dict[str, Any], name: str = "World", **kwargs):
    return {
        'type': 'greeting',
        'message': f'Hello, {name}!'
    }

greet_code = JumpCode(
    code="greet",
    description="Personalized greeting",
    handler=greet_handler,
    parameters={"name": "World"},  # Default value
    aliases=["g", "hi"]
)
registry.register(greet_code)
```

### Step 3: Context-Aware Jump Code

```python
def task_status_handler(context: Dict[str, Any], **kwargs):
    # Requires 'tasks' in context
    tasks = context.get('tasks', [])
    pending = [t for t in tasks if t['status'] == 'pending']
    
    return {
        'type': 'task_status',
        'total_tasks': len(tasks),
        'pending_tasks': len(pending),
        'message': f"{len(pending)} tasks pending"
    }

status_code = JumpCode(
    code="task_status",
    description="Show task status",
    handler=task_status_handler,
    parameters={},
    context_required=["tasks"]  # Will validate before execution
)
```

### Step 4: Async Jump Code

```python
async def async_analysis_handler(context: Dict[str, Any], **kwargs):
    # Long-running operation
    import asyncio
    await asyncio.sleep(2)  # Simulate work
    
    return {
        'type': 'analysis_complete',
        'result': 'Analysis finished'
    }

# Wrap async handler
def analysis_handler(context: Dict[str, Any], **kwargs):
    import asyncio
    loop = asyncio.get_event_loop()
    return loop.run_until_complete(async_analysis_handler(context, **kwargs))
```

## Advanced Patterns

### 1. Chained Jump Codes

```python
def chain_handler(context: Dict[str, Any], codes: List[str], **kwargs):
    results = []
    
    for code in codes:
        try:
            result = context['registry'].execute(code, context)
            results.append(result)
            
            # Update context with result
            if isinstance(result, dict):
                context.update(result)
        except Exception as e:
            results.append({'error': str(e)})
            break
    
    return {
        'type': 'chain_execution',
        'results': results
    }
```

### 2. Conditional Jump Codes

```python
def conditional_handler(context: Dict[str, Any], 
                      condition: str, 
                      if_true: str, 
                      if_false: str = None, 
                      **kwargs):
    # Evaluate condition
    try:
        # Safe evaluation of simple conditions
        result = eval(condition, {"__builtins__": {}}, context)
        
        if result:
            return context['registry'].execute(if_true, context)
        elif if_false:
            return context['registry'].execute(if_false, context)
        else:
            return {'type': 'condition_false', 'message': 'Condition not met'}
    except Exception as e:
        return {'error': f'Invalid condition: {e}'}
```

### 3. Batch Operations

```python
def batch_create_agents_handler(context: Dict[str, Any], 
                              agents_spec: List[Dict], 
                              **kwargs):
    created_agents = []
    
    for spec in agents_spec:
        try:
            result = context['registry'].execute(
                f"@create_agent:role={spec['role']},goal={spec['goal']}", 
                context
            )
            created_agents.append(result)
        except Exception as e:
            logger.error(f"Failed to create agent: {e}")
    
    return {
        'type': 'batch_creation',
        'created': len(created_agents),
        'agents': created_agents
    }
```

## Error Handling

### 1. Input Validation

```python
def validate_parameters(params: Dict[str, Any], required: List[str]) -> None:
    """Validate required parameters are present"""
    missing = [p for p in required if p not in params or params[p] is None]
    if missing:
        raise ValueError(f"Missing required parameters: {missing}")
```

### 2. Safe Execution

```python
def safe_execute(self, code_string: str, context: Dict[str, Any] = None):
    """Execute with comprehensive error handling"""
    try:
        # Pre-execution validation
        if not self._validate_code_format(code_string):
            return {'error': 'Invalid code format'}
        
        # Execute
        result = self.execute(code_string, context)
        
        # Post-execution validation
        if not isinstance(result, dict):
            result = {'result': result}
        
        return result
        
    except ValueError as e:
        return {'error': f'Validation error: {e}'}
    except Exception as e:
        logger.exception("Unexpected error in jump code execution")
        return {'error': f'Execution error: {e}'}
```

### 3. Recovery Mechanisms

```python
def with_recovery(self, code_string: str, context: Dict[str, Any] = None):
    """Execute with automatic recovery"""
    checkpoint = context.copy() if context else {}
    
    try:
        return self.execute(code_string, context)
    except Exception as e:
        # Restore context
        context.clear()
        context.update(checkpoint)
        
        # Try recovery action
        recovery_code = f"@restore_state:name=last_stable"
        try:
            self.execute(recovery_code, context)
        except:
            pass
        
        return {'error': str(e), 'recovered': True}
```

## Testing Jump Codes

### 1. Unit Testing

```python
import unittest
from unittest.mock import Mock, patch

class TestJumpCodes(unittest.TestCase):
    def setUp(self):
        self.registry = JumpCodeRegistry()
        self.context = {'test': True}
    
    def test_basic_execution(self):
        result = self.registry.execute("@status", self.context)
        self.assertEqual(result['type'], 'status')
        self.assertIn('total_codes', result)
    
    def test_parameter_parsing(self):
        result = self.registry.execute(
            "@create_agent:role=tester,goal=test code", 
            self.context
        )
        self.assertEqual(result.get('role'), 'tester')
    
    def test_error_handling(self):
        result = self.registry.execute("@invalid_code", self.context)
        self.assertIn('error', result)
```

### 2. Integration Testing

```python
def test_workflow_integration():
    """Test complete workflow using jump codes"""
    squad = EnhancedAgentSquad()
    
    # Create agents
    squad.process_jump_code("@create_agent:role=developer,goal=write code")
    squad.process_jump_code("@create_agent:role=tester,goal=test code")
    
    # Assign tasks
    squad.process_jump_code("@chain:tasks=developer:implement feature,tester:test feature")
    
    # Run workflow
    result = squad.process_jump_code("@run_workflow:workflow=development")
    
    assert result['type'] == 'workflow_completed'
```

## Performance Optimization

### 1. Caching Frequently Used Codes

```python
from functools import lru_cache

class CachedRegistry(JumpCodeRegistry):
    @lru_cache(maxsize=128)
    def _parse_jump_code(self, code_string: str) -> Dict[str, Any]:
        return super()._parse_jump_code(code_string)
```

### 2. Lazy Loading

```python
class LazyLoadRegistry(JumpCodeRegistry):
    def __init__(self):
        super().__init__()
        self._lazy_codes = {}
    
    def register_lazy(self, code: str, loader: Callable):
        """Register a code that loads on first use"""
        self._lazy_codes[code] = loader
    
    def execute(self, code_string: str, context: Dict[str, Any] = None):
        parsed = self._parse_jump_code(code_string)
        code_name = parsed['code']
        
        # Load lazy code if needed
        if code_name in self._lazy_codes and code_name not in self.codes:
            jump_code = self._lazy_codes[code_name]()
            self.register(jump_code)
        
        return super().execute(code_string, context)
```

### 3. Parallel Execution

```python
import concurrent.futures
from typing import List, Tuple

def execute_parallel(self, codes: List[str], context: Dict[str, Any] = None):
    """Execute multiple jump codes in parallel"""
    with concurrent.futures.ThreadPoolExecutor(max_workers=5) as executor:
        # Submit all tasks
        futures = {
            executor.submit(self.execute, code, context.copy()): code 
            for code in codes
        }
        
        # Collect results
        results = []
        for future in concurrent.futures.as_completed(futures):
            code = futures[future]
            try:
                result = future.result()
                results.append((code, result))
            except Exception as e:
                results.append((code, {'error': str(e)}))
        
        return results
```

## Security Considerations

### 1. Input Sanitization

```python
def sanitize_code_string(code_string: str) -> str:
    """Remove potentially dangerous characters"""
    # Remove shell metacharacters
    dangerous_chars = ';|&$`\\'
    for char in dangerous_chars:
        code_string = code_string.replace(char, '')
    
    # Limit length
    max_length = 500
    if len(code_string) > max_length:
        code_string = code_string[:max_length]
    
    return code_string
```

### 2. Permission Checking

```python
def check_permissions(self, code: str, context: Dict[str, Any]) -> bool:
    """Check if code execution is allowed"""
    user_role = context.get('user_role', 'guest')
    
    # Define permission levels
    permissions = {
        'guest': ['status', 'help', 'list'],
        'user': ['create_agent', 'assign_task', 'run_workflow'],
        'admin': ['reset', 'debug', 'delete']
    }
    
    allowed_codes = []
    for role in ['guest', 'user', 'admin']:
        allowed_codes.extend(permissions[role])
        if role == user_role:
            break
    
    return code in allowed_codes
```

### 3. Audit Logging

```python
import json
from datetime import datetime

def audit_log(self, code_string: str, context: Dict[str, Any], result: Dict[str, Any]):
    """Log jump code execution for audit"""
    log_entry = {
        'timestamp': datetime.now().isoformat(),
        'code': code_string,
        'user': context.get('user_id', 'anonymous'),
        'success': 'error' not in result,
        'result_type': result.get('type', 'unknown')
    }
    
    # Write to audit log
    with open('jump_code_audit.log', 'a') as f:
        f.write(json.dumps(log_entry) + '\n')
```

## Debugging Tools

### 1. Interactive Debugger

```python
def debug_jump_code(self, code_string: str, context: Dict[str, Any] = None):
    """Interactive debugging for jump codes"""
    import pdb
    
    print(f"Debugging: {code_string}")
    print(f"Context keys: {list(context.keys()) if context else []}")
    
    # Set breakpoint
    pdb.set_trace()
    
    # Execute with full trace
    import sys
    import trace
    
    tracer = trace.Trace(trace=True)
    result = tracer.runfunc(self.execute, code_string, context)
    
    return result
```

### 2. Execution Profiler

```python
import cProfile
import pstats
from io import StringIO

def profile_jump_code(self, code_string: str, context: Dict[str, Any] = None):
    """Profile jump code execution"""
    profiler = cProfile.Profile()
    
    # Profile execution
    profiler.enable()
    result = self.execute(code_string, context)
    profiler.disable()
    
    # Format results
    stream = StringIO()
    stats = pstats.Stats(profiler, stream=stream)
    stats.sort_stats('cumulative')
    stats.print_stats(10)  # Top 10 functions
    
    return {
        'result': result,
        'profile': stream.getvalue()
    }
```

## Best Practices Summary

1. **Keep handlers focused** - Each jump code should do one thing well
2. **Use consistent naming** - Follow the established patterns
3. **Document thoroughly** - Include examples and edge cases
4. **Test comprehensively** - Unit and integration tests
5. **Handle errors gracefully** - Always return structured responses
6. **Log important operations** - For debugging and audit
7. **Optimize for common cases** - Cache and lazy load when appropriate
8. **Secure by default** - Validate inputs and check permissions

---

*For the complete jump code reference, see [Jump Code Registry](./jump_code_registry.md).*
