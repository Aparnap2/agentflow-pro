#!/usr/bin/env python3
"""Seed the database with test agents."""
import asyncio
import sys
from pathlib import Path
from datetime import datetime, timezone

# Add the project root to the Python path
project_root = Path(__file__).parent.parent
sys.path.append(str(project_root))

from app.db.config import init_db, close_db
from app.db.repository import get_repository
from app.db.models import AgentNode, NodeType
from app.api.schemas.agent import AgentCreate, ToolConfig, LLMConfig

# Sample test agents
SAMPLE_AGENTS = [
    {
        "name": "Design Assistant",
        "description": "Helps with UI/UX design tasks",
        "agent_type": "design",
        "tools": [
            {"name": "generate_color_palette", "description": "Generate a color palette based on a base color"},
            {"name": "check_accessibility", "description": "Check color contrast and accessibility"},
            {"name": "generate_style_guide", "description": "Generate a style guide based on brand guidelines"}
        ],
        "llm_config": {
            "model": "openai/gpt-4-turbo-preview",
            "temperature": 0.7,
            "max_tokens": 2000
        }
    },
    {
        "name": "Code Assistant",
        "description": "Helps with programming tasks",
        "agent_type": "code",
        "tools": [
            {"name": "generate_code", "description": "Generate code based on a description"},
            {"name": "explain_code", "description": "Explain what a piece of code does"},
            {"name": "debug_code", "description": "Help debug code issues"}
        ],
        "llm_config": {
            "model": "deepseek-coder-33b-instruct",
            "temperature": 0.5,
            "max_tokens": 4000
        }
    },
    {
        "name": "Marketing Assistant",
        "description": "Helps with marketing content creation",
        "agent_type": "marketing",
        "tools": [
            {"name": "generate_headline", "description": "Generate attention-grabbing headlines"},
            {"name": "write_blog_post", "description": "Write a blog post on a given topic"},
            {"name": "create_social_media_post", "description": "Create engaging social media posts"}
        ],
        "llm_config": {
            "model": "anthropic/claude-3-opus",
            "temperature": 0.8,
            "max_tokens": 2000
        }
    }
]

async def seed_agents():
    """Seed the database with test agents."""
    print("Seeding database with test agents...")
    
    try:
        # Initialize the database
        await init_db()
        repo = get_repository()
        
        # Create each agent
        for agent_data in SAMPLE_AGENTS:
            # Convert to Pydantic model
            agent_create = AgentCreate(
                name=agent_data["name"],
                description=agent_data["description"],
                agent_type=agent_data["agent_type"],
                tools=[ToolConfig(**tool) for tool in agent_data["tools"]],
                llm_config=LLMConfig(**agent_data["llm_config"])
            )
            
            # Create the agent
            agent_node = AgentNode(
                name=agent_create.name,
                description=agent_create.description,
                config={
                    "agent_type": agent_create.agent_type,
                    "is_active": True,
                    "tags": [],
                    "metadata": {}
                },
                tools=[tool.dict() for tool in agent_create.tools],
                llm_config=agent_create.llm_config.dict()
            )
            
            # Save to database
            created_agent = await repo.create_node(agent_node)
            print(f"✅ Created agent: {created_agent.name} (ID: {created_agent.id})")
        
        print("\n✅ Database seeded successfully")
        
    except Exception as e:
        print(f"❌ Error seeding database: {e}")
        raise
    finally:
        await close_db()

if __name__ == "__main__":
    asyncio.run(seed_agents())
