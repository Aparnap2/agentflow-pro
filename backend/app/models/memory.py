from pydantic import BaseModel
from typing import Any, Dict, List

class VectorUpsertRequest(BaseModel):
    collection: str
    vectors: List[Any]

class VectorSearchRequest(BaseModel):
    collection: str
    query_vector: Any
    top_k: int = 5

class NodeCreateRequest(BaseModel):
    label: str
    properties: Dict[str, Any]

class EdgeCreateRequest(BaseModel):
    from_node_id: int
    to_node_id: int
    rel_type: str
    properties: Dict[str, Any] = None

class CypherQueryRequest(BaseModel):
    cypher: str 