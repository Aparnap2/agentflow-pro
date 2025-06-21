from fastapi import APIRouter
from app.services.tool_manager import ToolManager
from app.services.crawl4ai import Crawl4AIService
from app.services.email_calendar import EmailCalendarService
from app.services.social_media import SocialMediaService

router = APIRouter(prefix="/tools", tags=["tools"])

tool_manager = ToolManager()
crawl4ai = Crawl4AIService()
email_calendar = EmailCalendarService()
social_media = SocialMediaService()

@router.post("/register")
def register_tool(tool_id: str, tool_info: dict):
    return tool_manager.register_tool(tool_id, tool_info)

@router.get("/list")
def list_tools():
    return tool_manager.list_tools()

@router.delete("/remove/{tool_id}")
def remove_tool(tool_id: str):
    return tool_manager.remove_tool(tool_id)

@router.post("/crawl4ai/trigger")
def trigger_crawl(url: str):
    return crawl4ai.trigger_crawl(url)

@router.get("/crawl4ai/results/{crawl_id}")
def fetch_crawl_results(crawl_id: str):
    return crawl4ai.fetch_results(crawl_id)

@router.post("/email/send")
def send_email(to: str, subject: str, body: str):
    return email_calendar.send_email(to, subject, body)

@router.get("/email/fetch")
def fetch_emails(folder: str = "inbox"):
    return email_calendar.fetch_emails(folder)

@router.post("/calendar/event")
def create_event(title: str, start_time: str, end_time: str):
    return email_calendar.create_event(title, start_time, end_time)

@router.post("/social/post")
def post_message(platform: str, message: str):
    return social_media.post_message(platform, message)

@router.get("/social/fetch")
def fetch_messages(platform: str, count: int = 10):
    return social_media.fetch_messages(platform, count) 