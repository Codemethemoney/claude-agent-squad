# advanced_jump_codes.py
from typing import List, Dict, Any, Optional
from datetime import datetime
from jump_codes import JumpCodeRegistry
import re
import json
import logging

logger = logging.getLogger(__name__)

class SequentialJumpCodes:
    """Handle sequential execution of jump codes with shared context"""
    
    def __init__(self, registry: JumpCodeRegistry):
        self.registry = registry
        self.sequence_memory: List[Dict[str, Any]] = []
        self.max_memory_size = 100  # Keep last 100 sequences
    
    def execute_sequence(self, sequence: List[str]) -> List[Dict[str, Any]]:
        """Execute a sequence of jump codes with shared context"""
        shared_context = {
            'sequence_id': datetime.now().strftime('%Y%m%d_%H%M%S_%f'),
            'sequence_start': datetime.now()
        }
        results = []
        
        logger.info(f"Starting sequence execution with {len(sequence)} codes")
        
        for i, code in enumerate(sequence):
            # Add sequence position to context
            shared_context['sequence_position'] = i
            shared_context['previous_results'] = results.copy()
            
            try:
                logger.debug(f"Executing code {i+1}/{len(sequence)}: {code}")
                result = self.registry.execute(code, shared_context)
                
                results.append({
                    'code': code,
                    'success': True,
                    'result': result,
                    'position': i,
                    'timestamp': datetime.now().isoformat()
                })
                
                # Update shared context with result if it's a dict
                if isinstance(result, dict):
                    # Avoid overwriting critical keys
                    protected_keys = {'sequence_id', 'sequence_position', 'previous_results'}
                    for key, value in result.items():
                        if key not in protected_keys:
                            shared_context[key] = value
                
            except Exception as e:
                logger.error(f"Error executing code at position {i}: {e}")
                results.append({
                    'code': code,
                    'success': False,
                    'error': str(e),
                    'position': i,
                    'timestamp': datetime.now().isoformat()
                })
                
                # Decide whether to continue or abort
                if self._should_abort_sequence(e, i, len(sequence)):
                    logger.warning("Aborting sequence due to critical error")
                    break
        
        # Record sequence in memory
        sequence_record = {
            'sequence': sequence,
            'results': results,
            'timestamp': datetime.now(),
            'duration': (datetime.now() - shared_context['sequence_start']).total_seconds(),
            'completed': len(results) == len(sequence),
            'success_rate': sum(1 for r in results if r['success']) / len(results) if results else 0
        }
        
        self._add_to_memory(sequence_record)
        logger.info(f"Sequence completed. Success rate: {sequence_record['success_rate']*100:.1f}%")
        
        return results
    
    def _should_abort_sequence(self, error: Exception, position: int, total: int) -> bool:
        """Determine if sequence should be aborted based on error"""
        # Critical errors that should stop execution
        critical_errors = [
            "Missing required context",
            "Unknown jump code",
            "Invalid jump code format"
        ]
        
        error_msg = str(error)
        for critical in critical_errors:
            if critical in error_msg:
                return True
        
        # Don't abort on last item
        if position == total - 1:
            return False
        
        # Continue by default
        return False
    
    def _add_to_memory(self, record: Dict[str, Any]):
        """Add sequence record to memory with size limit"""
        self.sequence_memory.append(record)
        
        # Maintain memory size limit
        if len(self.sequence_memory) > self.max_memory_size:
            self.sequence_memory = self.sequence_memory[-self.max_memory_size:]
    
    def get_history(self, limit: int = 10) -> List[Dict[str, Any]]:
        """Get recent sequence execution history"""
        return self.sequence_memory[-limit:]
    
    def find_successful_sequences(self) -> List[Dict[str, Any]]:
        """Find all completely successful sequences"""
        return [seq for seq in self.sequence_memory 
                if seq['completed'] and seq['success_rate'] == 1.0]
    
    def replay_sequence(self, sequence_index: int) -> List[Dict[str, Any]]:
        """Replay a sequence from history"""
        if 0 <= sequence_index < len(self.sequence_memory):
            sequence = self.sequence_memory[sequence_index]['sequence']
            logger.info(f"Replaying sequence from history: {sequence_index}")
            return self.execute_sequence(sequence)
        else:
            raise ValueError(f"Invalid sequence index: {sequence_index}")


