from typing import Dict, List, Any, Optional, Callable
import logging
import asyncio
from datetime import datetime
from pydantic import BaseModel
from enum import Enum

from .crawl4ai import Crawl4AIService, CrawlRequest
from .email_calendar import EmailCalendarService
from .social_media import SocialMediaService

logger = logging.getLogger(__name__)

class ToolType(str, Enum):
    WEB_SCRAPING = "web_scraping"
    EMAIL = "email"
    CALENDAR = "calendar"
    SOCIAL_MEDIA = "social_media"
    API = "api"
    DATABASE = "database"
    FILE_PROCESSING = "file_processing"
    CUSTOM = "custom"

class ToolStatus(str, Enum):
    ACTIVE = "active"
    INACTIVE = "inactive"
    ERROR = "error"
    MAINTENANCE = "maintenance"

class Tool(BaseModel):
    """Tool definition model"""
    id: str
    name: str
    description: str
    tool_type: ToolType
    version: str = "1.0.0"
    status: ToolStatus = ToolStatus.ACTIVE
    config: Dict[str, Any] = {}
    capabilities: List[str] = []
    required_params: List[str] = []
    optional_params: List[str] = []
    output_format: str = "json"
    rate_limit: Optional[int] = None  # requests per minute
    timeout: int = 30  # seconds
    created_at: str
    updated_at: str

class ToolExecution(BaseModel):
    """Tool execution result"""
    execution_id: str
    tool_id: str
    agent_id: str
    parameters: Dict[str, Any]
    result: Optional[Dict[str, Any]] = None
    error: Optional[str] = None
    status: str
    started_at: str
    completed_at: Optional[str] = None
    execution_time: Optional[float] = None

