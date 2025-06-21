from typing import Any, Dict, List, Optional, Callable
import logging
import uuid
from datetime import datetime
from langgraph.graph import StateGraph, END
from langgraph.checkpoint.memory import MemorySaver
from langchain_core.messages import BaseMessage, HumanMessage, AIMessage
from pydantic import BaseModel

from ..models.workflow import AgentState, OrchestrationState
from ..services.qdrant_client import QdrantClient
from ..services.neo4j_client import Neo4jClient

logger = logging.getLogger(__name__)

class WorkflowConfig(BaseModel):
    """Configuration for a workflow"""
    name: str
    description: str
    agents: List[str]
    entry_point: str
    human_in_loop_points: List[str] = []
    max_iterations: int = 50

class LangGraphOrchestrator:
    def __init__(self, qdrant_client: Optional[QdrantClient] = None, neo4j_client: Optional[Neo4jClient] = None):
        self.qdrant_client = qdrant_client
        self.neo4j_client = neo4j_client
        self.workflows: Dict[str, StateGraph] = {}
        self.workflow_configs: Dict[str, WorkflowConfig] = {}
        self.active_workflows: Dict[str, Dict[str, Any]] = {}
        self.checkpointer = MemorySaver()
        
    async def define_workflow(self, workflow_config: Dict[str, Any]) -> str:
        """Define a new workflow using LangGraph"""
        try:
            config = WorkflowConfig(**workflow_config)
            workflow_id = str(uuid.uuid4())
            
            # Create the state graph
            workflow = StateGraph(OrchestrationState)
            
            # Add nodes for each agent
            for agent_id in config.agents:
                workflow.add_node(agent_id, self._create_agent_node(agent_id))
            
            # Add conditional edges based on workflow logic
            workflow.add_conditional_edges(
                config.entry_point,
                self._route_to_next_agent,
                {agent_id: agent_id for agent_id in config.agents}
            )
            
            # Add human-in-the-loop checkpoints
            for hil_point in config.human_in_loop_points:
                workflow.add_node(f"{hil_point}_hil", self._human_in_loop_node)
                workflow.add_edge(hil_point, f"{hil_point}_hil")
            
            # Set entry point
            workflow.set_entry_point(config.entry_point)
            
            # Compile the workflow
            compiled_workflow = workflow.compile(checkpointer=self.checkpointer)
            
            # Store the workflow
            self.workflows[workflow_id] = compiled_workflow
            self.workflow_configs[workflow_id] = config
            
            # Store in Neo4j if available
            if self.neo4j_client:
                await self.neo4j_client.create_workflow_graph(workflow_id, {
                    'name': config.name,
                    'description': config.description,
                    'created_at': datetime.now().isoformat(),
                    'status': 'defined'
                })
                
                # Link agents to workflow
                for agent_id in config.agents:
                    await self.neo4j_client.link_agent_to_workflow(
                        agent_id, workflow_id, 'participant'
                    )
            
            logger.info(f"Workflow {config.name} defined with ID: {workflow_id}")
            return workflow_id
            
        except Exception as e:
            logger.error(f"Failed to define workflow: {e}")
            raise

    async def run_workflow(self, workflow_id: str, input_data: Dict[str, Any], config: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """Run a workflow with given input data"""
        if workflow_id not in self.workflows:
            raise ValueError(f"Workflow {workflow_id} not found")
        
        try:
            workflow = self.workflows[workflow_id]
            thread_id = str(uuid.uuid4())
            
            # Prepare initial state
            initial_state = OrchestrationState(
                user_request=input_data.get('user_request', ''),
                task_breakdown=[],
                assigned_agents=[],
                results={},
                coordination_messages=[HumanMessage(content=input_data.get('user_request', ''))],
                final_output=None
            )
            
            # Store workflow execution info
            self.active_workflows[thread_id] = {
                'workflow_id': workflow_id,
                'status': 'running',
                'started_at': datetime.now().isoformat(),
                'input_data': input_data,
                'thread_id': thread_id
            }
            
            # Run the workflow
            config_dict = {"configurable": {"thread_id": thread_id}}
            if config:
                config_dict.update(config)
            
            result = await workflow.ainvoke(initial_state.dict(), config=config_dict)
            
            # Update workflow status
            self.active_workflows[thread_id]['status'] = 'completed'
            self.active_workflows[thread_id]['completed_at'] = datetime.now().isoformat()
            self.active_workflows[thread_id]['result'] = result
            
            # Store results in memory systems
            if self.qdrant_client:
                await self._store_workflow_result_in_qdrant(workflow_id, thread_id, result)
            
            if self.neo4j_client:
                await self._store_workflow_result_in_neo4j(workflow_id, thread_id, result)
            
            logger.info(f"Workflow {workflow_id} completed successfully")
            return {
                'status': 'completed',
                'workflow_id': workflow_id,
                'thread_id': thread_id,
                'result': result
            }
            
        except Exception as e:
            logger.error(f"Failed to run workflow {workflow_id}: {e}")
            if thread_id in self.active_workflows:
                self.active_workflows[thread_id]['status'] = 'failed'
                self.active_workflows[thread_id]['error'] = str(e)
            raise

    async def get_workflow_state(self, workflow_id: str, thread_id: Optional[str] = None) -> Dict[str, Any]:
        """Get current state of a workflow"""
        if workflow_id not in self.workflows:
            return {'error': f'Workflow {workflow_id} not found'}
        
        try:
            if thread_id and thread_id in self.active_workflows:
                return self.active_workflows[thread_id]
            
            # Return general workflow info
            config = self.workflow_configs.get(workflow_id)
            return {
                'workflow_id': workflow_id,
                'name': config.name if config else 'Unknown',
                'status': 'defined',
                'agents': config.agents if config else [],
                'active_executions': [
                    exec_info for exec_info in self.active_workflows.values()
                    if exec_info['workflow_id'] == workflow_id
                ]
            }
            
        except Exception as e:
            logger.error(f"Failed to get workflow state: {e}")
            return {'error': str(e)}

    async def pause_workflow(self, thread_id: str) -> Dict[str, Any]:
        """Pause a running workflow"""
        if thread_id not in self.active_workflows:
            return {'error': f'Workflow thread {thread_id} not found'}
        
        try:
            self.active_workflows[thread_id]['status'] = 'paused'
            self.active_workflows[thread_id]['paused_at'] = datetime.now().isoformat()
            
            logger.info(f"Workflow thread {thread_id} paused")
            return {'status': 'paused', 'thread_id': thread_id}
            
        except Exception as e:
            logger.error(f"Failed to pause workflow: {e}")
            return {'error': str(e)}

    async def resume_workflow(self, thread_id: str, human_input: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """Resume a paused workflow"""
        if thread_id not in self.active_workflows:
            return {'error': f'Workflow thread {thread_id} not found'}
        
        try:
            workflow_info = self.active_workflows[thread_id]
            workflow_id = workflow_info['workflow_id']
            workflow = self.workflows[workflow_id]
            
            # Update status
            self.active_workflows[thread_id]['status'] = 'running'
            self.active_workflows[thread_id]['resumed_at'] = datetime.now().isoformat()
            
            if human_input:
                self.active_workflows[thread_id]['human_input'] = human_input
            
            logger.info(f"Workflow thread {thread_id} resumed")
            return {'status': 'resumed', 'thread_id': thread_id}
            
        except Exception as e:
            logger.error(f"Failed to resume workflow: {e}")
            return {'error': str(e)}

    def _create_agent_node(self, agent_id: str) -> Callable:
        """Create a node function for an agent"""
        async def agent_node(state: OrchestrationState) -> OrchestrationState:
            try:
                # This would integrate with your actual agent implementation
                # For now, we'll simulate agent execution
                logger.info(f"Executing agent: {agent_id}")
                
                # Add agent to assigned agents if not already there
                if agent_id not in state.assigned_agents:
                    state.assigned_agents.append(agent_id)
                
                # Simulate agent work
                result = {
                    'agent_id': agent_id,
                    'status': 'completed',
                    'output': f'Result from {agent_id}',
                    'timestamp': datetime.now().isoformat()
                }
                
                state.results[agent_id] = result
                state.coordination_messages.append(
                    AIMessage(content=f"Agent {agent_id} completed task")
                )
                
                return state
                
            except Exception as e:
                logger.error(f"Error in agent node {agent_id}: {e}")
                state.results[agent_id] = {
                    'agent_id': agent_id,
                    'status': 'failed',
                    'error': str(e),
                    'timestamp': datetime.now().isoformat()
                }
                return state
        
        return agent_node

    def _route_to_next_agent(self, state: OrchestrationState) -> str:
        """Determine the next agent to execute"""
        # Simple routing logic - can be made more sophisticated
        config = self.workflow_configs.get(state.user_request, {})
        agents = getattr(config, 'agents', [])
        
        for agent_id in agents:
            if agent_id not in state.assigned_agents:
                return agent_id
        
        return END

    async def _human_in_loop_node(self, state: OrchestrationState) -> OrchestrationState:
        """Handle human-in-the-loop checkpoint"""
        logger.info("Human-in-the-loop checkpoint reached")
        # This would pause execution and wait for human input
        # Implementation depends on your HIL service
        return state

    async def _store_workflow_result_in_qdrant(self, workflow_id: str, thread_id: str, result: Dict[str, Any]):
        """Store workflow results in Qdrant for semantic search"""
        try:
            # Create embeddings for the workflow result
            # This would use your embedding service
            collection_name = f"workflow_results"
            
            vector_data = {
                'id': thread_id,
                'vector': [0.0] * 1536,  # Placeholder - use actual embeddings
                'payload': {
                    'workflow_id': workflow_id,
                    'thread_id': thread_id,
                    'result': result,
                    'timestamp': datetime.now().isoformat()
                }
            }
            
            await self.qdrant_client.create_collection(collection_name)
            await self.qdrant_client.upsert_vectors(collection_name, [vector_data])
            
        except Exception as e:
            logger.error(f"Failed to store workflow result in Qdrant: {e}")

    async def _store_workflow_result_in_neo4j(self, workflow_id: str, thread_id: str, result: Dict[str, Any]):
        """Store workflow results in Neo4j for graph relationships"""
        try:
            # Create execution node
            execution_data = {
                'thread_id': thread_id,
                'status': 'completed',
                'result': result,
                'completed_at': datetime.now().isoformat()
            }
            
            query = """
            MATCH (w:Workflow {id: $workflow_id})
            CREATE (e:Execution {
                id: $thread_id,
                status: $status,
                completed_at: $completed_at
            })
            CREATE (w)-[:HAS_EXECUTION]->(e)
            RETURN e
            """
            
            await self.neo4j_client.run_query(query, {
                'workflow_id': workflow_id,
                'thread_id': thread_id,
                'status': 'completed',
                'completed_at': datetime.now().isoformat()
            })
            
        except Exception as e:
            logger.error(f"Failed to store workflow result in Neo4j: {e}")

    async def list_workflows(self) -> List[Dict[str, Any]]:
        """List all defined workflows"""
        workflows = []
        for workflow_id, config in self.workflow_configs.items():
            workflows.append({
                'id': workflow_id,
                'name': config.name,
                'description': config.description,
                'agents': config.agents,
                'status': 'defined'
            })
        return workflows

    async def delete_workflow(self, workflow_id: str) -> bool:
        """Delete a workflow"""
        try:
            if workflow_id in self.workflows:
                del self.workflows[workflow_id]
            if workflow_id in self.workflow_configs:
                del self.workflow_configs[workflow_id]
            
            # Remove from Neo4j if available
            if self.neo4j_client:
                query = "MATCH (w:Workflow {id: $workflow_id}) DETACH DELETE w"
                await self.neo4j_client.run_query(query, {'workflow_id': workflow_id})
            
            logger.info(f"Workflow {workflow_id} deleted")
            return True
            
        except Exception as e:
            logger.error(f"Failed to delete workflow {workflow_id}: {e}")
            return False