class JumpCodeMacros:
    """Define and manage reusable jump code sequences"""
    
    def __init__(self):
        self.macros: Dict[str, Dict[str, Any]] = {}
        self._load_default_macros()
    
    def _load_default_macros(self):
        """Load default macro definitions"""
        defaults = {
            'init_project': {
                'sequence': [
                    '@create_agent:role=project_manager,goal=coordinate project tasks',
                    '@create_agent:role=developer,goal=implement features',
                    '@create_agent:role=tester,goal=ensure quality',
                    '@template:name=full_code_review'
                ],
                'description': 'Initialize a new project with standard agents',
                'parameters': []
            },
            'quick_review': {
                'sequence': [
                    '@create_agent:role=reviewer,goal=review code',
                    '@assign_task:agent=reviewer,task=${task_description}',
                    '@run_workflow:workflow=review'
                ],
                'description': 'Quick code review workflow',
                'parameters': ['task_description']
            },
            'debug_all': {
                'sequence': [
                    '@debug:agent=all,verbose=true,save_logs=true',
                    '@status',
                    '@list_agents'
                ],
                'description': 'Enable full debugging and show status',
                'parameters': []
            },
            'save_and_switch': {
                'sequence': [
                    '@save_state:name=${checkpoint_name}',
                    '@switch_context:context=${new_context},preserve_state=true'
                ],
                'description': 'Save current state and switch context',
                'parameters': ['checkpoint_name', 'new_context']
            },
            'parallel_analysis': {
                'sequence': [
                    '@create_agent:role=code_analyst,goal=analyze code structure',
                    '@create_agent:role=security_scanner,goal=find vulnerabilities',
                    '@create_agent:role=performance_profiler,goal=identify bottlenecks',
                    '@parallel:tasks=analyze_structure;scan_security;profile_performance'
                ],
                'description': 'Parallel code analysis workflow',
                'parameters': []
            }
        }
        
        for name, config in defaults.items():
            self.define_macro(
                name=name,
                sequence=config['sequence'],
                description=config['description'],
                parameters=config.get('parameters', [])
            )
    
    def define_macro(self, name: str, sequence: List[str], 
                    description: str = "", parameters: List[str] = None):
        """Define a new macro"""
        if not re.match(r'^[a-zA-Z_]\w*$', name):
            raise ValueError(f"Invalid macro name format: {name}")
        
        self.macros[name] = {
            'sequence': sequence,
            'description': description,
            'parameters': parameters or [],
            'created': datetime.now(),
            'usage_count': 0
        }
        
        logger.info(f"Macro '{name}' defined with {len(sequence)} steps")
    
    def undefine_macro(self, name: str) -> bool:
        """Remove a macro definition"""
        if name in self.macros:
            del self.macros[name]
            logger.info(f"Macro '{name}' removed")
            return True
        return False
    
    def expand_macro(self, name: str, params: Dict[str, str] = None) -> List[str]:
        """Expand macro with parameter substitution"""
        if name not in self.macros:
            raise ValueError(f"Unknown macro: {name}")
        
        macro = self.macros[name]
        params = params or {}
        
        # Check required parameters
        missing_params = [p for p in macro['parameters'] if p not in params]
        if missing_params:
            raise ValueError(f"Missing required parameters for macro '{name}': {missing_params}")
        
        # Expand sequence with parameter substitution
        expanded_sequence = []
        for code in macro['sequence']:
            expanded_code = self._substitute_params(code, params)
            expanded_sequence.append(expanded_code)
        
        # Update usage count
        macro['usage_count'] += 1
        
        logger.info(f"Macro '{name}' expanded with {len(params)} parameters")
        return expanded_sequence
    
    def _substitute_params(self, code: str, params: Dict[str, str]) -> str:
        """Substitute parameters in a jump code string"""
        # Pattern to match ${param_name}
        pattern = r'\$\{(\w+)\}'
        
        def replacer(match):
            param_name = match.group(1)
            if param_name in params:
                return params[param_name]
            else:
                # Keep original if parameter not provided
                return match.group(0)
        
        return re.sub(pattern, replacer, code)
    
    def list_macros(self) -> Dict[str, Dict[str, Any]]:
        """List all available macros"""
        return {
            name: {
                'description': macro['description'],
                'parameters': macro['parameters'],
                'steps': len(macro['sequence']),
                'usage_count': macro['usage_count']
            }
            for name, macro in self.macros.items()
        }
    
    def get_macro_details(self, name: str) -> Optional[Dict[str, Any]]:
        """Get detailed information about a macro"""
        if name in self.macros:
            macro = self.macros[name].copy()
            # Don't expose internal fields
            macro.pop('created', None)
            return macro
        return None
    
    def save_macros(self, filename: str):
        """Save macros to file"""
        data = {
            name: {
                'sequence': macro['sequence'],
                'description': macro['description'],
                'parameters': macro['parameters']
            }
            for name, macro in self.macros.items()
        }
        
        with open(filename, 'w') as f:
            json.dump(data, f, indent=2)
        
        logger.info(f"Saved {len(data)} macros to {filename}")
    
    def load_macros(self, filename: str):
        """Load macros from file"""
        try:
            with open(filename, 'r') as f:
                data = json.load(f)
            
            for name, config in data.items():
                self.define_macro(
                    name=name,
                    sequence=config['sequence'],
                    description=config.get('description', ''),
                    parameters=config.get('parameters', [])
                )
            
            logger.info(f"Loaded {len(data)} macros from {filename}")
        except Exception as e:
            logger.error(f"Failed to load macros from {filename}: {e}")
            raise


