from typing import Any, List, Dict, Optional
import logging
from neo4j import GraphDatabase, Driver, Session
from neo4j.exceptions import ServiceUnavailable, AuthError

logger = logging.getLogger(__name__)

class Neo4jClient:
    def __init__(self, uri: str = 'bolt://localhost:7687', user: str = 'neo4j', password: str = 'password'):
        self.uri = uri
        self.user = user
        self.password = password
        self.driver: Optional[Driver] = None
        self._connected = False

    async def connect(self):
        """Connect to Neo4j database"""
        try:
            self.driver = GraphDatabase.driver(
                self.uri, 
                auth=(self.user, self.password)
            )
            
            # Test connection
            with self.driver.session() as session:
                result = session.run("RETURN 1 as test")
                result.single()
            
            self._connected = True
            logger.info(f"Connected to Neo4j at {self.uri}")
            return True
        except (ServiceUnavailable, AuthError) as e:
            logger.error(f"Failed to connect to Neo4j: {e}")
            self._connected = False
            return False

    async def run_query(self, query: str, parameters: Dict[str, Any] = None) -> List[Dict[str, Any]]:
        """Run Cypher query and return results"""
        if not self._connected:
            await self.connect()
        
        if not self.driver:
            logger.error("No Neo4j driver available")
            return []
        
        try:
            with self.driver.session() as session:
                result = session.run(query, parameters or {})
                return [record.data() for record in result]
        except Exception as e:
            logger.error(f"Failed to run query: {e}")
            return []

    async def create_agent_node(self, agent_id: str, agent_data: Dict[str, Any]):
        """Create an agent node in the graph"""
        query = """
        MERGE (a:Agent {id: $agent_id})
        SET a += $agent_data
        RETURN a
        """
        return await self.run_query(query, {
            'agent_id': agent_id,
            'agent_data': agent_data
        })

    async def create_task_node(self, task_id: str, task_data: Dict[str, Any]):
        """Create a task node in the graph"""
        query = """
        MERGE (t:Task {id: $task_id})
        SET t += $task_data
        RETURN t
        """
        return await self.run_query(query, {
            'task_id': task_id,
            'task_data': task_data
        })

    async def create_relationship(self, from_id: str, to_id: str, relationship_type: str, properties: Dict[str, Any] = None):
        """Create a relationship between two nodes"""
        query = f"""
        MATCH (a {{id: $from_id}})
        MATCH (b {{id: $to_id}})
        MERGE (a)-[r:{relationship_type}]->(b)
        SET r += $properties
        RETURN r
        """
        return await self.run_query(query, {
            'from_id': from_id,
            'to_id': to_id,
            'properties': properties or {}
        })

    async def get_agent_relationships(self, agent_id: str) -> List[Dict[str, Any]]:
        """Get all relationships for an agent"""
        query = """
        MATCH (a:Agent {id: $agent_id})-[r]-(n)
        RETURN type(r) as relationship_type, 
               properties(r) as relationship_props,
               labels(n) as node_labels,
               properties(n) as node_props
        """
        return await self.run_query(query, {'agent_id': agent_id})

    async def get_task_history(self, agent_id: str, limit: int = 10) -> List[Dict[str, Any]]:
        """Get task history for an agent"""
        query = """
        MATCH (a:Agent {id: $agent_id})-[:EXECUTED]->(t:Task)
        RETURN t
        ORDER BY t.created_at DESC
        LIMIT $limit
        """
        return await self.run_query(query, {
            'agent_id': agent_id,
            'limit': limit
        })

    async def store_agent_memory(self, agent_id: str, memory_type: str, content: Dict[str, Any]):
        """Store agent memory as a graph structure"""
        query = """
        MATCH (a:Agent {id: $agent_id})
        CREATE (m:Memory {
            id: randomUUID(),
            type: $memory_type,
            content: $content,
            created_at: datetime()
        })
        CREATE (a)-[:HAS_MEMORY]->(m)
        RETURN m
        """
        return await self.run_query(query, {
            'agent_id': agent_id,
            'memory_type': memory_type,
            'content': content
        })

    async def get_agent_memory(self, agent_id: str, memory_type: Optional[str] = None) -> List[Dict[str, Any]]:
        """Retrieve agent memory"""
        if memory_type:
            query = """
            MATCH (a:Agent {id: $agent_id})-[:HAS_MEMORY]->(m:Memory {type: $memory_type})
            RETURN m
            ORDER BY m.created_at DESC
            """
            params = {'agent_id': agent_id, 'memory_type': memory_type}
        else:
            query = """
            MATCH (a:Agent {id: $agent_id})-[:HAS_MEMORY]->(m:Memory)
            RETURN m
            ORDER BY m.created_at DESC
            """
            params = {'agent_id': agent_id}
        
        return await self.run_query(query, params)

    async def create_workflow_graph(self, workflow_id: str, workflow_data: Dict[str, Any]):
        """Create a workflow graph structure"""
        query = """
        MERGE (w:Workflow {id: $workflow_id})
        SET w += $workflow_data
        RETURN w
        """
        return await self.run_query(query, {
            'workflow_id': workflow_id,
            'workflow_data': workflow_data
        })

    async def link_agent_to_workflow(self, agent_id: str, workflow_id: str, role: str):
        """Link an agent to a workflow with a specific role"""
        query = """
        MATCH (a:Agent {id: $agent_id})
        MATCH (w:Workflow {id: $workflow_id})
        MERGE (a)-[r:PARTICIPATES_IN {role: $role}]->(w)
        RETURN r
        """
        return await self.run_query(query, {
            'agent_id': agent_id,
            'workflow_id': workflow_id,
            'role': role
        })

    async def get_workflow_participants(self, workflow_id: str) -> List[Dict[str, Any]]:
        """Get all agents participating in a workflow"""
        query = """
        MATCH (a:Agent)-[r:PARTICIPATES_IN]->(w:Workflow {id: $workflow_id})
        RETURN a, r.role as role
        """
        return await self.run_query(query, {'workflow_id': workflow_id})

    def close(self):
        """Close the Neo4j connection"""
        if self.driver:
            self.driver.close()
            self._connected = False
            logger.info("Neo4j connection closed")

    # Legacy methods for backward compatibility
    def create_node(self, label: str, properties: Dict[str, Any]):
        """Legacy method - use create_agent_node or create_task_node instead"""
        pass

    def create_edge(self, from_node_id: int, to_node_id: int, rel_type: str, properties: Dict[str, Any] = None):
        """Legacy method - use create_relationship instead"""
        pass

    def query(self, cypher: str):
        """Legacy method - use run_query instead"""
        return []