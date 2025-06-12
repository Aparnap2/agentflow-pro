"""
Example demonstrating the integration of CrewAI and LangGraph in a workflow.
"""
import asyncio
import os
from dotenv import load_dotenv
from datetime import datetime

# Load environment variables
load_dotenv()

# Configure logging
import logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Import the necessary components
from app.ai.agents.agent_factory import agent_factory
from app.ai.workflow.workflow_manager import Workflow
from app.ai.integrations import CrewAIWorkflowStep

# Example agent configurations
AGENT_CONFIGS = {
    "researcher": {
        "name": "Researcher",
        "role": "Senior Research Analyst",
        "goal": "Conduct thorough research on given topics",
        "backstory": "You are an expert researcher with years of experience in gathering and analyzing information.",
        "tools": ["web_search"],
        "verbose": True
    },
    "writer": {
        "name": "Writer",
        "role": "Content Writer",
        "goal": "Write engaging and informative content",
        "backstory": "You are a skilled writer who can create compelling content based on research findings.",
        "verbose": True
    },
    "editor": {
        "name": "Editor",
        "role": "Senior Editor",
        "goal": "Review and improve written content",
        "backstory": "You are an experienced editor with a keen eye for detail and a talent for improving clarity and flow.",
        "verbose": True
    }
}

# Example workflow configuration
WORKFLOW_CONFIG = {
    "workflow_id": "content_creation",
    "name": "Content Creation Workflow",
    "description": "A workflow that creates content using multiple AI agents"
}

async def setup_agents():
    """Set up the agents using the agent factory."""
    for agent_id, config in AGENT_CONFIGS.items():
        await agent_factory.create_agent(
            agent_type="base",  # Using base agent type for simplicity
            agent_id=agent_id,
            **config
        )
    logger.info("Agents set up successfully")

async def create_crew():
    """Create a CrewAI crew with the configured agents."""
    crew = agent_factory.crewai_integration.create_crew(
        crew_id="content_team",
        name="Content Creation Team",
        agent_ids=list(AGENT_CONFIGS.keys()),
        config={
            "process": "hierarchical",  # Use hierarchical process for agent delegation
            "verbose": True
        }
    )
    logger.info("Crew created successfully")
    return crew

def create_workflow() -> Workflow:
    """Create a workflow with CrewAI steps."""
    workflow = Workflow(
        workflow_id=WORKFLOW_CONFIG["workflow_id"],
        name=WORKFLOW_CONFIG["name"],
        metadata={"description": WORKFLOW_CONFIG["description"]}
    )
    
    # Add CrewAI step for research
    research_step = CrewAIWorkflowStep(
        name="research_step",
        crew_id="content_team",
        task_template="Research the following topic: {topic}",
        output_key="research_results"
    )
    workflow.add_step(research_step)
    
    # Add CrewAI step for writing
    write_step = CrewAIWorkflowStep(
        name="write_step",
        crew_id="content_team",
        task_template="Write an article based on this research: {research_results}",
        output_key="draft_article"
    )
    workflow.add_step(write_step)
    
    # Add editing step
    edit_step = CrewAIWorkflowStep(
        name="edit_step",
        crew_id="content_team",
        task_template="Edit and improve this article for {target_audience} with a {tone} tone: {draft_article}",
        output_key="final_article"
    )
    workflow.add_step(edit_step)
    
    logger.info("Workflow created with 3 steps: research, write, edit")
    return workflow

async def main():
    """Run the example workflow."""
    try:
        # Initialize the agent factory
        await agent_factory.initialize()
        
        # Set up agents
        await setup_agents()
        
        # Create a crew
        await create_crew()
        
        # Create the workflow
        workflow = create_workflow()
        
        # Define the input data
        input_data = {
            "topic": "The impact of AI on content creation",
            "target_audience": "business professionals",
            "tone": "professional"
        }
        
        logger.info("Starting workflow execution...")
        
        # Execute the workflow
        result = await workflow.execute(
            initial_data=input_data,
            trace_id=f"run_{int(datetime.utcnow().timestamp())}"
        )
        
        if result.success:
            logger.info("Workflow completed successfully!")
            logger.info(f"Final output: {result.output.get('final_article', 'No output')}")
        else:
            logger.error(f"Workflow failed: {result.error}")
            
    except Exception as e:
        logger.error(f"An error occurred: {str(e)}", exc_info=True)
    finally:
        # Clean up
        await agent_factory.close()

if __name__ == "__main__":
    asyncio.run(main())
