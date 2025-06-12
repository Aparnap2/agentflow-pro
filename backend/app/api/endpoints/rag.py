"""
RAG API endpoints for document management and semantic search.
"""

from fastapi import APIRouter, Depends, HTTPException, UploadFile, File, Form
from fastapi.responses import JSONResponse
from typing import List, Optional, Dict, Any
import json
import uuid

from app.core.security import get_current_active_user
from app.models.user import User
from app.ai.rag.knowledge_base import RAGKnowledgeBase, DocumentType
from app.ai.rag.vector_store import DocumentChunk

router = APIRouter()

@router.post("/documents", response_model=Dict[str, str])
async def upload_document(
    file: UploadFile = File(...),
    document_type: Optional[DocumentType] = Form(DocumentType.TEXT),
    metadata: str = Form("{}"),
    current_user: User = Depends(get_current_active_user)
):
    """
    Upload a document to the knowledge base.
    
    The document will be processed, chunked, and stored in the vector store.
    """
    try:
        # Parse metadata
        try:
            metadata_dict = json.loads(metadata)
            if not isinstance(metadata_dict, dict):
                metadata_dict = {}
        except json.JSONDecodeError:
            metadata_dict = {}
        
        # Add user and source info to metadata
        metadata_dict.update({
            "uploaded_by": current_user.email,
            "filename": file.filename,
            "content_type": file.content_type,
        })
        
        # Read file content
        content = await file.read()
        
        # Add to knowledge base
        document_id = await RAGKnowledgeBase().add_document(
            content=content,
            document_type=document_type,
            metadata=metadata_dict
        )
        
        return {"document_id": document_id, "message": "Document uploaded successfully"}
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to upload document: {str(e)}")

@router.get("/documents/search", response_model=List[DocumentChunk])
async def search_documents(
    query: str,
    limit: int = 10,
    min_score: float = 0.5,
    current_user: User = Depends(get_current_active_user)
):
    """
    Search documents using semantic search.
    
    Returns matching document chunks with relevance scores.
    """
    try:
        results = await RAGKnowledgeBase().search(
            query=query,
            limit=limit,
            min_score=min_score
        )
        return results
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Search failed: {str(e)}")

@router.get("/documents/{document_id}/chunks", response_model=List[DocumentChunk])
async def get_document_chunks(
    document_id: str,
    limit: int = 100,
    offset: int = 0,
    current_user: User = Depends(get_current_active_user)
):
    """
    Retrieve all chunks for a specific document.
    """
    try:
        return await RAGKnowledgeBase().get_document_chunks(
            document_id=document_id,
            limit=limit,
            offset=offset
        )
    except Exception as e:
        raise HTTPException(status_code=404, detail=f"Document not found: {str(e)}")

@router.delete("/documents/{document_id}", response_model=Dict[str, str])
async def delete_document(
    document_id: str,
    current_user: User = Depends(get_current_active_user)
):
    """
    Delete a document and all its chunks from the knowledge base.
    """
    try:
        success = await RAGKnowledgeBase().delete_document(document_id)
        if not success:
            raise HTTPException(status_code=404, detail="Document not found")
        return {"message": f"Document {document_id} deleted successfully"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to delete document: {str(e)}")

@router.get("/info", response_model=Dict[str, Any])
async def get_knowledge_base_info(
    current_user: User = Depends(get_current_active_user)
):
    """
    Get information about the knowledge base.
    """
    try:
        return await RAGKnowledgeBase().get_collection_info()
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get knowledge base info: {str(e)}")
