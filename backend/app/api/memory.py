from fastapi import APIRouter
from app.models.memory import VectorUpsertRequest, VectorSearchRequest, NodeCreateRequest, EdgeCreateRequest, CypherQueryRequest
from app.services.qdrant_client import QdrantClient
from app.services.neo4j_client import Neo4jClient

router = APIRouter(prefix="/memory", tags=["memory"])

qdrant = QdrantClient()
neo4j = Neo4jClient()

@router.post("/vector/upsert")
def upsert_vectors(req: VectorUpsertRequest):
    qdrant.upsert_vectors(req.collection, req.vectors)
    return {"status": "upserted"}

@router.post("/vector/search")
def search_vectors(req: VectorSearchRequest):
    results = qdrant.search_vectors(req.collection, req.query_vector, req.top_k)
    return {"results": results}

@router.post("/graph/node")
def create_node(req: NodeCreateRequest):
    neo4j.create_node(req.label, req.properties)
    return {"status": "node created"}

@router.post("/graph/edge")
def create_edge(req: EdgeCreateRequest):
    neo4j.create_edge(req.from_node_id, req.to_node_id, req.rel_type, req.properties)
    return {"status": "edge created"}

@router.post("/graph/query")
def run_cypher(req: CypherQueryRequest):
    results = neo4j.query(req.cypher)
    return {"results": results} 