class ToolManager:
    def __init__(self):
        self.tools: Dict[str, Tool] = {}
        self.tool_instances: Dict[str, Any] = {}
        self.execution_history: Dict[str, ToolExecution] = {}
        self.rate_limits: Dict[str, List[datetime]] = {}
        
        # Initialize built-in tools
        self._initialize_builtin_tools()

    def _initialize_builtin_tools(self):
        """Initialize built-in tools"""
        try:
            # Web scraping tool (Crawl4AI)
            crawl_tool = Tool(
                id="crawl4ai",
                name="Web Scraper",
                description="Extract data from websites using Crawl4AI",
                tool_type=ToolType.WEB_SCRAPING,
                capabilities=["web_scraping", "html_parsing", "data_extraction"],
                required_params=["url"],
                optional_params=["crawl_type", "max_pages", "follow_links", "extract_images", "custom_selectors"],
                created_at=datetime.now().isoformat(),
                updated_at=datetime.now().isoformat()
            )
            self.tools["crawl4ai"] = crawl_tool
            self.tool_instances["crawl4ai"] = Crawl4AIService()
            
            # Email tool
            email_tool = Tool(
                id="email_service",
                name="Email Service",
                description="Send emails and manage email campaigns",
                tool_type=ToolType.EMAIL,
                capabilities=["send_email", "email_templates", "bulk_email"],
                required_params=["to", "subject", "body"],
                optional_params=["cc", "bcc", "attachments", "template_id"],
                created_at=datetime.now().isoformat(),
                updated_at=datetime.now().isoformat()
            )
            self.tools["email_service"] = email_tool
            self.tool_instances["email_service"] = EmailCalendarService()
            
            # Calendar tool
            calendar_tool = Tool(
                id="calendar_service",
                name="Calendar Service",
                description="Manage calendar events and scheduling",
                tool_type=ToolType.CALENDAR,
                capabilities=["create_event", "list_events", "update_event", "delete_event"],
                required_params=["action"],
                optional_params=["event_data", "calendar_id", "date_range"],
                created_at=datetime.now().isoformat(),
                updated_at=datetime.now().isoformat()
            )
            self.tools["calendar_service"] = calendar_tool
            # Calendar service is part of EmailCalendarService
            
            # Social media tool
            social_tool = Tool(
                id="social_media",
                name="Social Media Manager",
                description="Manage social media posts and engagement",
                tool_type=ToolType.SOCIAL_MEDIA,
                capabilities=["post_content", "schedule_post", "get_analytics", "manage_engagement"],
                required_params=["platform", "action"],
                optional_params=["content", "media", "schedule_time", "target_audience"],
                created_at=datetime.now().isoformat(),
                updated_at=datetime.now().isoformat()
            )
            self.tools["social_media"] = social_tool
            self.tool_instances["social_media"] = SocialMediaService()
            
            logger.info(f"Initialized {len(self.tools)} built-in tools")
            
        except Exception as e:
            logger.error(f"Failed to initialize built-in tools: {e}")

    async def register_tool(self, tool_data: Dict[str, Any]) -> Dict[str, Any]:
        """Register a new tool"""
        try:
            tool = Tool(**tool_data)
            self.tools[tool.id] = tool
            
            logger.info(f"Registered tool: {tool.id}")
            return {
                "status": "registered",
                "tool_id": tool.id,
                "tool": tool.dict()
            }
            
        except Exception as e:
            logger.error(f"Failed to register tool: {e}")
            return {"error": str(e)}

    async def execute_tool(self, tool_id: str, agent_id: str, parameters: Dict[str, Any]) -> Dict[str, Any]:
        """Execute a tool with given parameters"""
        try:
            if tool_id not in self.tools:
                return {"error": f"Tool {tool_id} not found"}
            
            tool = self.tools[tool_id]
            
            # Check tool status
            if tool.status != ToolStatus.ACTIVE:
                return {"error": f"Tool {tool_id} is not active (status: {tool.status})"}
            
            # Check rate limits
            if not await self._check_rate_limit(tool_id, tool.rate_limit):
                return {"error": f"Rate limit exceeded for tool {tool_id}"}
            
            # Validate required parameters
            missing_params = [param for param in tool.required_params if param not in parameters]
            if missing_params:
                return {"error": f"Missing required parameters: {missing_params}"}
            
            # Create execution record
            execution_id = f"{tool_id}_{agent_id}_{datetime.now().timestamp()}"
            execution = ToolExecution(
                execution_id=execution_id,
                tool_id=tool_id,
                agent_id=agent_id,
                parameters=parameters,
                status="running",
                started_at=datetime.now().isoformat()
            )
            
            self.execution_history[execution_id] = execution
            
            # Execute the tool
            start_time = datetime.now()
            result = await self._execute_tool_logic(tool_id, parameters)
            end_time = datetime.now()
            
            # Update execution record
            execution.completed_at = end_time.isoformat()
            execution.execution_time = (end_time - start_time).total_seconds()
            
            if "error" in result:
                execution.status = "failed"
                execution.error = result["error"]
            else:
                execution.status = "completed"
                execution.result = result
            
            logger.info(f"Tool {tool_id} executed by agent {agent_id} in {execution.execution_time:.2f}s")
            
            return {
                "execution_id": execution_id,
                "status": execution.status,
                "result": execution.result,
                "error": execution.error,
                "execution_time": execution.execution_time
            }
            
        except Exception as e:
            logger.error(f"Failed to execute tool {tool_id}: {e}")
            return {"error": str(e)}

    async def _execute_tool_logic(self, tool_id: str, parameters: Dict[str, Any]) -> Dict[str, Any]:
        """Execute the actual tool logic"""
        try:
            if tool_id == "crawl4ai":
                return await self._execute_crawl4ai(parameters)
            elif tool_id == "email_service":
                return await self._execute_email_service(parameters)
            elif tool_id == "calendar_service":
                return await self._execute_calendar_service(parameters)
            elif tool_id == "social_media":
                return await self._execute_social_media(parameters)
            else:
                # For custom tools, you would implement the execution logic here
                return {"error": f"Execution logic not implemented for tool {tool_id}"}
                
        except Exception as e:
            logger.error(f"Error executing tool {tool_id}: {e}")
            return {"error": str(e)}

    async def _execute_crawl4ai(self, parameters: Dict[str, Any]) -> Dict[str, Any]:
        """Execute Crawl4AI tool"""
        try:
            crawl_service = self.tool_instances["crawl4ai"]
            
            # Create crawl request
            crawl_request = CrawlRequest(
                url=parameters["url"],
                crawl_type=parameters.get("crawl_type", "basic"),
                max_pages=parameters.get("max_pages", 1),
                follow_links=parameters.get("follow_links", False),
                extract_images=parameters.get("extract_images", False),
                custom_selectors=parameters.get("custom_selectors")
            )
            
            # Start crawl
            crawl_result = await crawl_service.trigger_crawl(crawl_request)
            
            if "error" in crawl_result:
                return crawl_result
            
            # Wait for completion (for synchronous execution)
            crawl_id = crawl_result["crawl_id"]
            max_wait = 60  # seconds
            wait_time = 0
            
            while wait_time < max_wait:
                result = await crawl_service.fetch_results(crawl_id)
                if result.get("status") in ["completed", "failed"]:
                    return result
                
                await asyncio.sleep(2)
                wait_time += 2
            
            return {"error": "Crawl timeout"}
            
        except Exception as e:
            return {"error": str(e)}

    async def _execute_email_service(self, parameters: Dict[str, Any]) -> Dict[str, Any]:
        """Execute email service tool"""
        try:
            email_service = self.tool_instances["email_service"]
            
            result = await email_service.send_email(
                to=parameters["to"],
                subject=parameters["subject"],
                body=parameters["body"],
                cc=parameters.get("cc"),
                bcc=parameters.get("bcc"),
                attachments=parameters.get("attachments")
            )
            
            return result
            
        except Exception as e:
            return {"error": str(e)}

    async def _execute_calendar_service(self, parameters: Dict[str, Any]) -> Dict[str, Any]:
        """Execute calendar service tool"""
        try:
            calendar_service = self.tool_instances["email_service"]  # Same service handles calendar
            
            action = parameters["action"]
            
            if action == "create_event":
                return await calendar_service.create_calendar_event(parameters.get("event_data", {}))
            elif action == "list_events":
                return await calendar_service.list_calendar_events(
                    parameters.get("calendar_id"),
                    parameters.get("date_range")
                )
            elif action == "update_event":
                return await calendar_service.update_calendar_event(
                    parameters.get("event_id"),
                    parameters.get("event_data", {})
                )
            elif action == "delete_event":
                return await calendar_service.delete_calendar_event(parameters.get("event_id"))
            else:
                return {"error": f"Unknown calendar action: {action}"}
                
        except Exception as e:
            return {"error": str(e)}

    async def _execute_social_media(self, parameters: Dict[str, Any]) -> Dict[str, Any]:
        """Execute social media tool"""
        try:
            social_service = self.tool_instances["social_media"]
            
            platform = parameters["platform"]
            action = parameters["action"]
            
            if action == "post_content":
                return await social_service.post_content(
                    platform,
                    parameters.get("content", ""),
                    parameters.get("media")
                )
            elif action == "schedule_post":
                return await social_service.schedule_post(
                    platform,
                    parameters.get("content", ""),
                    parameters.get("schedule_time"),
                    parameters.get("media")
                )
            elif action == "get_analytics":
                return await social_service.get_analytics(platform)
            else:
                return {"error": f"Unknown social media action: {action}"}
                
        except Exception as e:
            return {"error": str(e)}

    async def _check_rate_limit(self, tool_id: str, rate_limit: Optional[int]) -> bool:
        """Check if tool execution is within rate limits"""
        if rate_limit is None:
            return True
        
        try:
            current_time = datetime.now()
            
            if tool_id not in self.rate_limits:
                self.rate_limits[tool_id] = []
            
            # Remove old entries (older than 1 minute)
            self.rate_limits[tool_id] = [
                timestamp for timestamp in self.rate_limits[tool_id]
                if (current_time - timestamp).total_seconds() < 60
            ]
            
            # Check if under rate limit
            if len(self.rate_limits[tool_id]) < rate_limit:
                self.rate_limits[tool_id].append(current_time)
                return True
            
            return False
            
        except Exception as e:
            logger.error(f"Error checking rate limit for tool {tool_id}: {e}")
            return True  # Allow execution if rate limit check fails

    async def list_tools(self, tool_type: Optional[ToolType] = None, status: Optional[ToolStatus] = None) -> List[Dict[str, Any]]:
        """List all tools, optionally filtered by type and status"""
        try:
            tools = []
            
            for tool in self.tools.values():
                if tool_type and tool.tool_type != tool_type:
                    continue
                if status and tool.status != status:
                    continue
                
                tools.append(tool.dict())
            
            return tools
            
        except Exception as e:
            logger.error(f"Failed to list tools: {e}")
            return []

    async def get_tool(self, tool_id: str) -> Optional[Dict[str, Any]]:
        """Get a specific tool by ID"""
        try:
            if tool_id in self.tools:
                return self.tools[tool_id].dict()
            return None
            
        except Exception as e:
            logger.error(f"Failed to get tool {tool_id}: {e}")
            return None

    async def update_tool(self, tool_id: str, updates: Dict[str, Any]) -> Dict[str, Any]:
        """Update a tool configuration"""
        try:
            if tool_id not in self.tools:
                return {"error": f"Tool {tool_id} not found"}
            
            tool = self.tools[tool_id]
            
            # Update allowed fields
            allowed_updates = ["name", "description", "status", "config", "rate_limit", "timeout"]
            for key, value in updates.items():
                if key in allowed_updates:
                    setattr(tool, key, value)
            
            tool.updated_at = datetime.now().isoformat()
            
            logger.info(f"Updated tool: {tool_id}")
            return {
                "status": "updated",
                "tool_id": tool_id,
                "tool": tool.dict()
            }
            
        except Exception as e:
            logger.error(f"Failed to update tool {tool_id}: {e}")
            return {"error": str(e)}

    async def remove_tool(self, tool_id: str) -> Dict[str, Any]:
        """Remove a tool"""
        try:
            if tool_id not in self.tools:
                return {"error": f"Tool {tool_id} not found"}
            
            # Don't allow removal of built-in tools
            builtin_tools = ["crawl4ai", "email_service", "calendar_service", "social_media"]
            if tool_id in builtin_tools:
                return {"error": f"Cannot remove built-in tool {tool_id}"}
            
            del self.tools[tool_id]
            
            if tool_id in self.tool_instances:
                del self.tool_instances[tool_id]
            
            logger.info(f"Removed tool: {tool_id}")
            return {"status": "removed", "tool_id": tool_id}
            
        except Exception as e:
            logger.error(f"Failed to remove tool {tool_id}: {e}")
            return {"error": str(e)}

    async def get_execution_history(self, tool_id: Optional[str] = None, agent_id: Optional[str] = None, limit: int = 50) -> List[Dict[str, Any]]:
        """Get tool execution history"""
        try:
            executions = []
            
            for execution in self.execution_history.values():
                if tool_id and execution.tool_id != tool_id:
                    continue
                if agent_id and execution.agent_id != agent_id:
                    continue
                
                executions.append(execution.dict())
            
            # Sort by start time (most recent first)
            executions.sort(key=lambda x: x["started_at"], reverse=True)
            
            return executions[:limit]
            
        except Exception as e:
            logger.error(f"Failed to get execution history: {e}")
            return []

    async def get_tool_stats(self, tool_id: str) -> Dict[str, Any]:
        """Get statistics for a specific tool"""
        try:
            if tool_id not in self.tools:
                return {"error": f"Tool {tool_id} not found"}
            
            executions = [exec for exec in self.execution_history.values() if exec.tool_id == tool_id]
            
            total_executions = len(executions)
            successful_executions = len([exec for exec in executions if exec.status == "completed"])
            failed_executions = len([exec for exec in executions if exec.status == "failed"])
            
            avg_execution_time = 0
            if executions:
                execution_times = [exec.execution_time for exec in executions if exec.execution_time]
                if execution_times:
                    avg_execution_time = sum(execution_times) / len(execution_times)
            
            return {
                "tool_id": tool_id,
                "total_executions": total_executions,
                "successful_executions": successful_executions,
                "failed_executions": failed_executions,
                "success_rate": successful_executions / total_executions if total_executions > 0 else 0,
                "average_execution_time": avg_execution_time
            }
            
        except Exception as e:
            logger.error(f"Failed to get tool stats for {tool_id}: {e}")
            return {"error": str(e)}