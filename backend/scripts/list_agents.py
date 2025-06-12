#!/usr/bin/env python3
"""List all agents in the database."""
import asyncio
import sys
from pathlib import Path
from tabulate import tabulate

# Add the project root to the Python path
project_root = Path(__file__).parent.parent
sys.path.append(str(project_root))

from app.db.config import init_db, close_db
from app.db.repository import get_repository
from app.db.models import AgentNode

async def list_agents():
    """List all agents in the database."""
    print("Fetching agents from the database...")
    
    try:
        # Initialize the database
        await init_db()
        repo = get_repository()
        
        # Get all agents
        agents = await repo.find_nodes(AgentNode)
        
        if not agents:
            print("No agents found in the database.")
            return
        
        # Prepare data for tabulate
        table_data = []
        for agent in agents:
            table_data.append([
                agent.id[:8] + "...",
                agent.name,
                agent.properties.get("config", {}).get("agent_type", "N/A"),
                "Active" if agent.properties.get("config", {}).get("is_active", False) else "Inactive",
                len(agent.tools) if hasattr(agent, 'tools') else 0,
                agent.created_at.strftime("%Y-%m-%d %H:%M") if hasattr(agent, 'created_at') else "N/A"
            ])
        
        # Print table
        headers = ["ID", "Name", "Type", "Status", "Tools", "Created At"]
        print("\n" + tabulate(table_data, headers=headers, tablefmt="grid"))
        print(f"\nTotal agents: {len(agents)}")
        
    except Exception as e:
        print(f"❌ Error listing agents: {e}")
        raise
    finally:
        await close_db()

if __name__ == "__main__":
    asyncio.run(list_agents())
