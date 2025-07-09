# jump_codes.py
from typing import Dict, Callable, Any, Optional, List
from dataclasses import dataclass
import re
from datetime import datetime
import logging

logger = logging.getLogger(__name__)

@dataclass
class JumpCode:
    """Represents a single jump code command"""
    code: str
    description: str
    handler: Callable
    parameters: Dict[str, Any]
    aliases: List[str] = None
    context_required: List[str] = None

    def __post_init__(self):
        if self.aliases is None:
            self.aliases = []
        if self.context_required is None:
            self.context_required = []

class JumpCodeRegistry:
    """Registry for managing jump codes"""
    
    def __init__(self):
        self.codes: Dict[str, JumpCode] = {}
        self.aliases: Dict[str, str] = {}
        self._initialize_core_codes()
    
    def _initialize_core_codes(self):
        """Initialize built-in jump codes"""
        # Status jump code
        self.register(JumpCode(
            code="status",
            description="Show current system status",
            handler=self._status_handler,
            parameters={},
            aliases=["s", "stat"]
        ))
        
        # Help jump code
        self.register(JumpCode(
            code="help",
            description="Show available jump codes",
            handler=self._help_handler,
            parameters={"filter": ""},
            aliases=["h", "?"]
        ))
        
        # List jump code
        self.register(JumpCode(
            code="list",
            description="List all registered jump codes",
            handler=self._list_handler,
            parameters={},
            aliases=["ls", "l"]
        ))
    
    def register(self, jump_code: JumpCode):
        """Register a new jump code"""
        # Validate code format
        if not re.match(r'^[a-zA-Z_]\w*$', jump_code.code):
            raise ValueError(f"Invalid jump code format: {jump_code.code}")
        
        # Check for duplicates
        if jump_code.code in self.codes:
            logger.warning(f"Overriding existing jump code: {jump_code.code}")
        
        self.codes[jump_code.code] = jump_code
        
        # Register aliases
        if jump_code.aliases:
            for alias in jump_code.aliases:
                if alias in self.aliases:
                    logger.warning(f"Overriding existing alias: {alias}")
                self.aliases[alias] = jump_code.code
    
    def unregister(self, code: str):
        """Unregister a jump code"""
        if code in self.codes:
            jump_code = self.codes[code]
            # Remove aliases
            if jump_code.aliases:
                for alias in jump_code.aliases:
                    if alias in self.aliases:
                        del self.aliases[alias]
            # Remove code
            del self.codes[code]
            return True
        return False
    
    def execute(self, code_string: str, context: Dict[str, Any] = None):
        """Execute a jump code with optional context"""
        if context is None:
            context = {}
        
        try:
            parsed = self._parse_jump_code(code_string)
            code_name = parsed['code']
            params = parsed['parameters']
            
            # Resolve aliases
            if code_name in self.aliases:
                code_name = self.aliases[code_name]
            
            # Check if code exists
            if code_name not in self.codes:
                raise ValueError(f"Unknown jump code: {code_name}")
            
            jump_code = self.codes[code_name]
            
            # Validate context requirements
            if jump_code.context_required:
                self._validate_context(jump_code.context_required, context)
            
            # Merge parameters with defaults
            final_params = {**jump_code.parameters, **params}
            
            # Execute handler
            logger.info(f"Executing jump code: {code_name} with params: {final_params}")
            return jump_code.handler(context=context, **final_params)
            
        except Exception as e:
            logger.error(f"Error executing jump code '{code_string}': {e}")
            raise
    
    def _parse_jump_code(self, code_string: str) -> Dict[str, Any]:
        """Parse jump code format: @code:param1=value1,param2=value2"""
        # Remove @ prefix if present
        if code_string.startswith('@'):
            code_string = code_string[1:]
        
        # Pattern for parsing jump codes
        pattern = r'^(\w+)(?::(.+))?$'
        match = re.match(pattern, code_string)
        
        if not match:
            raise ValueError(f"Invalid jump code format: {code_string}")
        
        code = match.group(1)
        params_str = match.group(2) or ""
        
        parameters = {}
        if params_str:
            # Parse key=value pairs
            for param in params_str.split(','):
                param = param.strip()
                if '=' in param:
                    key, value = param.split('=', 1)
                    key = key.strip()
                    value = value.strip()
                    
                    # Try to parse value types
                    if value.lower() in ('true', 'false'):
                        parameters[key] = value.lower() == 'true'
                    elif value.isdigit():
                        parameters[key] = int(value)
                    elif value.replace('.', '', 1).isdigit():
                        parameters[key] = float(value)
                    else:
                        parameters[key] = value
                else:
                    # Flag parameter without value
                    parameters[param] = True
        
        return {'code': code, 'parameters': parameters}
    
    def _validate_context(self, required: List[str], context: Dict[str, Any]):
        """Validate that required context keys are present"""
        missing = [key for key in required if key not in context]
        if missing:
            raise ValueError(f"Missing required context: {', '.join(missing)}")
    
    # Built-in handlers
    def _status_handler(self, context: Dict[str, Any], **kwargs):
        """Show current system status"""
        return {
            'type': 'status',
            'total_codes': len(self.codes),
            'total_aliases': len(self.aliases),
            'context_keys': list(context.keys()),
            'timestamp': datetime.now().isoformat()
        }
    
    def _help_handler(self, context: Dict[str, Any], filter: str = "", **kwargs):
        """Show help for jump codes"""
        codes_info = []
        
        for code_name, jump_code in self.codes.items():
            if filter and filter.lower() not in code_name.lower() and filter.lower() not in jump_code.description.lower():
                continue
            
            codes_info.append({
                'code': code_name,
                'description': jump_code.description,
                'aliases': jump_code.aliases,
                'parameters': list(jump_code.parameters.keys()),
                'context_required': jump_code.context_required
            })
        
        return {
            'type': 'help',
            'codes': codes_info,
            'filter': filter
        }
    
    def _list_handler(self, context: Dict[str, Any], **kwargs):
        """List all registered jump codes"""
        codes_list = []
        
        for code_name, jump_code in sorted(self.codes.items()):
            code_info = f"@{code_name}"
            if jump_code.aliases:
                code_info += f" (aliases: {', '.join(jump_code.aliases)})"
            code_info += f" - {jump_code.description}"
            codes_list.append(code_info)
        
        return {
            'type': 'list',
            'codes': codes_list
        }

# Utility functions
def create_jump_code_decorator(registry: JumpCodeRegistry):
    """Create a decorator for easily registering jump codes"""
    def jump_code(code: str, description: str, aliases: List[str] = None, 
                  context_required: List[str] = None, **default_params):
        def decorator(func):
            jump = JumpCode(
                code=code,
                description=description,
                handler=func,
                parameters=default_params,
                aliases=aliases,
                context_required=context_required
            )
            registry.register(jump)
            return func
        return decorator
    return jump_code
