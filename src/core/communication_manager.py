"""
Communication Manager for inter-agent communication.

This module manages communication between different agents in the system,
providing message routing, queuing, and coordination capabilities.
"""

import asyncio
import logging
import threading
import uuid
from datetime import datetime, timedelta
from enum import Enum
from typing import Dict, List, Optional, Any, Callable
from dataclasses import dataclass, field
from collections import defaultdict, deque
import json

logger = logging.getLogger(__name__)

class MessageType(Enum):
    """Message types for inter-agent communication."""
    REQUEST = "request"
    RESPONSE = "response"
    NOTIFICATION = "notification"
    BROADCAST = "broadcast"
    ERROR = "error"
    SYSTEM = "system"

class MessagePriority(Enum):
    """Message priority levels."""
    LOW = 1
    NORMAL = 2
    HIGH = 3
    CRITICAL = 4

@dataclass
class Message:
    """Message structure for inter-agent communication."""
    id: str = field(default_factory=lambda: str(uuid.uuid4()))
    type: MessageType = MessageType.REQUEST
    priority: MessagePriority = MessagePriority.NORMAL
    sender: str = ""
    recipient: str = ""
    subject: str = ""
    payload: Dict[str, Any] = field(default_factory=dict)
    timestamp: datetime = field(default_factory=datetime.now)
    expires_at: Optional[datetime] = None
    correlation_id: Optional[str] = None
    reply_to: Optional[str] = None
    delivery_count: int = 0
    max_retries: int = 3
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert message to dictionary."""
        return {
            'id': self.id,
            'type': self.type.value,
            'priority': self.priority.value,
            'sender': self.sender,
            'recipient': self.recipient,
            'subject': self.subject,
            'payload': self.payload,
            'timestamp': self.timestamp.isoformat(),
            'expires_at': self.expires_at.isoformat() if self.expires_at else None,
            'correlation_id': self.correlation_id,
            'reply_to': self.reply_to,
            'delivery_count': self.delivery_count,
            'max_retries': self.max_retries
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'Message':
        """Create message from dictionary."""
        msg = cls()
        msg.id = data.get('id', msg.id)
        msg.type = MessageType(data.get('type', MessageType.REQUEST.value))
        msg.priority = MessagePriority(data.get('priority', MessagePriority.NORMAL.value))
        msg.sender = data.get('sender', '')
        msg.recipient = data.get('recipient', '')
        msg.subject = data.get('subject', '')
        msg.payload = data.get('payload', {})
        msg.timestamp = datetime.fromisoformat(data['timestamp']) if data.get('timestamp') else datetime.now()
        msg.expires_at = datetime.fromisoformat(data['expires_at']) if data.get('expires_at') else None
        msg.correlation_id = data.get('correlation_id')
        msg.reply_to = data.get('reply_to')
        msg.delivery_count = data.get('delivery_count', 0)
        msg.max_retries = data.get('max_retries', 3)
        return msg
    
    def is_expired(self) -> bool:
        """Check if message has expired."""
        return self.expires_at is not None and datetime.now() > self.expires_at
    
    def can_retry(self) -> bool:
        """Check if message can be retried."""
        return self.delivery_count < self.max_retries

@dataclass
class AgentInfo:
    """Information about registered agents."""
    id: str
    name: str
    description: str
    capabilities: List[str]
    status: str = "active"  # active, inactive, busy, error
    last_seen: datetime = field(default_factory=datetime.now)
    message_count: int = 0
    error_count: int = 0

class CommunicationManager:
    """
    Manages communication between agents in the system.
    
    Features:
    - Message routing and delivery
    - Agent registration and discovery
    - Message queuing and priority handling
    - Event broadcasting
    - Request/response correlation
    - Message persistence and retry logic
    """
    
    def __init__(self, max_queue_size: int = 1000):
        self.max_queue_size = max_queue_size
        self.agents: Dict[str, AgentInfo] = {}
        self.message_queues: Dict[str, deque] = defaultdict(lambda: deque(maxlen=max_queue_size))
        self.subscribers: Dict[str, List[str]] = defaultdict(list)  # event -> agent_ids
        self.message_handlers: Dict[str, Callable] = {}  # agent_id -> handler function
        self.pending_responses: Dict[str, Message] = {}  # correlation_id -> message
        self.message_history: deque = deque(maxlen=10000)  # Keep last 10k messages
        
        # Threading and async support
        self.lock = threading.RLock()
        self.running = False
        self.background_thread: Optional[threading.Thread] = None
        
        # Statistics
        self.stats = {
            'messages_sent': 0,
            'messages_delivered': 0,
            'messages_failed': 0,
            'messages_expired': 0,
            'agents_registered': 0
        }
        
        logger.info("Communication Manager initialized")
    
    def start(self):
        """Start the communication manager background processing."""
        with self.lock:
            if not self.running:
                self.running = True
                self.background_thread = threading.Thread(target=self._background_processor, daemon=True)
                self.background_thread.start()
                logger.info("Communication Manager started")
    
    def stop(self):
        """Stop the communication manager."""
        with self.lock:
            self.running = False
            if self.background_thread:
                self.background_thread.join(timeout=5)
                self.background_thread = None
            logger.info("Communication Manager stopped")
    
    def register_agent(self, agent_id: str, name: str, description: str = "", 
                      capabilities: List[str] = None, handler: Callable = None) -> bool:
        """
        Register an agent with the communication manager.
        
        Args:
            agent_id: Unique identifier for the agent
            name: Human-readable name
            description: Description of the agent's purpose
            capabilities: List of capabilities the agent provides
            handler: Optional message handler function
            
        Returns:
            True if registered successfully, False otherwise
        """
        try:
            with self.lock:
                if agent_id in self.agents:
                    logger.warning(f"Agent {agent_id} already registered, updating info")
                
                self.agents[agent_id] = AgentInfo(
                    id=agent_id,
                    name=name,
                    description=description,
                    capabilities=capabilities or []
                )
                
                if handler:
                    self.message_handlers[agent_id] = handler
                
                # Initialize message queue for agent
                if agent_id not in self.message_queues:
                    self.message_queues[agent_id] = deque(maxlen=self.max_queue_size)
                
                self.stats['agents_registered'] += 1
                logger.info(f"Agent registered: {agent_id} ({name})")
                return True
                
        except Exception as e:
            logger.error(f"Failed to register agent {agent_id}: {e}")
            return False
    
    def unregister_agent(self, agent_id: str) -> bool:
        """
        Unregister an agent from the communication manager.
        
        Args:
            agent_id: ID of the agent to unregister
            
        Returns:
            True if unregistered successfully, False otherwise
        """
        try:
            with self.lock:
                if agent_id in self.agents:
                    del self.agents[agent_id]
                
                if agent_id in self.message_handlers:
                    del self.message_handlers[agent_id]
                
                if agent_id in self.message_queues:
                    del self.message_queues[agent_id]
                
                # Remove from subscriptions
                for event_type in list(self.subscribers.keys()):
                    if agent_id in self.subscribers[event_type]:
                        self.subscribers[event_type].remove(agent_id)
                        if not self.subscribers[event_type]:
                            del self.subscribers[event_type]
                
                logger.info(f"Agent unregistered: {agent_id}")
                return True
                
        except Exception as e:
            logger.error(f"Failed to unregister agent {agent_id}: {e}")
            return False
    
    def send_message(self, message: Message) -> bool:
        """
        Send a message to an agent.
        
        Args:
            message: Message to send
            
        Returns:
            True if queued successfully, False otherwise
        """
        try:
            with self.lock:
                # Validate message
                if not message.recipient:
                    logger.error("Message recipient not specified")
                    return False
                
                if message.is_expired():
                    logger.warning(f"Message {message.id} has expired")
                    self.stats['messages_expired'] += 1
                    return False
                
                # Check if recipient exists
                if message.recipient not in self.agents and message.recipient != "broadcast":
                    logger.error(f"Recipient agent not found: {message.recipient}")
                    self.stats['messages_failed'] += 1
                    return False
                
                # Handle broadcast messages
                if message.recipient == "broadcast":
                    return self._broadcast_message(message)
                
                # Queue message for delivery
                queue = self.message_queues[message.recipient]
                
                # Priority insertion
                if message.priority == MessagePriority.CRITICAL:
                    queue.appendleft(message)
                else:
                    queue.append(message)
                
                # Update statistics
                self.stats['messages_sent'] += 1
                self.message_history.append(message)
                
                # Update agent stats
                if message.sender in self.agents:
                    self.agents[message.sender].message_count += 1
                
                logger.debug(f"Message queued: {message.id} from {message.sender} to {message.recipient}")
                return True
                
        except Exception as e:
            logger.error(f"Failed to send message {message.id}: {e}")
            self.stats['messages_failed'] += 1
            return False
    
    def get_messages(self, agent_id: str, max_messages: int = 10) -> List[Message]:
        """
        Get pending messages for an agent.
        
        Args:
            agent_id: ID of the agent requesting messages
            max_messages: Maximum number of messages to return
            
        Returns:
            List of messages for the agent
        """
        try:
            with self.lock:
                if agent_id not in self.agents:
                    logger.error(f"Agent not registered: {agent_id}")
                    return []
                
                queue = self.message_queues[agent_id]
                messages = []
                
                for _ in range(min(max_messages, len(queue))):
                    if queue:
                        message = queue.popleft()
                        
                        # Check if message has expired
                        if message.is_expired():
                            logger.warning(f"Expired message removed: {message.id}")
                            self.stats['messages_expired'] += 1
                            continue
                        
                        message.delivery_count += 1
                        messages.append(message)
                        self.stats['messages_delivered'] += 1
                
                # Update agent last seen
                self.agents[agent_id].last_seen = datetime.now()
                
                return messages
                
        except Exception as e:
            logger.error(f"Failed to get messages for agent {agent_id}: {e}")
            return []
    
    def send_request(self, sender: str, recipient: str, subject: str, 
                    payload: Dict[str, Any], timeout: int = 30) -> Optional[Message]:
        """
        Send a request message and wait for response.
        
        Args:
            sender: ID of the sending agent
            recipient: ID of the recipient agent
            subject: Subject of the request
            payload: Request data
            timeout: Timeout in seconds
            
        Returns:
            Response message if received, None if timeout
        """
        try:
            # Create request message
            correlation_id = str(uuid.uuid4())
            request = Message(
                type=MessageType.REQUEST,
                sender=sender,
                recipient=recipient,
                subject=subject,
                payload=payload,
                correlation_id=correlation_id,
                expires_at=datetime.now() + timedelta(seconds=timeout)
            )
            
            # Send request
            if not self.send_message(request):
                return None
            
            # Wait for response
            start_time = datetime.now()
            while (datetime.now() - start_time).seconds < timeout:
                if correlation_id in self.pending_responses:
                    response = self.pending_responses.pop(correlation_id)
                    return response
                
                threading.Event().wait(0.1)  # Small delay
            
            logger.warning(f"Request timeout: {correlation_id}")
            return None
            
        except Exception as e:
            logger.error(f"Failed to send request: {e}")
            return None
    
    def send_response(self, original_message: Message, response_payload: Dict[str, Any]) -> bool:
        """
        Send a response to a request message.
        
        Args:
            original_message: The original request message
            response_payload: Response data
            
        Returns:
            True if sent successfully, False otherwise
        """
        try:
            if not original_message.correlation_id:
                logger.error("Cannot send response: original message has no correlation ID")
                return False
            
            response = Message(
                type=MessageType.RESPONSE,
                sender=original_message.recipient,
                recipient=original_message.sender,
                subject=f"Re: {original_message.subject}",
                payload=response_payload,
                correlation_id=original_message.correlation_id
            )
            
            # Store response for retrieval
            self.pending_responses[original_message.correlation_id] = response
            
            return self.send_message(response)
            
        except Exception as e:
            logger.error(f"Failed to send response: {e}")
            return False
    
    def subscribe_to_event(self, agent_id: str, event_type: str) -> bool:
        """
        Subscribe an agent to an event type.
        
        Args:
            agent_id: ID of the subscribing agent
            event_type: Type of event to subscribe to
            
        Returns:
            True if subscribed successfully, False otherwise
        """
        try:
            with self.lock:
                if agent_id not in self.agents:
                    logger.error(f"Agent not registered: {agent_id}")
                    return False
                
                if agent_id not in self.subscribers[event_type]:
                    self.subscribers[event_type].append(agent_id)
                    logger.info(f"Agent {agent_id} subscribed to event {event_type}")
                
                return True
                
        except Exception as e:
            logger.error(f"Failed to subscribe agent {agent_id} to event {event_type}: {e}")
            return False
    
    def unsubscribe_from_event(self, agent_id: str, event_type: str) -> bool:
        """
        Unsubscribe an agent from an event type.
        
        Args:
            agent_id: ID of the agent to unsubscribe
            event_type: Type of event to unsubscribe from
            
        Returns:
            True if unsubscribed successfully, False otherwise
        """
        try:
            with self.lock:
                if agent_id in self.subscribers[event_type]:
                    self.subscribers[event_type].remove(agent_id)
                    logger.info(f"Agent {agent_id} unsubscribed from event {event_type}")
                
                if not self.subscribers[event_type]:
                    del self.subscribers[event_type]
                
                return True
                
        except Exception as e:
            logger.error(f"Failed to unsubscribe agent {agent_id} from event {event_type}: {e}")
            return False
    
    def broadcast_event(self, sender: str, event_type: str, payload: Dict[str, Any]) -> int:
        """
        Broadcast an event to all subscribed agents.
        
        Args:
            sender: ID of the sending agent
            event_type: Type of event
            payload: Event data
            
        Returns:
            Number of agents the event was sent to
        """
        try:
            with self.lock:
                subscribers = self.subscribers.get(event_type, [])
                
                if not subscribers:
                    logger.debug(f"No subscribers for event type: {event_type}")
                    return 0
                
                sent_count = 0
                for subscriber in subscribers:
                    event_message = Message(
                        type=MessageType.NOTIFICATION,
                        sender=sender,
                        recipient=subscriber,
                        subject=f"Event: {event_type}",
                        payload=payload
                    )
                    
                    if self.send_message(event_message):
                        sent_count += 1
                
                logger.info(f"Event {event_type} broadcast to {sent_count} agents")
                return sent_count
                
        except Exception as e:
            logger.error(f"Failed to broadcast event {event_type}: {e}")
            return 0
    
    def get_agent_info(self, agent_id: str) -> Optional[AgentInfo]:
        """Get information about a registered agent."""
        return self.agents.get(agent_id)
    
    def list_agents(self) -> List[AgentInfo]:
        """Get list of all registered agents."""
        return list(self.agents.values())
    
    def get_agents_by_capability(self, capability: str) -> List[AgentInfo]:
        """Get agents that have a specific capability."""
        return [agent for agent in self.agents.values() if capability in agent.capabilities]
    
    def get_statistics(self) -> Dict[str, Any]:
        """Get communication statistics."""
        with self.lock:
            return {
                **self.stats,
                'active_agents': len(self.agents),
                'total_queue_size': sum(len(queue) for queue in self.message_queues.values()),
                'pending_responses': len(self.pending_responses),
                'event_subscriptions': len(self.subscribers)
            }
    
    def clear_expired_messages(self):
        """Remove expired messages from all queues."""
        try:
            with self.lock:
                expired_count = 0
                
                for agent_id, queue in self.message_queues.items():
                    # Create new queue with non-expired messages
                    new_queue = deque(maxlen=self.max_queue_size)
                    
                    while queue:
                        message = queue.popleft()
                        if not message.is_expired():
                            new_queue.append(message)
                        else:
                            expired_count += 1
                    
                    self.message_queues[agent_id] = new_queue
                
                # Clean pending responses
                expired_responses = [
                    corr_id for corr_id, msg in self.pending_responses.items()
                    if msg.is_expired()
                ]
                
                for corr_id in expired_responses:
                    del self.pending_responses[corr_id]
                    expired_count += 1
                
                if expired_count > 0:
                    logger.info(f"Cleaned up {expired_count} expired messages")
                    self.stats['messages_expired'] += expired_count
                
        except Exception as e:
            logger.error(f"Failed to clear expired messages: {e}")
    
    def _broadcast_message(self, message: Message) -> bool:
        """Handle broadcast message delivery."""
        try:
            sent_count = 0
            
            for agent_id in self.agents.keys():
                if agent_id != message.sender:  # Don't send to sender
                    broadcast_msg = Message(
                        type=message.type,
                        priority=message.priority,
                        sender=message.sender,
                        recipient=agent_id,
                        subject=message.subject,
                        payload=message.payload,
                        timestamp=message.timestamp,
                        expires_at=message.expires_at
                    )
                    
                    queue = self.message_queues[agent_id]
                    queue.append(broadcast_msg)
                    sent_count += 1
            
            logger.info(f"Broadcast message sent to {sent_count} agents")
            return sent_count > 0
            
        except Exception as e:
            logger.error(f"Failed to broadcast message: {e}")
            return False
    
    def _background_processor(self):
        """Background thread for periodic maintenance tasks."""
        logger.info("Communication Manager background processor started")
        
        while self.running:
            try:
                # Clean up expired messages every 60 seconds
                self.clear_expired_messages()
                
                # Update agent statuses
                current_time = datetime.now()
                for agent_id, agent in self.agents.items():
                    time_since_seen = (current_time - agent.last_seen).seconds
                    
                    if time_since_seen > 300:  # 5 minutes
                        if agent.status == "active":
                            agent.status = "inactive"
                            logger.warning(f"Agent {agent_id} marked as inactive")
                
                # Sleep for 30 seconds before next iteration
                for _ in range(30):
                    if not self.running:
                        break
                    threading.Event().wait(1)
                
            except Exception as e:
                logger.error(f"Error in background processor: {e}")
                threading.Event().wait(10)  # Wait longer on error
        
        logger.info("Communication Manager background processor stopped")
