"""Neo4j database configuration."""
from typing import Optional
from neo4j import GraphDatabase, Driver
from neo4j.exceptions import ServiceUnavailable
import os
from loguru import logger

class Neo4jConfig:
    def __init__(self):
        self.uri = os.getenv("NEO4J_URI", "bolt://localhost:7687")
        self.user = os.getenv("NEO4J_USER", "neo4j")
        self.password = os.getenv("NEO4J_PASSWORD", "password")
        self.database = os.getenv("NEO4J_DATABASE", "agentflow")
        self.encrypted = os.getenv("NEO4J_ENCRYPTED", "false").lower() == "true"

# Global driver instance
_driver: Optional[Driver] = None

def get_neo4j_driver() -> Driver:
    """Get or create a Neo4j driver instance."""
    global _driver
    if _driver is None:
        config = Neo4jConfig()
        _driver = GraphDatabase.driver(
            config.uri,
            auth=(config.user, config.password),
            encrypted=config.encrypted
        )
        # Test the connection
        try:
            with _driver.session() as session:
                session.run("RETURN 1")
            logger.info("Successfully connected to Neo4j")
        except ServiceUnavailable as e:
            logger.error(f"Failed to connect to Neo4j: {e}")
            raise
    return _driver

async def init_db():
    """Initialize the database with constraints and indexes."""
    driver = get_neo4j_driver()
    constraints = [
        "CREATE CONSTRAINT node_id IF NOT EXISTS FOR (n:Node) REQUIRE n.id IS UNIQUE",
        "CREATE INDEX node_labels IF NOT EXISTS FOR (n:Node) ON (labels(n))",
        "CREATE INDEX node_type IF NOT EXISTS FOR (n:Node) ON (n.type)",
        "CREATE INDEX node_created_at IF NOT EXISTS FOR (n:Node) ON (n.created_at)",
    ]
    
    with driver.session() as session:
        for constraint in constraints:
            session.run(constraint)

async def close_db():
    """Close the Neo4j driver connection."""
    global _driver
    if _driver is not None:
        await _driver.close()
        _driver = None
