"""
Example usage of the LangGraphOrchestrator with agent workflows.

This script demonstrates how to:
1. Initialize the required services
2. Create a workflow with multiple agents
3. Execute tasks through the workflow
4. Handle the results
"""
import asyncio
import logging
from datetime import datetime, timedelta
from typing import Dict, Any

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Import the orchestrator and services
from app.workflows import LangGraphOrchestrator
from app.services.memory import GraphitiMemoryService
from app.services.rag import QdrantRAGService

# Sample task data
SAMPLE_TASKS = [
    {
        "task_id": "task_legal_1",
        "title": "Review NDA for new client",
        "description": "We need to review the NDA for our new client Acme Corp. Please analyze the terms and highlight any potential risks.",
        "priority": "high",
        "tags": ["legal", "nda"],
        "deadline": (datetime.utcnow() + timedelta(days=2)).isoformat()
    },
    {
        "task_id": "task_finance_1",
        "title": "Q2 Financial Analysis",
        "description": "Analyze our Q2 financial performance and prepare a report with key metrics and insights.",
        "priority": "medium",
        "tags": ["finance", "reporting"],
        "deadline": (datetime.utcnow() + timedelta(days=5)).isoformat()
    },
    {
        "task_id": "task_support_1",
        "title": "Customer onboarding issue",
        "description": "A customer is having trouble with the onboarding process. Please assist them in resolving the issue.",
        "priority": "high",
        "tags": ["support", "onboarding"],
        "deadline": (datetime.utcnow() + timedelta(hours=4)).isoformat()
    }
]

async def run_example():
    """Run the workflow example."""
    logger.info("Starting workflow example...")
    
    try:
        # Initialize services
        logger.info("Initializing services...")
        memory_service = GraphitiMemoryService()
        rag_service = QdrantRAGService()
        
        # Create orchestrator
        logger.info("Creating orchestrator...")
        orchestrator = LangGraphOrchestrator(
            memory_service=memory_service,
            rag_service=rag_service
        )
        
        # Process sample tasks
        for task in SAMPLE_TASKS:
            logger.info(f"\nProcessing task: {task['title']}")
            logger.info(f"Description: {task['description']}")
            
            # Execute the workflow
            result = await orchestrator.process_task(
                task=task,
                user_id="example_user"
            )
            
            # Display results
            if result.get("status") == "success":
                logger.info("Workflow completed successfully!")
                logger.info(f"Final agent: {result.get('agent_id')}")
                logger.info(f"Completed: {result.get('completed')}")
                
                # Show the last message
                if result.get("messages"):
                    last_msg = result["messages"][-1]
                    logger.info(f"Last message: {last_msg['content']}")
                    
                # Show reasoning steps if available
                if result.get("reasoning_steps"):
                    logger.info("\nReasoning steps:")
                    for i, step in enumerate(result["reasoning_steps"][:3], 1):  # Show first 3 steps
                        logger.info(f"{i}. {step.get('step', 'No step description')}")
                    if len(result["reasoning_steps"]) > 3:
                        logger.info(f"... and {len(result['reasoning_steps']) - 3} more steps")
                
            else:
                logger.error(f"Workflow failed: {result.get('error')}")
            
            logger.info("-" * 50)
    
    except Exception as e:
        logger.exception("Error in workflow example")
        raise
    
    logger.info("Workflow example completed")

if __name__ == "__main__":
    asyncio.run(run_example())
