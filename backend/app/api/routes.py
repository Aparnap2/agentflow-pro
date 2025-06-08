from fastapi import APIRouter, Depends, HTTPException, status
from typing import Dict, Any
from loguru import logger
from ..core.config import settings
from ..services.ai.orchestrator import AIOrchestrator

# Create router
api_router = APIRouter()

# Health check endpoint
@api_router.get("/health", response_model=Dict[str, str])
async def health_check() -> Dict[str, str]:
    return {"status": "ok"}

# Chat endpoint
@api_router.post("/chat", response_model=Dict[str, Any])
async def chat_endpoint(
    payload: Dict[str, Any],
    orchestrator: AIOrchestrator = Depends(lambda: AIOrchestrator())
) -> Dict[str, Any]:
    """
    Process a chat message through the AI workflow
    
    Request body:
    - message: str - The user's message
    - context: Dict - Any additional context
    """
    try:
        message = payload.get("message")
        context = payload.get("context", {})
        
        if not message:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Message is required"
            )
        
        logger.info(f"Processing message: {message[:100]}...")
        
        # Process the message through the AI orchestrator
        response = await orchestrator.process_message(message, context)
        
        return {
            "success": True,
            "data": response,
            "metadata": {
                "model": response.get("metadata", {}).get("model", "unknown"),
                "environment": settings.ENVIRONMENT
            }
        }
        
    except Exception as e:
        logger.error(f"Error processing chat: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )

# Additional endpoints can be added here for specific functionalities
# Example: Knowledge base search, document processing, etc.
