# agent_squad_jump_integration.py
from crewai import Agent, Task, Crew
from jump_codes import JumpCodeRegistry, JumpCode
from typing import Dict, Any, List, Optional
import json
import logging
from datetime import datetime

logger = logging.getLogger(__name__)

class EnhancedAgentSquad:
    """Enhanced Agent Squad with Jump Code support"""
    
    def __init__(self):
        self.jump_registry = JumpCodeRegistry()
        self.agents: Dict[str, Agent] = {}
        self.tasks: List[Task] = []
        self.crews: Dict[str, Crew] = {}
        self.current_context = {
            'session_id': datetime.now().strftime('%Y%m%d_%H%M%S'),
            'agents': {},
            'tasks': [],
            'results': []
        }
        self._register_squad_jump_codes()
    
    def _register_squad_jump_codes(self):
        """Register agent-squad specific jump codes"""
        
        # Agent creation jump code
        self.jump_registry.register(JumpCode(
            code="create_agent",
            description="Quickly create a new agent with predefined template",
            handler=self._create_agent_handler,
            parameters={"role": "", "goal": "", "backstory": "", "tools": []},
            aliases=["ca", "new_agent"]
        ))
        
        # Task assignment jump code
        self.jump_registry.register(JumpCode(
            code="assign_task",
            description="Assign task to specific agent",
            handler=self._assign_task_handler,
            parameters={"agent": "", "task": "", "priority": "normal"},
            aliases=["at", "task"]
        ))
        
        # Workflow execution jump code
        self.jump_registry.register(JumpCode(
            code="run_workflow",
            description="Execute predefined workflow",
            handler=self._run_workflow_handler,
            parameters={"workflow": "", "async": False},
            aliases=["rw", "exec"]
        ))
        
        # Context switching jump code
        self.jump_registry.register(JumpCode(
            code="switch_context",
            description="Switch to different project context",
            handler=self._switch_context_handler,
            parameters={"context": "", "preserve_state": True},
            aliases=["sc", "ctx"]
        ))
        
        # List agents jump code
        self.jump_registry.register(JumpCode(
            code="list_agents",
            description="List all available agents",
            handler=self._list_agents_handler,
            parameters={},
            aliases=["la", "agents"]
        ))
        
        # Save state jump code
        self.jump_registry.register(JumpCode(
            code="save_state",
            description="Save current state to checkpoint",
            handler=self._save_state_handler,
            parameters={"name": "", "include": ["agents", "tasks", "results"]},
            aliases=["save", "checkpoint"]
        ))
        
        # Restore state jump code
        self.jump_registry.register(JumpCode(
            code="restore_state",
            description="Restore from saved checkpoint",
            handler=self._restore_state_handler,
            parameters={"name": "", "partial": False},
            aliases=["restore", "load"]
        ))
        
        # Chain tasks jump code
        self.jump_registry.register(JumpCode(
            code="chain",
            description="Chain multiple tasks together",
            handler=self._chain_tasks_handler,
            parameters={"tasks": []},
            aliases=["ch", "sequence"]
        ))
        
        # Debug jump code
        self.jump_registry.register(JumpCode(
            code="debug",
            description="Enable debug mode for agents",
            handler=self._debug_handler,
            parameters={"agent": "all", "verbose": True, "save_logs": False},
            aliases=["dbg", "d"]
        ))
        
        # Template jump code
        self.jump_registry.register(JumpCode(
            code="template",
            description="Apply workflow template",
            handler=self._template_handler,
            parameters={"name": "", "agents": []},
            aliases=["tpl", "t"]
        ))
        
        # Parallel execution jump code
        self.jump_registry.register(JumpCode(
            code="parallel",
            description="Execute tasks in parallel",
            handler=self._parallel_handler,
            parameters={"tasks": "", "timeout": 300, "fail_fast": False},
            aliases=["par", "concurrent"]
        ))
    
    def process_jump_code(self, code_string: str) -> Dict[str, Any]:
        """Process jump code from user input"""
        try:
            result = self.jump_registry.execute(
                code_string, 
                context=self.current_context
            )
            logger.info(f"Jump code executed successfully: {code_string}")
            return result
        except Exception as e:
            logger.error(f"Jump code error: {str(e)}")
            return {
                'error': True,
                'message': f"Jump code error: {str(e)}",
                'code': code_string
            }
    
    def process_input_with_jump_codes(self, user_input: str) -> Optional[Dict[str, Any]]:
        """Process user input and extract/execute jump codes"""
        # Check for direct jump code
        if user_input.startswith('@'):
            return self.process_jump_code(user_input)
        
        # Check for inline jump codes
        import re
        inline_pattern = r'\{@([^}]+)\}'
        matches = re.findall(inline_pattern, user_input)
        
        if matches:
            results = []
            for match in matches:
                result = self.process_jump_code(f"@{match}")
                results.append(result)
            return {
                'type': 'inline_codes',
                'results': results,
                'original_input': user_input
            }
        
        return None
    
    # Jump code handlers
    def _create_agent_handler(self, context: Dict[str, Any], 
                            role: str, goal: str, backstory: str, 
                            tools: List[str] = None, **kwargs) -> Dict[str, Any]:
        """Create a new agent"""
        try:
            # Validate inputs
            if not role:
                raise ValueError("Agent role is required")
            if not goal:
                raise ValueError("Agent goal is required")
            
            # Create agent
            agent = Agent(
                role=role,
                goal=goal,
                backstory=backstory or f"Expert {role} with extensive experience",
                tools=tools or [],
                verbose=True,
                allow_delegation=False
            )
            
            # Store agent
            agent_id = f"agent_{len(self.agents) + 1}"
            self.agents[agent_id] = agent
            
            # Update context
            context['agents'][agent_id] = {
                'role': role,
                'goal': goal,
                'created_at': datetime.now().isoformat()
            }
            
            return {
                'type': 'agent_created',
                'agent_id': agent_id,
                'role': role,
                'goal': goal,
                'message': f"Agent '{role}' created successfully"
            }
            
        except Exception as e:
            return {
                'error': True,
                'message': f"Failed to create agent: {str(e)}"
            }
    
    def _assign_task_handler(self, context: Dict[str, Any], 
                           agent: str, task: str, priority: str = "normal", 
                           **kwargs) -> Dict[str, Any]:
        """Assign a task to an agent"""
        try:
            # Find agent
            if agent not in self.agents:
                available = list(self.agents.keys())
                return {
                    'error': True,
                    'message': f"Agent '{agent}' not found. Available: {available}"
                }
            
            # Create task
            task_obj = Task(
                description=task,
                agent=self.agents[agent],
                expected_output="Detailed results of the task execution"
            )
            
            # Store task
            self.tasks.append(task_obj)
            
            # Update context
            context['tasks'].append({
                'agent': agent,
                'description': task,
                'priority': priority,
                'assigned_at': datetime.now().isoformat()
            })
            
            return {
                'type': 'task_assigned',
                'agent': agent,
                'task': task,
                'priority': priority,
                'message': f"Task assigned to agent '{agent}'"
            }
            
        except Exception as e:
            return {
                'error': True,
                'message': f"Failed to assign task: {str(e)}"
            }
    
    def _run_workflow_handler(self, context: Dict[str, Any], 
                            workflow: str, async_mode: bool = False, 
                            **kwargs) -> Dict[str, Any]:
        """Execute a workflow"""
        try:
            if not self.agents:
                return {
                    'error': True,
                    'message': "No agents available to run workflow"
                }
            
            if not self.tasks:
                return {
                    'error': True,
                    'message': "No tasks available to run"
                }
            
            # Create crew
            crew = Crew(
                agents=list(self.agents.values()),
                tasks=self.tasks,
                verbose=True,
                process="sequential"  # or "hierarchical"
            )
            
            # Store crew
            crew_id = f"crew_{workflow}_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
            self.crews[crew_id] = crew
            
            # Execute
            if async_mode:
                # Would implement async execution here
                return {
                    'type': 'workflow_started',
                    'crew_id': crew_id,
                    'workflow': workflow,
                    'async': True,
                    'message': f"Workflow '{workflow}' started in async mode"
                }
            else:
                result = crew.kickoff()
                
                # Update context with results
                context['results'].append({
                    'workflow': workflow,
                    'crew_id': crew_id,
                    'result': str(result),
                    'completed_at': datetime.now().isoformat()
                })
                
                return {
                    'type': 'workflow_completed',
                    'crew_id': crew_id,
                    'workflow': workflow,
                    'result': str(result),
                    'message': f"Workflow '{workflow}' completed successfully"
                }
            
        except Exception as e:
            return {
                'error': True,
                'message': f"Failed to run workflow: {str(e)}"
            }
    
    def _switch_context_handler(self, context: Dict[str, Any], 
                              context_name: str, preserve_state: bool = True, 
                              **kwargs) -> Dict[str, Any]:
        """Switch to a different context"""
        try:
            if preserve_state:
                # Save current state
                self._save_context_state(context['session_id'])
            
            # Create new context
            self.current_context = {
                'session_id': f"{context_name}_{datetime.now().strftime('%Y%m%d_%H%M%S')}",
                'agents': {},
                'tasks': [],
                'results': [],
                'previous_context': context['session_id'] if preserve_state else None
            }
            
            return {
                'type': 'context_switched',
                'new_context': context_name,
                'session_id': self.current_context['session_id'],
                'preserved': preserve_state,
                'message': f"Switched to context '{context_name}'"
            }
            
        except Exception as e:
            return {
                'error': True,
                'message': f"Failed to switch context: {str(e)}"
            }
    
    def _list_agents_handler(self, context: Dict[str, Any], **kwargs) -> Dict[str, Any]:
        """List all available agents"""
        agents_info = []
        
        for agent_id, agent in self.agents.items():
            agents_info.append({
                'id': agent_id,
                'role': agent.role,
                'goal': agent.goal,
                'tools': [tool.__class__.__name__ if hasattr(tool, '__class__') else str(tool) 
                         for tool in agent.tools] if agent.tools else []
            })
        
        return {
            'type': 'agents_list',
            'agents': agents_info,
            'total': len(agents_info)
        }
    
    def _save_state_handler(self, context: Dict[str, Any], 
                          name: str, include: List[str] = None, 
                          **kwargs) -> Dict[str, Any]:
        """Save current state"""
        try:
            if not name:
                name = f"checkpoint_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
            
            include = include or ["agents", "tasks", "results"]
            
            state = {
                'name': name,
                'timestamp': datetime.now().isoformat(),
                'session_id': context['session_id']
            }
            
            if "agents" in include:
                state['agents'] = context.get('agents', {})
            if "tasks" in include:
                state['tasks'] = context.get('tasks', [])
            if "results" in include:
                state['results'] = context.get('results', [])
            
            # Save to file
            filename = f"state_{name}.json"
            with open(filename, 'w') as f:
                json.dump(state, f, indent=2)
            
            return {
                'type': 'state_saved',
                'name': name,
                'filename': filename,
                'included': include,
                'message': f"State saved as '{name}'"
            }
            
        except Exception as e:
            return {
                'error': True,
                'message': f"Failed to save state: {str(e)}"
            }
    
    def _restore_state_handler(self, context: Dict[str, Any], 
                             name: str, partial: bool = False, 
                             **kwargs) -> Dict[str, Any]:
        """Restore from saved state"""
        try:
            filename = f"state_{name}.json"
            
            with open(filename, 'r') as f:
                state = json.load(f)
            
            if not partial:
                # Full restore
                self.current_context.update(state)
            else:
                # Partial restore - merge with current
                if 'agents' in state:
                    context['agents'].update(state['agents'])
                if 'tasks' in state:
                    context['tasks'].extend(state['tasks'])
                if 'results' in state:
                    context['results'].extend(state['results'])
            
            return {
                'type': 'state_restored',
                'name': name,
                'partial': partial,
                'message': f"State restored from '{name}'"
            }
            
        except Exception as e:
            return {
                'error': True,
                'message': f"Failed to restore state: {str(e)}"
            }
    
    def _chain_tasks_handler(self, context: Dict[str, Any], 
                           tasks: List[str], **kwargs) -> Dict[str, Any]:
        """Chain multiple tasks together"""
        try:
            chained_results = []
            
            for task_desc in tasks:
                # Parse task format: "agent:task_description"
                if ':' in task_desc:
                    agent_id, task_content = task_desc.split(':', 1)
                    result = self._assign_task_handler(
                        context, 
                        agent=agent_id.strip(), 
                        task=task_content.strip()
                    )
                    chained_results.append(result)
                else:
                    return {
                        'error': True,
                        'message': f"Invalid task format: {task_desc}. Use 'agent:task'"
                    }
            
            return {
                'type': 'tasks_chained',
                'tasks': tasks,
                'results': chained_results,
                'message': f"Chained {len(tasks)} tasks successfully"
            }
            
        except Exception as e:
            return {
                'error': True,
                'message': f"Failed to chain tasks: {str(e)}"
            }
    
    def _debug_handler(self, context: Dict[str, Any], 
                     agent: str = "all", verbose: bool = True, 
                     save_logs: bool = False, **kwargs) -> Dict[str, Any]:
        """Enable debug mode"""
        try:
            if agent == "all":
                for agent_obj in self.agents.values():
                    agent_obj.verbose = verbose
                message = f"Debug mode {'enabled' if verbose else 'disabled'} for all agents"
            else:
                if agent in self.agents:
                    self.agents[agent].verbose = verbose
                    message = f"Debug mode {'enabled' if verbose else 'disabled'} for agent '{agent}'"
                else:
                    return {
                        'error': True,
                        'message': f"Agent '{agent}' not found"
                    }
            
            if save_logs:
                # Configure logging to file
                log_filename = f"debug_logs_{datetime.now().strftime('%Y%m%d_%H%M%S')}.log"
                file_handler = logging.FileHandler(log_filename)
                file_handler.setLevel(logging.DEBUG)
                formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
                file_handler.setFormatter(formatter)
                logger.addHandler(file_handler)
                message += f" - Logs saved to {log_filename}"
            
            return {
                'type': 'debug_configured',
                'agent': agent,
                'verbose': verbose,
                'save_logs': save_logs,
                'message': message
            }
            
        except Exception as e:
            return {
                'error': True,
                'message': f"Failed to configure debug: {str(e)}"
            }
    
    def _template_handler(self, context: Dict[str, Any], 
                        name: str, agents: List[str] = None, 
                        **kwargs) -> Dict[str, Any]:
        """Apply a workflow template"""
        templates = {
            'full_code_review': {
                'agents': [
                    {'role': 'code_reviewer', 'goal': 'Ensure code quality and standards'},
                    {'role': 'security_auditor', 'goal': 'Identify security vulnerabilities'},
                    {'role': 'performance_analyst', 'goal': 'Optimize code performance'},
                    {'role': 'documenter', 'goal': 'Create comprehensive documentation'}
                ],
                'tasks': [
                    'code_reviewer:Review code structure and patterns',
                    'security_auditor:Scan for security issues',
                    'performance_analyst:Analyze performance bottlenecks',
                    'documenter:Generate documentation'
                ]
            },
            'data_pipeline': {
                'agents': [
                    {'role': 'data_extractor', 'goal': 'Extract data from sources'},
                    {'role': 'data_transformer', 'goal': 'Transform and clean data'},
                    {'role': 'data_loader', 'goal': 'Load data to destination'}
                ],
                'tasks': [
                    'data_extractor:Extract data from configured sources',
                    'data_transformer:Apply transformations and cleaning',
                    'data_loader:Load processed data to target'
                ]
            }
        }
        
        try:
            if name not in templates:
                return {
                    'error': True,
                    'message': f"Template '{name}' not found. Available: {list(templates.keys())}"
                }
            
            template = templates[name]
            results = []
            
            # Create agents from template
            for agent_spec in template['agents']:
                if not agents or agent_spec['role'] in agents:
                    result = self._create_agent_handler(
                        context,
                        role=agent_spec['role'],
                        goal=agent_spec['goal'],
                        backstory=agent_spec.get('backstory', '')
                    )
                    results.append(result)
            
            # Create tasks from template
            for task in template['tasks']:
                result = self.process_jump_code(f"@chain:tasks={task}")
                results.append(result)
            
            return {
                'type': 'template_applied',
                'template': name,
                'results': results,
                'message': f"Template '{name}' applied successfully"
            }
            
        except Exception as e:
            return {
                'error': True,
                'message': f"Failed to apply template: {str(e)}"
            }
    
    def _parallel_handler(self, context: Dict[str, Any], 
                         tasks: str, timeout: int = 300, 
                         fail_fast: bool = False, **kwargs) -> Dict[str, Any]:
        """Execute tasks in parallel"""
        try:
            # Parse tasks string (format: "task1;task2;task3")
            task_list = [t.strip() for t in tasks.split(';') if t.strip()]
            
            if not task_list:
                return {
                    'error': True,
                    'message': "No tasks provided for parallel execution"
                }
            
            # Import threading for parallel execution
            import concurrent.futures
            import time
            
            results = {}
            failed = False
            
            def execute_task(task_str):
                """Execute a single task"""
                # Parse task format: "agent:task_description" or just "task_description"
                if ':' in task_str:
                    agent_id, task_desc = task_str.split(':', 1)
                else:
                    # Use first available agent
                    if self.agents:
                        agent_id = list(self.agents.keys())[0]
                        task_desc = task_str
                    else:
                        return {'error': 'No agents available'}
                
                # Execute task assignment
                return self._assign_task_handler(
                    context,
                    agent=agent_id.strip(),
                    task=task_desc.strip()
                )
            
            # Execute tasks in parallel
            with concurrent.futures.ThreadPoolExecutor(max_workers=len(task_list)) as executor:
                # Submit all tasks
                future_to_task = {
                    executor.submit(execute_task, task): task 
                    for task in task_list
                }
                
                # Collect results
                for future in concurrent.futures.as_completed(future_to_task, timeout=timeout):
                    task = future_to_task[future]
                    try:
                        result = future.result()
                        results[task] = result
                        
                        if fail_fast and result.get('error'):
                            failed = True
                            executor.shutdown(wait=False)
                            break
                    except Exception as e:
                        results[task] = {'error': True, 'message': str(e)}
                        if fail_fast:
                            failed = True
                            executor.shutdown(wait=False)
                            break
            
            return {
                'type': 'parallel_execution',
                'tasks': task_list,
                'results': results,
                'completed': len(results),
                'total': len(task_list),
                'failed': failed,
                'message': f"Executed {len(results)}/{len(task_list)} tasks in parallel"
            }
            
        except concurrent.futures.TimeoutError:
            return {
                'error': True,
                'message': f"Parallel execution timed out after {timeout} seconds"
            }
        except Exception as e:
            return {
                'error': True,
                'message': f"Failed to execute tasks in parallel: {str(e)}"
            }
    
    def _save_context_state(self, session_id: str):
        """Helper to save context state"""
        state_file = f"context_{session_id}.json"
        with open(state_file, 'w') as f:
            json.dump(self.current_context, f, indent=2)
