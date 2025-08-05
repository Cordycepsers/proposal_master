"""
Base agent class for all AI agents in the Proposal Master system.

This module provides the foundation for all specialized agents.
"""

from abc import ABC, abstractmethod
from typing import Dict, Any, List, Optional
import logging

logger = logging.getLogger(__name__)


class BaseAgent(ABC):
    """Base class for all AI agents."""
    
    def __init__(self, name: str, description: str):
        self.name = name
        self.description = description
        self.logger = logging.getLogger(f"{__name__}.{name}")
        self._context = {}
        self._history = []
    
    @abstractmethod
    async def process(self, input_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Process input data and return results.
        
        Args:
            input_data: Input data dictionary
            
        Returns:
            Processed results dictionary
        """
        pass
    
    def set_context(self, context: Dict[str, Any]) -> None:
        """Set context information for the agent."""
        self._context.update(context)
        self.logger.debug(f"Context updated for {self.name}")
    
    def get_context(self) -> Dict[str, Any]:
        """Get current context."""
        return self._context.copy()
    
    def add_to_history(self, entry: Dict[str, Any]) -> None:
        """Add entry to processing history."""
        self._history.append(entry)
        
        # Keep only last 100 entries
        if len(self._history) > 100:
            self._history = self._history[-100:]
    
    def get_history(self, limit: Optional[int] = None) -> List[Dict[str, Any]]:
        """Get processing history."""
        if limit:
            return self._history[-limit:]
        return self._history.copy()
    
    def clear_history(self) -> None:
        """Clear processing history."""
        self._history.clear()
        self.logger.info(f"History cleared for {self.name}")
    
    def log_operation(self, operation: str, details: Dict[str, Any] = None) -> None:
        """Log an operation with optional details."""
        self.logger.info(f"{self.name} - {operation}")
        if details:
            self.logger.debug(f"Operation details: {details}")
        
        # Add to history
        self.add_to_history({
            'timestamp': self._get_timestamp(),
            'operation': operation,
            'details': details or {}
        })
    
    def _get_timestamp(self) -> str:
        """Get current timestamp string."""
        from datetime import datetime
        return datetime.now().isoformat()
    
    def __str__(self) -> str:
        return f"{self.name}: {self.description}"
    
    def __repr__(self) -> str:
        return f"BaseAgent(name='{self.name}', description='{self.description}')"
