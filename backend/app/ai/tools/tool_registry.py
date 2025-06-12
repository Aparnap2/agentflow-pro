from typing import Dict, Type, Any, Optional
from pydantic import BaseModel
import logging

logger = logging.getLogger(__name__)

class ToolResult(BaseModel):
    success: bool
    output: Optional[Any] = None
    error: Optional[str] = None
    metadata: Dict[str, Any] = {}

class BaseTool(ABC):
    """Base class for all tools."""
    
    def __init__(self, name: str, description: str = ""):
        self.name = name
        self.description = description
    
    async def execute(self, params: Dict[str, Any]) -> ToolResult:
        """Execute the tool with the given parameters."""
        try:
            result = await self._execute(params)
            return ToolResult(
                success=True,
                output=result,
                metadata={"tool": self.name}
            )
        except Exception as e:
            logger.error(f"Error executing tool {self.name}: {str(e)}", exc_info=True)
            return ToolResult(
                success=False,
                error=str(e),
                metadata={"tool": self.name}
            )
    
    @abstractmethod
    async def _execute(self, params: Dict[str, Any]) -> Any:
        """Tool-specific execution logic to be implemented by subclasses."""
        pass

class ToolRegistry:
    _instance = None
    
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._instance._tools: Dict[str, BaseTool] = {}
        return cls._instance
    
    def register(self, tool: BaseTool) -> None:
        """Register a tool with the registry."""
        if tool.name in self._tools:
            logger.warning(f"Tool with name '{tool.name}' is already registered and will be overwritten")
        self._tools[tool.name] = tool
        logger.info(f"Registered tool: {tool.name}")
    
    def register_multiple(self, tools: list[BaseTool]) -> None:
        """Register multiple tools at once."""
        for tool in tools:
            self.register(tool)
    
    def get_tool(self, name: str) -> Optional[BaseTool]:
        """Get a tool by name."""
        return self._tools.get(name)
    
    def list_tools(self) -> list[str]:
        """List all registered tool names."""
        return list(self._tools.keys())
    
    def remove_tool(self, name: str) -> bool:
        """Remove a tool from the registry."""
        if name in self._tools:
            del self._tools[name]
            logger.info(f"Removed tool: {name}")
            return True
        logger.warning(f"Attempted to remove non-existent tool: {name}")
        return False
    
    def clear(self) -> None:
        """Clear all tools from the registry."""
        count = len(self._tools)
        self._tools.clear()
        logger.info(f"Cleared all {count} tools from registry")
    
    async def execute_tool(self, tool_name: str, params: Dict[str, Any]) -> ToolResult:
        """Execute a tool by name with the given parameters."""
        tool = self.get_tool(tool_name)
        if not tool:
            return ToolResult(
                success=False,
                error=f"Tool '{tool_name}' not found"
            )
        
        try:
            return await tool.execute(params)
        except Exception as e:
            logger.error(f"Error executing tool '{tool_name}': {str(e)}", exc_info=True)
            return ToolResult(
                success=False,
                error=f"Failed to execute tool: {str(e)}"
            )

# Singleton instance
tool_registry = ToolRegistry()

def register_tools(tools: list[BaseTool]) -> None:
    """Helper function to register multiple tools."""
    tool_registry.register_multiple(tools)

def get_tool(name: str) -> Optional[BaseTool]:
    """Helper function to get a tool by name."""
    return tool_registry.get_tool(name)

async def execute_tool(tool_name: str, params: Dict[str, Any]) -> ToolResult:
    """Helper function to execute a tool by name."""
    return await tool_registry.execute_tool(tool_name, params)
