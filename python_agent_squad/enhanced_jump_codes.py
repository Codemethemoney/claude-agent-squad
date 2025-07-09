"""
Enhanced Jump Codes System - Core Infrastructure
Provides an enhanced command processing system with @ prefix for agent operations
This is an alternative implementation with additional features
"""

import re
import json
import asyncio
from typing import Dict, List, Any, Callable, Optional, Union
from dataclasses import dataclass
from datetime import datetime
import inspect
from concurrent.futures import ThreadPoolExecutor

@dataclass
class JumpCodeResult:
    """Result of executing a jump code"""
    success: bool
    data: Any = None
    error: Optional[str] = None
    execution_time: float = 0.0
    timestamp: datetime = None

    def __post_init__(self):
        if self.timestamp is None:
            self.timestamp = datetime.now()

class EnhancedJumpCodeRegistry:
    """Enhanced registry for all jump codes in the system"""
    
    def __init__(self):
        self.codes: Dict[str, Callable] = {}
        self.aliases: Dict[str, str] = {}
        self.macros: Dict[str, List[str]] = {}
        self.execution_history: List[Dict] = []
        
    def register(self, pattern: str, handler: Callable, aliases: List[str] = None):
        """Register a jump code handler"""
        self.codes[pattern] = handler
        if aliases:
            for alias in aliases:
                self.aliases[alias] = pattern
                
    def register_macro(self, name: str, commands: List[str]):
        """Register a macro that executes multiple jump codes"""
        self.macros[name] = commands
        
    def get_handler(self, code: str) -> Optional[Callable]:
        """Get handler for a jump code"""
        # Check if it's an alias
        if code in self.aliases:
            code = self.aliases[code]
        
        # Find matching pattern
        for pattern, handler in self.codes.items():
            if re.match(pattern, code):
                return handler
        return None
        
    def list_codes(self) -> List[str]:
        """List all registered jump codes"""
        return list(self.codes.keys()) + list(self.aliases.keys())

class EnhancedJumpCodeProcessor:
    """Enhanced processor for jump codes"""
    
    def __init__(self):
        self.registry = EnhancedJumpCodeRegistry()
        self.context = {}
        self.executor = ThreadPoolExecutor(max_workers=10)
        
    def parse_jump_code(self, code: str) -> Dict[str, Any]:
        """Parse a jump code into components"""
        if not code.startswith('@'):
            raise ValueError(f"Jump code must start with @: {code}")
            
        # Extract code name and parameters
        match = re.match(r'@(\w+)(?::(.+))?', code)
        if not match:
            raise ValueError(f"Invalid jump code format: {code}")
            
        name = match.group(1)
        params_str = match.group(2) or ""
        
        # Parse parameters
        params = {}
        if params_str:
            # Handle key=value pairs
            for param in params_str.split(','):
                if '=' in param:
                    key, value = param.split('=', 1)
                    params[key.strip()] = value.strip()
                else:
                    params['value'] = param.strip()
                    
        return {
            'name': name,
            'params': params,
            'raw': code
        }
        
    async def execute_async(self, code: str) -> JumpCodeResult:
        """Execute a jump code asynchronously"""
        start_time = datetime.now()
        
        try:
            parsed = self.parse_jump_code(code)
            handler = self.registry.get_handler(f"@{parsed['name']}")
            
            if not handler:
                # Check if it's a macro
                if parsed['name'] in self.registry.macros:
                    return await self.execute_macro(parsed['name'])
                return JumpCodeResult(False, error=f"Unknown jump code: {code}")
            
            # Execute handler
            if inspect.iscoroutinefunction(handler):
                result = await handler(parsed['params'], self.context)
            else:
                result = await asyncio.get_event_loop().run_in_executor(
                    self.executor, handler, parsed['params'], self.context
                )
            
            execution_time = (datetime.now() - start_time).total_seconds()
            
            # Log execution
            self.execution_history.append({
                'code': code,
                'timestamp': datetime.now(),
                'success': True,
                'execution_time': execution_time
            })
            
            return JumpCodeResult(True, data=result, execution_time=execution_time)
            
        except Exception as e:
            execution_time = (datetime.now() - start_time).total_seconds()
            self.execution_history.append({
                'code': code,
                'timestamp': datetime.now(),
                'success': False,
                'error': str(e),
                'execution_time': execution_time
            })
            return JumpCodeResult(False, error=str(e), execution_time=execution_time)
            
    def execute(self, code: str) -> JumpCodeResult:
        """Execute a jump code synchronously"""
        return asyncio.run(self.execute_async(code))
        
    async def execute_macro(self, macro_name: str) -> JumpCodeResult:
        """Execute a macro (sequence of jump codes)"""
        if macro_name not in self.registry.macros:
            return JumpCodeResult(False, error=f"Unknown macro: {macro_name}")
            
        results = []
        for command in self.registry.macros[macro_name]:
            result = await self.execute_async(command)
            results.append(result)
            if not result.success:
                return JumpCodeResult(False, error=f"Macro failed at: {command}", data=results)
                
        return JumpCodeResult(True, data=results)
        
    async def execute_parallel(self, codes: List[str]) -> List[JumpCodeResult]:
        """Execute multiple jump codes in parallel"""
        tasks = [self.execute_async(code) for code in codes]
        return await asyncio.gather(*tasks)
        
    def execute_sequential(self, codes: List[str]) -> List[JumpCodeResult]:
        """Execute multiple jump codes sequentially"""
        results = []
        for code in codes:
            result = self.execute(code)
            results.append(result)
            if not result.success:
                break
        return results

# Global processor instance
_processor = EnhancedJumpCodeProcessor()

def jump_code(pattern: str, aliases: List[str] = None):
    """Decorator to register a function as a jump code handler"""
    def decorator(func):
        _processor.registry.register(pattern, func, aliases)
        return func
    return decorator

def register_macro(name: str, commands: List[str]):
    """Register a macro"""
    _processor.registry.register_macro(name, commands)

def execute(code: str) -> JumpCodeResult:
    """Execute a jump code"""
    return _processor.execute(code)

async def execute_async(code: str) -> JumpCodeResult:
    """Execute a jump code asynchronously"""
    return await _processor.execute_async(code)

def execute_parallel(codes: List[str]) -> List[JumpCodeResult]:
    """Execute multiple jump codes in parallel"""
    return asyncio.run(_processor.execute_parallel(codes))

def execute_sequential(codes: List[str]) -> List[JumpCodeResult]:
    """Execute multiple jump codes sequentially"""
    return _processor.execute_sequential(codes)

def get_context() -> Dict[str, Any]:
    """Get the current execution context"""
    return _processor.context

def set_context(key: str, value: Any):
    """Set a value in the execution context"""
    _processor.context[key] = value

def list_jump_codes() -> List[str]:
    """List all available jump codes"""
    return _processor.registry.list_codes()

def get_execution_history() -> List[Dict]:
    """Get the execution history"""
    return _processor.execution_history
