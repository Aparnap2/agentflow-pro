"""Graphiti repository for Neo4j operations."""
from typing import Dict, List, Optional, Type, TypeVar, Any, Union
from datetime import datetime
import logging
from neo4j import Transaction, Record
from neo4j.exceptions import Neo4jError

from ..core.config import settings
from .models import (
    Node, NodeType, Relationship, RelationshipType,
    AgentNode, CrewNode, WorkflowNode, TaskNode, MessageNode
)

logger = logging.getLogger(__name__)
T = TypeVar('T', bound=Node)

class GraphitiRepository:
    """Repository for graph operations using Neo4j."""
    
    def __init__(self, driver=None):
        """Initialize with a Neo4j driver."""
        self.driver = driver or get_neo4j_driver()
    
    async def create_node(self, node: Node) -> Node:
        """Create a new node in the graph."""
        query = """
        CREATE (n:Node $node_props)
        SET n:${labels}
        RETURN n
        """
        
        params = {
            "node_props": node.to_dict(),
            "labels": ":".join(node.labels)
        }
        
        with self.driver.session() as session:
            try:
                result = session.run(query, **params)
                record = result.single()
                if not record:
                    raise ValueError("Failed to create node")
                return self._node_from_record(record["n"], type(node))
            except Neo4jError as e:
                logger.error(f"Failed to create node: {e}")
                raise
    
    async def get_node(self, node_id: str, node_type: Type[T]) -> Optional[T]:
        """Get a node by ID and type."""
        query = """
        MATCH (n:Node {id: $node_id})
        WHERE $type IN labels(n)
        RETURN n
        """
        
        with self.driver.session() as session:
            try:
                result = session.run(
                    query, 
                    node_id=node_id,
                    type=node_type.__fields__["type"].default.value
                )
                record = result.single()
                if not record:
                    return None
                return self._node_from_record(record["n"], node_type)
            except Neo4jError as e:
                logger.error(f"Failed to get node {node_id}: {e}")
                raise
    
    async def update_node(self, node: Node) -> Node:
        """Update an existing node."""
        query = """
        MATCH (n:Node {id: $node_id})
        SET n += $props,
            n.updated_at = datetime().epochMillis
        RETURN n
        """
        
        # Convert node to dict and remove ID and type
        props = node.to_dict()
        node_id = props.pop("id")
        props.pop("type", None)
        
        with self.driver.session() as session:
            try:
                result = session.run(query, node_id=node_id, props=props)
                record = result.single()
                if not record:
                    raise ValueError(f"Node {node_id} not found")
                return self._node_from_record(record["n"], type(node))
            except Neo4jError as e:
                logger.error(f"Failed to update node {node_id}: {e}")
                raise
    
    async def delete_node(self, node_id: str, node_type: Type[T]) -> bool:
        """Delete a node by ID and type."""
        query = """
        MATCH (n:Node {id: $node_id})
        WHERE $type IN labels(n)
        DETACH DELETE n
        RETURN count(n) > 0 as deleted
        """
        
        with self.driver.session() as session:
            try:
                result = session.run(
                    query,
                    node_id=node_id,
                    type=node_type.__fields__["type"].default.value
                )
                record = result.single()
                return record["deleted"] if record else False
            except Neo4jError as e:
                logger.error(f"Failed to delete node {node_id}: {e}")
                return False
    
    async def create_relationship(
        self, 
        source_id: str, 
        target_id: str, 
        rel_type: RelationshipType,
        properties: Optional[Dict[str, Any]] = None
    ) -> Relationship:
        """Create a relationship between two nodes."""
        query = """
        MATCH (source:Node {id: $source_id}), (target:Node {id: $target_id})
        MERGE (source)-[r:${rel_type}]->(target)
        SET r += $properties
        RETURN source, r, target
        """
        
        params = {
            "source_id": source_id,
            "target_id": target_id,
            "rel_type": rel_type.value,
            "properties": properties or {}
        }
        
        with self.driver.session() as session:
            try:
                result = session.run(query, **params)
                record = result.single()
                if not record:
                    raise ValueError("Failed to create relationship")
                
                return Relationship(
                    source_id=source_id,
                    target_id=target_id,
                    type=rel_type,
                    properties=dict(record["r"])
                )
            except Neo4jError as e:
                logger.error(f"Failed to create relationship: {e}")
                raise
    
    async def find_nodes(
        self,
        node_type: Type[T],
        filters: Optional[Dict[str, Any]] = None,
        limit: int = 100,
        skip: int = 0
    ) -> List[T]:
        """Find nodes of a specific type with optional filters."""
        filters = filters or {}
        where_clause = " AND ".join([f"n.{k} = ${k}" for k in filters.keys()])
        where_clause = f"WHERE {where_clause}" if where_clause else ""
        
        query = f"""
        MATCH (n:Node)
        WHERE $type IN labels(n)
        {where_clause}
        RETURN n
        ORDER BY n.created_at DESC
        SKIP $skip
        LIMIT $limit
        """
        
        params = {
            "type": node_type.__fields__["type"].default.value,
            "skip": skip,
            "limit": limit,
            **filters
        }
        
        with self.driver.session() as session:
            try:
                result = session.run(query, **params)
                return [self._node_from_record(record["n"], node_type) for record in result]
            except Neo4jError as e:
                logger.error(f"Failed to find nodes: {e}")
                raise
    
    def _node_from_record(self, record: Record, node_type: Type[T]) -> T:
        """Convert a Neo4j record to a Node instance."""
        node_data = dict(record)
        return node_type.from_dict(node_data)

# Singleton instance
_repo = None

def get_repository() -> GraphitiRepository:
    """Get a singleton instance of the repository."""
    global _repo
    if _repo is None:
        _repo = GraphitiRepository()
    return _repo