class JumpCodeMiddleware:
    """Middleware for processing jump codes in user input"""
    
    def __init__(self, agent_squad):
        self.agent_squad = agent_squad
        self.jump_registry = agent_squad.jump_registry
        self.sequential = SequentialJumpCodes(self.jump_registry)
        self.macros = JumpCodeMacros()
        self._register_macro_codes()
    
    def _register_macro_codes(self):
        """Register jump codes for macro operations"""
        from jump_codes import JumpCode
        
        # Define macro jump code
        self.jump_registry.register(JumpCode(
            code="define_macro",
            description="Define a new macro",
            handler=self._define_macro_handler,
            parameters={"name": "", "sequence": [], "description": ""},
            aliases=["macro", "m"]
        ))
        
        # Execute macro jump code
        self.jump_registry.register(JumpCode(
            code="exec_macro",
            description="Execute a macro",
            handler=self._exec_macro_handler,
            parameters={"name": "", "params": {}},
            aliases=["em", "run_macro"]
        ))
        
        # List macros jump code
        self.jump_registry.register(JumpCode(
            code="list_macros",
            description="List all available macros",
            handler=self._list_macros_handler,
            parameters={},
            aliases=["lm", "macros"]
        ))
    
    def process_input(self, user_input: str) -> Optional[Dict[str, Any]]:
        """Process user input for jump codes and macros"""
        # Direct jump code
        if user_input.startswith('@'):
            return self._process_single_code(user_input)
        
        # Macro execution shorthand: !macro_name(param1=value1, param2=value2)
        macro_pattern = r'^!(\w+)\(([^)]*)\)$'
        macro_match = re.match(macro_pattern, user_input)
        if macro_match:
            macro_name = macro_match.group(1)
            params_str = macro_match.group(2)
            params = self._parse_macro_params(params_str)
            return self._exec_macro_handler({}, name=macro_name, params=params)
        
        # Sequence execution: @@code1 @@code2 @@code3
        if '@@' in user_input:
            codes = re.findall(r'@@(\S+)', user_input)
            if codes:
                return self._process_sequence(codes)
        
        # Inline jump codes: {some text {@code} more text}
        inline_pattern = r'\{@([^}]+)\}'
        if re.search(inline_pattern, user_input):
            return self._process_inline_codes(user_input)
        
        return None
    
    def _process_single_code(self, code: str) -> Dict[str, Any]:
        """Process a single jump code"""
        try:
            return self.agent_squad.process_jump_code(code)
        except Exception as e:
            return {
                'error': True,
                'message': str(e),
                'code': code
            }
    
    def _process_sequence(self, codes: List[str]) -> Dict[str, Any]:
        """Process a sequence of jump codes"""
        # Add @ prefix if not present
        codes = [f"@{code}" if not code.startswith('@') else code for code in codes]
        
        results = self.sequential.execute_sequence(codes)
        
        return {
            'type': 'sequence_execution',
            'codes': codes,
            'results': results,
            'success_count': sum(1 for r in results if r['success']),
            'total_count': len(results)
        }
    
    def _process_inline_codes(self, text: str) -> Dict[str, Any]:
        """Process inline jump codes within text"""
        inline_pattern = r'\{@([^}]+)\}'
        results = []
        processed_text = text
        
        for match in re.finditer(inline_pattern, text):
            code = f"@{match.group(1)}"
            result = self._process_single_code(code)
            results.append(result)
            
            # Replace inline code with result summary if successful
            if not result.get('error'):
                summary = result.get('message', 'Executed')
                processed_text = processed_text.replace(match.group(0), f"[{summary}]")
        
        return {
            'type': 'inline_execution',
            'original_text': text,
            'processed_text': processed_text,
            'results': results
        }
    
    def _parse_macro_params(self, params_str: str) -> Dict[str, str]:
        """Parse macro parameters from string"""
        params = {}
        if params_str:
            for param in params_str.split(','):
                param = param.strip()
                if '=' in param:
                    key, value = param.split('=', 1)
                    params[key.strip()] = value.strip()
        return params
    
    # Macro handlers
    def _define_macro_handler(self, context: Dict[str, Any], 
                            name: str, sequence: List[str], 
                            description: str = "", **kwargs) -> Dict[str, Any]:
        """Handler for defining macros"""
        try:
            # Extract parameters from sequence
            params = set()
            pattern = r'\$\{(\w+)\}'
            for code in sequence:
                params.update(re.findall(pattern, code))
            
            self.macros.define_macro(
                name=name,
                sequence=sequence,
                description=description,
                parameters=list(params)
            )
            
            return {
                'type': 'macro_defined',
                'name': name,
                'steps': len(sequence),
                'parameters': list(params),
                'message': f"Macro '{name}' defined successfully"
            }
        except Exception as e:
            return {
                'error': True,
                'message': f"Failed to define macro: {str(e)}"
            }
    
    def _exec_macro_handler(self, context: Dict[str, Any], 
                          name: str, params: Dict[str, str] = None, 
                          **kwargs) -> Dict[str, Any]:
        """Handler for executing macros"""
        try:
            # Expand macro
            sequence = self.macros.expand_macro(name, params or {})
            
            # Execute sequence
            results = self.sequential.execute_sequence(sequence)
            
            return {
                'type': 'macro_executed',
                'name': name,
                'parameters': params or {},
                'sequence_length': len(sequence),
                'results': results,
                'success_rate': sum(1 for r in results if r['success']) / len(results) if results else 0,
                'message': f"Macro '{name}' executed with {len(sequence)} steps"
            }
        except Exception as e:
            return {
                'error': True,
                'message': f"Failed to execute macro: {str(e)}"
            }
    
    def _list_macros_handler(self, context: Dict[str, Any], **kwargs) -> Dict[str, Any]:
        """Handler for listing macros"""
        macros = self.macros.list_macros()
        
        macro_list = []
        for name, info in macros.items():
            macro_str = f"!{name}"
            if info['parameters']:
                macro_str += f"({', '.join(info['parameters'])})"
            macro_str += f" - {info['description']} ({info['steps']} steps)"
            macro_list.append(macro_str)
        
        return {
            'type': 'macros_list',
            'macros': macro_list,
            'total': len(macros)
        }
