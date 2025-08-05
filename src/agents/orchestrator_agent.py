"""
Orchestrator Agent for coordinating AI agents in the proposal system.

This agent serves as the central coordinator, managing workflows,
delegating tasks to specialized agents, and ensuring proper communication
between different system components.
"""

import asyncio
import logging
import threading
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any, Callable
from dataclasses import dataclass
from enum import Enum

from ..agents.base_agent import BaseAgent
from ..core.communication_manager import CommunicationManager, Message, MessageType, MessagePriority

logger = logging.getLogger(__name__)

class WorkflowStatus(Enum):
    """Status of workflow execution."""
    PENDING = "pending"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"

class TaskPriority(Enum):
    """Task priority levels."""
    LOW = 1
    NORMAL = 2
    HIGH = 3
    CRITICAL = 4

@dataclass
class Task:
    """Individual task within a workflow."""
    id: str
    name: str
    agent_type: str
    input_data: Dict[str, Any]
    output_data: Dict[str, Any] = None
    status: WorkflowStatus = WorkflowStatus.PENDING
    priority: TaskPriority = TaskPriority.NORMAL
    depends_on: List[str] = None  # Task IDs this task depends on
    timeout: int = 300  # Timeout in seconds
    retry_count: int = 0
    max_retries: int = 3
    created_at: datetime = None
    started_at: datetime = None
    completed_at: datetime = None
    error_message: str = None
    
    def __post_init__(self):
        if self.created_at is None:
            self.created_at = datetime.now()
        if self.depends_on is None:
            self.depends_on = []

@dataclass
class Workflow:
    """Workflow definition containing multiple tasks."""
    id: str
    name: str
    description: str
    tasks: List[Task]
    status: WorkflowStatus = WorkflowStatus.PENDING
    created_at: datetime = None
    started_at: datetime = None
    completed_at: datetime = None
    progress: float = 0.0
    metadata: Dict[str, Any] = None
    
    def __post_init__(self):
        if self.created_at is None:
            self.created_at = datetime.now()
        if self.metadata is None:
            self.metadata = {}

