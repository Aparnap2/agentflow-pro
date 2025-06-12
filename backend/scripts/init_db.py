#!/usr/bin/env python3
"""Initialize the Neo4j database with constraints and indexes."""
import asyncio
import os
import sys
from pathlib import Path

# Add the project root to the Python path
project_root = Path(__file__).parent.parent
sys.path.append(str(project_root))

from app.db.config import init_db, close_db
from app.db.repository import get_repository

async def main():
    """Initialize the database with constraints and indexes."""
    print("Initializing database...")
    
    try:
        # Initialize the database with constraints
        await init_db()
        print("✅ Database initialized successfully")
        
        # Test the connection
        repo = get_repository()
        with repo.driver.session() as session:
            result = session.run("RETURN 'Neo4j connection successful' AS message")
            print(f"✅ {result.single()['message']}")
            
    except Exception as e:
        print(f"❌ Error initializing database: {e}")
        sys.exit(1)
    finally:
        await close_db()

if __name__ == "__main__":
    asyncio.run(main())
