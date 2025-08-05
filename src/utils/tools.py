"""
Base tool class for the Automated RFP System.
"""
from abc import ABC, abstractmethod
from typing import Dict, Any, Optional
import logging

logger = logging.getLogger(__name__)


class Tool(ABC):
    """Base class for all system tools."""
    
    name: str = ""
    description: str = ""
    parameters: Dict[str, Dict[str, str]] = {}
    
    def __init__(self):
        if not self.name:
            raise ValueError(f"Tool {self.__class__.__name__} must define a name")
        if not self.description:
            raise ValueError(f"Tool {self.__class__.__name__} must define a description")
    
    @abstractmethod
    def execute(self, **kwargs) -> Dict[str, Any]:
        """Execute the tool with given parameters."""
        pass
    
    def validate_parameters(self, **kwargs) -> bool:
        """Validate that required parameters are present."""
        for param_name, param_info in self.parameters.items():
            if param_info.get("required", False) and param_name not in kwargs:
                raise ValueError(f"Required parameter '{param_name}' missing for {self.name}")
        return True
    
    def log_execution(self, action: str, result: Dict[str, Any]) -> None:
        """Log tool execution for monitoring."""
        logger.info(f"Tool {self.name} executed action '{action}' with result: {result.get('status', 'unknown')}")


class ToolRegistry:
    """Registry for managing available tools."""
    
    def __init__(self):
        self._tools: Dict[str, Tool] = {}
    
    def register(self, tool: Tool) -> None:
        """Register a tool."""
        self._tools[tool.name] = tool
        logger.info(f"Registered tool: {tool.name}")
    
    def get_tool(self, name: str) -> Optional[Tool]:
        """Get a tool by name."""
        return self._tools.get(name)
    
    def list_tools(self) -> Dict[str, str]:
        """List all available tools."""
        return {name: tool.description for name, tool in self._tools.items()}
    
    def execute_tool(self, name: str, **kwargs) -> Dict[str, Any]:
        """Execute a tool by name."""
        tool = self.get_tool(name)
        if not tool:
            return {"error": f"Tool '{name}' not found"}
        
        try:
            tool.validate_parameters(**kwargs)
            result = tool.execute(**kwargs)
            tool.log_execution(name, result)
            return result
        except Exception as e:
            error_result = {"error": str(e), "tool": name}
            logger.error(f"Tool {name} execution failed: {e}")
            return error_result


# Global tool registry
tool_registry = ToolRegistry()
