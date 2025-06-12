"""
Test script for the agent workflow system.
"""
import asyncio
import logging
import sys
import os
import json
from datetime import datetime
from typing import Dict, Any, List, Optional

# Add the backend directory to the Python path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from app.ai.agents.agent_factory import AgentFactory, agent_factory
from app.ai.workflow.agent_workflow import AgentWorkflow, AgentWorkflowStep, AgentWorkflowStepType

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(),
        logging.FileHandler('agent_workflow_test.log')
    ]
)
logger = logging.getLogger(__name__)

async def test_workflow_execution():
    """Test the execution of an agent workflow."""
    logger.info("Starting workflow execution test")
    
    try:
        # Initialize the agent factory
        await agent_factory.initialize()
        
        # Create a workflow
        workflow = AgentWorkflow(
            workflow_id="test_workflow_1",
            name="Lead Processing Workflow",
            agent_factory=agent_factory
        )
        
        # Add steps to the workflow
        workflow.add_step(AgentWorkflowStep(
            step_id="qualify_lead",
            name="Qualify Lead",
            step_type=AgentWorkflowStepType.AGENT_TASK,
            agent_type="sales",
            task="qualify_lead",
            parameters={"priority": "high"},
            retry_policy={"stop_after_attempt": 3}
        ))
        
        workflow.add_step(AgentWorkflowStep(
            step_id="enrich_lead",
            name="Enrich Lead Data",
            step_type=AgentWorkflowStepType.AGENT_TASK,
            agent_type="sales",
            task="enrich_lead",
            depends_on=["qualify_lead"],
            input_template="""
            Process this lead data and enrich it with additional information:
            {{qualify_lead.output}}
            """,
            timeout=30.0
        ))
        
        workflow.add_step(AgentWorkflowStep(
            step_id="notify_team",
            name="Notify Sales Team",
            step_type=AgentWorkflowStepType.AGENT_TASK,
            agent_type="sales",
            task="notify_team",
            depends_on=["enrich_lead"],
            parameters={
                "channel": "slack",
                "template": "new_qualified_lead"
            }
        ))
        
        # Validate the workflow
        workflow.validate()
        logger.info("Workflow validation successful")
        
        # Test input data
        input_data = {
            "lead": {
                "name": "Acme Corp",
                "email": "contact@acmecorp.com",
                "website": "https://acmecorp.com",
                "budget": 50000,
                "timeframe": "Q3 2023",
                "requirements": "Need an AI solution for customer support automation"
            }
        }
        
        # Execute the workflow
        logger.info("Executing workflow...")
        start_time = datetime.utcnow()
        
        result = await workflow.execute(
            input_data=input_data,
            context={"source": "api", "user_id": "test_user_123"}
        )
        
        execution_time = (datetime.utcnow() - start_time).total_seconds()
        
        # Log results
        logger.info(f"Workflow completed in {execution_time:.2f} seconds")
        logger.info(f"Success: {result.success}")
        
        if result.error:
            logger.error(f"Error: {result.error}")
        
        logger.info("Step results:")
        for step_id, step_result in result.steps.items():
            status = "✅" if step_result.get("success", False) else "❌"
            duration = step_result.get("execution_time_ms", 0)
            logger.info(f"  {status} {step_id}: {step_result.get('status')} ({duration:.2f}ms)")
        
        logger.info("\nFull result:")
        logger.info(json.dumps(result.dict(), indent=2, default=str))
        
        return result
        
    except Exception as e:
        logger.error(f"Test failed: {str(e)}", exc_info=True)
        raise
    finally:
        # Clean up
        await agent_factory.close()

if __name__ == "__main__":
    asyncio.run(test_workflow_execution())