class OrchestratorAgent(BaseAgent):
    """
    Orchestrator Agent that coordinates workflows and manages other agents.
    
    Responsibilities:
    - Workflow definition and execution
    - Task scheduling and dependency management
    - Agent coordination and communication
    - Progress tracking and error handling
    - Resource allocation and load balancing
    """
    
    def __init__(self, config: Dict[str, Any] = None):
        super().__init__(config)
        self.agent_type = "orchestrator"
        self.name = "Orchestrator Agent"
        self.description = "Central coordinator for AI agent workflows"
        
        # Core components
        self.communication_manager: Optional[CommunicationManager] = None
        
        # Workflow management
        self.workflows: Dict[str, Workflow] = {}
        self.active_workflows: Dict[str, Workflow] = {}
        self.completed_workflows: Dict[str, Workflow] = {}
        
        # Agent registry
        self.registered_agents: Dict[str, Dict[str, Any]] = {}
        self.agent_capabilities: Dict[str, List[str]] = {}
        self.agent_workload: Dict[str, int] = {}
        
        # Task queue and scheduling
        self.task_queue: List[Task] = []
        self.running_tasks: Dict[str, Task] = {}
        
        # Threading for async operations
        self.executor_thread: Optional[threading.Thread] = None
        self.running = False
        
        # Statistics
        self.stats = {
            'workflows_created': 0,
            'workflows_completed': 0,
            'workflows_failed': 0,
            'tasks_executed': 0,
            'tasks_failed': 0,
            'messages_sent': 0,
            'messages_received': 0
        }
        
        logger.info("Orchestrator Agent initialized")
    
    async def initialize(self) -> bool:
        """Initialize the orchestrator agent."""
        try:
            # Initialize communication manager if not provided
            if not self.communication_manager:
                self.communication_manager = CommunicationManager()
                self.communication_manager.start()
            
            # Register with communication manager
            self.communication_manager.register_agent(
                agent_id="orchestrator",
                name=self.name,
                description=self.description,
                capabilities=["workflow_management", "task_scheduling", "agent_coordination"],
                handler=self._message_handler
            )
            
            # Start background executor
            self.running = True
            self.executor_thread = threading.Thread(target=self._workflow_executor, daemon=True)
            self.executor_thread.start()
            
            logger.info("Orchestrator Agent initialized successfully")
            return True
            
        except Exception as e:
            logger.error(f"Failed to initialize Orchestrator Agent: {e}")
            return False
    
    async def shutdown(self):
        """Shutdown the orchestrator agent."""
        try:
            self.running = False
            
            # Cancel active workflows
            for workflow in self.active_workflows.values():
                workflow.status = WorkflowStatus.CANCELLED
            
            # Stop executor thread
            if self.executor_thread:
                self.executor_thread.join(timeout=10)
            
            # Shutdown communication manager
            if self.communication_manager:
                self.communication_manager.stop()
            
            logger.info("Orchestrator Agent shutdown completed")
            
        except Exception as e:
            logger.error(f"Error during Orchestrator Agent shutdown: {e}")
    
    def register_agent(self, agent_id: str, agent_info: Dict[str, Any]) -> bool:
        """
        Register an agent with the orchestrator.
        
        Args:
            agent_id: Unique identifier for the agent
            agent_info: Agent information including capabilities
            
        Returns:
            True if registered successfully, False otherwise
        """
        try:
            self.registered_agents[agent_id] = agent_info
            self.agent_capabilities[agent_id] = agent_info.get('capabilities', [])
            self.agent_workload[agent_id] = 0
            
            logger.info(f"Agent registered: {agent_id}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to register agent {agent_id}: {e}")
            return False
    
    def create_workflow(self, workflow_definition: Dict[str, Any]) -> Optional[str]:
        """
        Create a new workflow from definition.
        
        Args:
            workflow_definition: Dictionary containing workflow configuration
            
        Returns:
            Workflow ID if created successfully, None otherwise
        """
        try:
            workflow_id = workflow_definition.get('id', f"workflow_{len(self.workflows) + 1}")
            
            # Create tasks from definition
            tasks = []
            for task_def in workflow_definition.get('tasks', []):
                task = Task(
                    id=task_def.get('id', f"task_{len(tasks) + 1}"),
                    name=task_def.get('name', ''),
                    agent_type=task_def.get('agent_type', ''),
                    input_data=task_def.get('input_data', {}),
                    depends_on=task_def.get('depends_on', []),
                    priority=TaskPriority(task_def.get('priority', TaskPriority.NORMAL.value)),
                    timeout=task_def.get('timeout', 300),
                    max_retries=task_def.get('max_retries', 3)
                )
                tasks.append(task)
            
            # Create workflow
            workflow = Workflow(
                id=workflow_id,
                name=workflow_definition.get('name', ''),
                description=workflow_definition.get('description', ''),
                tasks=tasks,
                metadata=workflow_definition.get('metadata', {})
            )
            
            self.workflows[workflow_id] = workflow
            self.stats['workflows_created'] += 1
            
            logger.info(f"Workflow created: {workflow_id} with {len(tasks)} tasks")
            return workflow_id
            
        except Exception as e:
            logger.error(f"Failed to create workflow: {e}")
            return None
    
    def start_workflow(self, workflow_id: str) -> bool:
        """
        Start executing a workflow.
        
        Args:
            workflow_id: ID of the workflow to start
            
        Returns:
            True if started successfully, False otherwise
        """
        try:
            if workflow_id not in self.workflows:
                logger.error(f"Workflow not found: {workflow_id}")
                return False
            
            workflow = self.workflows[workflow_id]
            
            if workflow.status != WorkflowStatus.PENDING:
                logger.error(f"Workflow {workflow_id} is not in pending state")
                return False
            
            # Move to active workflows
            workflow.status = WorkflowStatus.RUNNING
            workflow.started_at = datetime.now()
            self.active_workflows[workflow_id] = workflow
            
            # Queue initial tasks (those with no dependencies)
            for task in workflow.tasks:
                if not task.depends_on:
                    self._queue_task(task)
            
            logger.info(f"Workflow started: {workflow_id}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to start workflow {workflow_id}: {e}")
            return False
    
    def get_workflow_status(self, workflow_id: str) -> Optional[Dict[str, Any]]:
        """
        Get the status of a workflow.
        
        Args:
            workflow_id: ID of the workflow
            
        Returns:
            Workflow status information
        """
        try:
            if workflow_id not in self.workflows:
                return None
            
            workflow = self.workflows[workflow_id]
            
            # Calculate progress
            total_tasks = len(workflow.tasks)
            completed_tasks = sum(1 for task in workflow.tasks if task.status == WorkflowStatus.COMPLETED)
            progress = (completed_tasks / total_tasks) * 100 if total_tasks > 0 else 0
            workflow.progress = progress
            
            return {
                'id': workflow.id,
                'name': workflow.name,
                'status': workflow.status.value,
                'progress': progress,
                'created_at': workflow.created_at.isoformat(),
                'started_at': workflow.started_at.isoformat() if workflow.started_at else None,
                'completed_at': workflow.completed_at.isoformat() if workflow.completed_at else None,
                'total_tasks': total_tasks,
                'completed_tasks': completed_tasks,
                'failed_tasks': sum(1 for task in workflow.tasks if task.status == WorkflowStatus.FAILED),
                'running_tasks': sum(1 for task in workflow.tasks if task.status == WorkflowStatus.RUNNING),
                'tasks': [self._task_to_dict(task) for task in workflow.tasks]
            }
            
        except Exception as e:
            logger.error(f"Failed to get workflow status {workflow_id}: {e}")
            return None
    
    def cancel_workflow(self, workflow_id: str) -> bool:
        """
        Cancel a running workflow.
        
        Args:
            workflow_id: ID of the workflow to cancel
            
        Returns:
            True if cancelled successfully, False otherwise
        """
        try:
            if workflow_id not in self.workflows:
                logger.error(f"Workflow not found: {workflow_id}")
                return False
            
            workflow = self.workflows[workflow_id]
            workflow.status = WorkflowStatus.CANCELLED
            workflow.completed_at = datetime.now()
            
            # Cancel running tasks
            for task in workflow.tasks:
                if task.status == WorkflowStatus.RUNNING:
                    task.status = WorkflowStatus.CANCELLED
            
            # Move to completed workflows
            if workflow_id in self.active_workflows:
                del self.active_workflows[workflow_id]
            self.completed_workflows[workflow_id] = workflow
            
            logger.info(f"Workflow cancelled: {workflow_id}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to cancel workflow {workflow_id}: {e}")
            return False
    
    def get_agent_for_task(self, task: Task) -> Optional[str]:
        """
        Find the best agent to execute a task.
        
        Args:
            task: Task to find an agent for
            
        Returns:
            Agent ID if found, None otherwise
        """
        try:
            # Find agents with required capability
            capable_agents = []
            for agent_id, capabilities in self.agent_capabilities.items():
                if task.agent_type in capabilities or task.agent_type == agent_id:
                    capable_agents.append(agent_id)
            
            if not capable_agents:
                logger.warning(f"No capable agents found for task type: {task.agent_type}")
                return None
            
            # Select agent with lowest workload
            best_agent = min(capable_agents, key=lambda x: self.agent_workload.get(x, 0))
            return best_agent
            
        except Exception as e:
            logger.error(f"Failed to find agent for task {task.id}: {e}")
            return None
    
    def _queue_task(self, task: Task):
        """Queue a task for execution."""
        # Insert based on priority
        inserted = False
        for i, queued_task in enumerate(self.task_queue):
            if task.priority.value > queued_task.priority.value:
                self.task_queue.insert(i, task)
                inserted = True
                break
        
        if not inserted:
            self.task_queue.append(task)
        
        logger.debug(f"Task queued: {task.id}")
    
    def _execute_task(self, task: Task) -> bool:
        """
        Execute a single task.
        
        Args:
            task: Task to execute
            
        Returns:
            True if task completed successfully, False otherwise
        """
        try:
            # Find agent to execute task
            agent_id = self.get_agent_for_task(task)
            if not agent_id:
                task.status = WorkflowStatus.FAILED
                task.error_message = "No capable agent available"
                return False
            
            # Update task status
            task.status = WorkflowStatus.RUNNING
            task.started_at = datetime.now()
            self.running_tasks[task.id] = task
            
            # Increase agent workload
            self.agent_workload[agent_id] = self.agent_workload.get(agent_id, 0) + 1
            
            # Send task message to agent
            message = Message(
                type=MessageType.REQUEST,
                sender="orchestrator",
                recipient=agent_id,
                subject=f"Execute Task: {task.name}",
                payload={
                    'task_id': task.id,
                    'task_name': task.name,
                    'input_data': task.input_data,
                    'timeout': task.timeout
                },
                expires_at=datetime.now() + timedelta(seconds=task.timeout)
            )
            
            # Send message through communication manager
            if self.communication_manager.send_message(message):
                self.stats['messages_sent'] += 1
                logger.info(f"Task {task.id} assigned to agent {agent_id}")
                return True
            else:
                task.status = WorkflowStatus.FAILED
                task.error_message = "Failed to send task message"
                self.agent_workload[agent_id] -= 1
                return False
            
        except Exception as e:
            logger.error(f"Failed to execute task {task.id}: {e}")
            task.status = WorkflowStatus.FAILED
            task.error_message = str(e)
            return False
    
    def _complete_task(self, task: Task, result: Dict[str, Any]):
        """
        Mark a task as completed and update workflow.
        
        Args:
            task: Completed task
            result: Task execution result
        """
        try:
            task.status = WorkflowStatus.COMPLETED
            task.completed_at = datetime.now()
            task.output_data = result
            
            # Remove from running tasks
            if task.id in self.running_tasks:
                del self.running_tasks[task.id]
            
            # Update agent workload
            for agent_id in self.agent_workload:
                if self.agent_workload[agent_id] > 0:
                    self.agent_workload[agent_id] -= 1
                    break
            
            self.stats['tasks_executed'] += 1
            
            # Check if workflow can be progressed
            self._check_workflow_progress(task)
            
            logger.info(f"Task completed: {task.id}")
            
        except Exception as e:
            logger.error(f"Failed to complete task {task.id}: {e}")
    
    def _fail_task(self, task: Task, error_message: str):
        """
        Mark a task as failed and handle retry logic.
        
        Args:
            task: Failed task
            error_message: Error description
        """
        try:
            task.retry_count += 1
            
            if task.retry_count < task.max_retries:
                # Retry task
                task.status = WorkflowStatus.PENDING
                task.error_message = f"Retry {task.retry_count}: {error_message}"
                self._queue_task(task)
                logger.warning(f"Task {task.id} failed, retrying ({task.retry_count}/{task.max_retries})")
            else:
                # Task failed permanently
                task.status = WorkflowStatus.FAILED
                task.error_message = error_message
                task.completed_at = datetime.now()
                
                # Remove from running tasks
                if task.id in self.running_tasks:
                    del self.running_tasks[task.id]
                
                self.stats['tasks_failed'] += 1
                
                # Check if workflow should be failed
                self._check_workflow_failure(task)
                
                logger.error(f"Task failed permanently: {task.id} - {error_message}")
            
        except Exception as e:
            logger.error(f"Failed to handle task failure {task.id}: {e}")
    
    def _check_workflow_progress(self, completed_task: Task):
        """
        Check if workflow can progress after task completion.
        
        Args:
            completed_task: Task that was just completed
        """
        try:
            # Find workflow containing this task
            workflow = None
            for wf in self.active_workflows.values():
                if any(task.id == completed_task.id for task in wf.tasks):
                    workflow = wf
                    break
            
            if not workflow:
                return
            
            # Check for tasks that can now be executed
            for task in workflow.tasks:
                if (task.status == WorkflowStatus.PENDING and 
                    all(self._is_task_completed(workflow, dep_id) for dep_id in task.depends_on)):
                    self._queue_task(task)
            
            # Check if workflow is complete
            if all(task.status in [WorkflowStatus.COMPLETED, WorkflowStatus.FAILED] for task in workflow.tasks):
                self._complete_workflow(workflow)
            
        except Exception as e:
            logger.error(f"Failed to check workflow progress: {e}")
    
    def _check_workflow_failure(self, failed_task: Task):
        """
        Check if workflow should be marked as failed.
        
        Args:
            failed_task: Task that failed permanently
        """
        try:
            # Find workflow containing this task
            workflow = None
            for wf in self.active_workflows.values():
                if any(task.id == failed_task.id for task in wf.tasks):
                    workflow = wf
                    break
            
            if not workflow:
                return
            
            # Check if any pending tasks depend on the failed task
            dependent_tasks = [
                task for task in workflow.tasks
                if failed_task.id in task.depends_on and task.status == WorkflowStatus.PENDING
            ]
            
            # Fail dependent tasks
            for task in dependent_tasks:
                task.status = WorkflowStatus.FAILED
                task.error_message = f"Dependency failed: {failed_task.id}"
                task.completed_at = datetime.now()
            
            # Check if workflow should be failed
            failed_tasks = [task for task in workflow.tasks if task.status == WorkflowStatus.FAILED]
            if len(failed_tasks) >= len(workflow.tasks) * 0.5:  # If 50% or more tasks failed
                workflow.status = WorkflowStatus.FAILED
                workflow.completed_at = datetime.now()
                
                # Move to completed workflows
                del self.active_workflows[workflow.id]
                self.completed_workflows[workflow.id] = workflow
                self.stats['workflows_failed'] += 1
                
                logger.error(f"Workflow failed: {workflow.id}")
            
        except Exception as e:
            logger.error(f"Failed to check workflow failure: {e}")
    
    def _complete_workflow(self, workflow: Workflow):
        """
        Mark workflow as completed.
        
        Args:
            workflow: Workflow to complete
        """
        try:
            workflow.status = WorkflowStatus.COMPLETED
            workflow.completed_at = datetime.now()
            
            # Move to completed workflows
            del self.active_workflows[workflow.id]
            self.completed_workflows[workflow.id] = workflow
            self.stats['workflows_completed'] += 1
            
            logger.info(f"Workflow completed: {workflow.id}")
            
        except Exception as e:
            logger.error(f"Failed to complete workflow {workflow.id}: {e}")
    
    def _is_task_completed(self, workflow: Workflow, task_id: str) -> bool:
        """Check if a task in the workflow is completed."""
        for task in workflow.tasks:
            if task.id == task_id:
                return task.status == WorkflowStatus.COMPLETED
        return False
    
    def _task_to_dict(self, task: Task) -> Dict[str, Any]:
        """Convert task to dictionary representation."""
        return {
            'id': task.id,
            'name': task.name,
            'agent_type': task.agent_type,
            'status': task.status.value,
            'priority': task.priority.value,
            'depends_on': task.depends_on,
            'created_at': task.created_at.isoformat() if task.created_at else None,
            'started_at': task.started_at.isoformat() if task.started_at else None,
            'completed_at': task.completed_at.isoformat() if task.completed_at else None,
            'retry_count': task.retry_count,
            'max_retries': task.max_retries,
            'error_message': task.error_message
        }
    
    def _message_handler(self, message: Message):
        """Handle incoming messages from other agents."""
        try:
            self.stats['messages_received'] += 1
            
            # Handle task completion messages
            if message.subject.startswith("Task Completed:"):
                task_id = message.payload.get('task_id')
                result = message.payload.get('result', {})
                
                if task_id in self.running_tasks:
                    task = self.running_tasks[task_id]
                    self._complete_task(task, result)
            
            # Handle task failure messages
            elif message.subject.startswith("Task Failed:"):
                task_id = message.payload.get('task_id')
                error_message = message.payload.get('error_message', 'Unknown error')
                
                if task_id in self.running_tasks:
                    task = self.running_tasks[task_id]
                    self._fail_task(task, error_message)
            
            # Handle agent registration messages
            elif message.subject == "Agent Registration":
                agent_info = message.payload
                self.register_agent(message.sender, agent_info)
            
            logger.debug(f"Message processed from {message.sender}: {message.subject}")
            
        except Exception as e:
            logger.error(f"Failed to handle message: {e}")
    
    def _workflow_executor(self):
        """Background thread for executing workflows."""
        logger.info("Workflow executor started")
        
        while self.running:
            try:
                # Process task queue
                if self.task_queue:
                    task = self.task_queue.pop(0)
                    
                    # Check if task dependencies are met
                    workflow = None
                    for wf in self.active_workflows.values():
                        if any(t.id == task.id for t in wf.tasks):
                            workflow = wf
                            break
                    
                    if workflow and all(self._is_task_completed(workflow, dep_id) for dep_id in task.depends_on):
                        self._execute_task(task)
                    else:
                        # Re-queue task if dependencies not met
                        self._queue_task(task)
                
                # Check for timed out tasks
                current_time = datetime.now()
                timed_out_tasks = []
                
                for task in self.running_tasks.values():
                    if task.started_at:
                        elapsed = (current_time - task.started_at).seconds
                        if elapsed > task.timeout:
                            timed_out_tasks.append(task)
                
                for task in timed_out_tasks:
                    self._fail_task(task, f"Task timed out after {task.timeout} seconds")
                
                # Small delay to prevent busy waiting
                threading.Event().wait(1)
                
            except Exception as e:
                logger.error(f"Error in workflow executor: {e}")
                threading.Event().wait(5)  # Wait longer on error
        
        logger.info("Workflow executor stopped")
    
    def get_statistics(self) -> Dict[str, Any]:
        """Get orchestrator statistics."""
        return {
            **self.stats,
            'active_workflows': len(self.active_workflows),
            'completed_workflows': len(self.completed_workflows),
            'registered_agents': len(self.registered_agents),
            'queued_tasks': len(self.task_queue),
            'running_tasks': len(self.running_tasks)
        }
