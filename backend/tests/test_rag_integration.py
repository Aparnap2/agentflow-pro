"""
Test script for RAG integration with Qdrant.

This script tests the RAG knowledge base functionality including:
- Document ingestion
- Semantic search
- Document retrieval
- Document deletion
"""

import os
import asyncio
import uuid
import logging
from pathlib import Path
from typing import List, Dict, Any, Optional

import pytest
from pydantic import BaseModel

# Add parent directory to path to allow imports
import sys
sys.path.append(str(Path(__file__).parent.parent))

from app.ai.rag.knowledge_base import RAGKnowledgeBase, DocumentType
from app.ai.rag.vector_store import DocumentChunk

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Test data
TEST_DOCUMENTS = [
    {
        "content": """
        AgentFlow Pro is an AI agent automation platform that helps businesses
        automate their workflows using AI agents. It provides a visual interface
        to design, deploy, and monitor AI agents that can perform various tasks.
        """,
        "metadata": {
            "title": "AgentFlow Pro Overview",
            "category": "introduction",
            "source": "test"
        }
    },
    {
        "content": """
        To get started with AgentFlow Pro, you need to:
        1. Sign up for an account
        2. Create your first agent
        3. Configure the agent's workflow
        4. Deploy the agent
        5. Monitor its performance
        """,
        "metadata": {
            "title": "Getting Started Guide",
            "category": "tutorial",
            "source": "test"
        }
    },
    {
        "content": """
        Troubleshooting common issues in AgentFlow Pro:
        - If an agent is not responding, check its status in the dashboard
        - For performance issues, review the agent's resource allocation
        - Check the logs for detailed error messages
        - Ensure all required API keys are properly configured
        """,
        "metadata": {
            "title": "Troubleshooting Guide",
            "category": "troubleshooting",
            "source": "test"
        }
    }
]

@pytest.fixture(scope="module")
def test_collection_name():
    """Generate a unique test collection name."""
    return f"test_rag_{uuid.uuid4().hex[:8]}"

@pytest.fixture(scope="module")
async def rag_kb(test_collection_name):
    """Create a RAG knowledge base instance for testing."""
    # Initialize with test collection name
    kb = RAGKnowledgeBase()
    # Override collection name for testing
    kb.config.collection_name = test_collection_name
    
    # Initialize collection
    await kb._initialize_collection()
    
    yield kb
    
    # Cleanup: Delete the test collection
    try:
        await kb.vector_store.client.delete_collection(test_collection_name)
    except Exception as e:
        logger.warning(f"Failed to delete test collection: {e}")

@pytest.mark.asyncio
async def test_document_ingestion(rag_kb, test_collection_name):
    """Test document ingestion into the knowledge base."""
    # Test adding a document
    doc_id = await rag_kb.add_document(
        content=TEST_DOCUMENTS[0]["content"],
        metadata=TEST_DOCUMENTS[0]["metadata"]
    )
    
    assert doc_id is not None
    assert isinstance(doc_id, str)
    
    # Verify the document was added
    chunks = await rag_kb.get_document_chunks(doc_id)
    assert len(chunks) > 0
    
    # Cleanup
    await rag_kb.delete_document(doc_id)

@pytest.mark.asyncio
async def test_semantic_search(rag_kb, test_collection_name):
    """Test semantic search functionality."""
    # Add test documents
    doc_ids = []
    for doc in TEST_DOCUMENTS:
        doc_id = await rag_kb.add_document(
            content=doc["content"],
            metadata=doc["metadata"]
        )
        doc_ids.append(doc_id)
    
    try:
        # Test search
        results = await rag_kb.search(
            query="How do I get started with AgentFlow?",
            limit=2
        )
        
        # Verify results
        assert len(results) > 0
        assert any("getting started" in chunk.metadata.get("title", "").lower() 
                  for chunk in results)
        
        # Test with filters
        results = await rag_kb.search(
            query="troubleshoot agent issues",
            filter_conditions={"category": "troubleshooting"}
        )
        
        assert len(results) > 0
        assert all("troubleshooting" in chunk.metadata.get("category", "").lower() 
                  for chunk in results)
        
    finally:
        # Cleanup
        for doc_id in doc_ids:
            await rag_kb.delete_document(doc_id)

@pytest.mark.asyncio
async def test_document_deletion(rag_kb, test_collection_name):
    """Test document deletion from the knowledge base."""
    # Add a document
    doc_id = await rag_kb.add_document(
        content=TEST_DOCUMENTS[0]["content"],
        metadata=TEST_DOCUMENTS[0]["metadata"]
    )
    
    # Verify it was added
    chunks = await rag_kb.get_document_chunks(doc_id)
    assert len(chunks) > 0
    
    # Delete the document
    success = await rag_kb.delete_document(doc_id)
    assert success is True
    
    # Verify it was deleted
    chunks = await rag_kb.get_document_chunks(doc_id)
    assert len(chunks) == 0

@pytest.mark.asyncio
async def test_collection_info(rag_kb, test_collection_name):
    """Test getting collection information."""
    # Get collection info
    info = await rag_kb.get_collection_info()
    
    # Verify basic structure
    assert "name" in info
    assert "vector_count" in info
    assert "indexed_vector_count" in info
    assert "points_count" in info
    
    # Should be empty initially
    assert info["points_count"] == 0

if __name__ == "__main__":
    # Run tests directly with: python -m tests.test_rag_integration
    import asyncio
    
    async def run_tests():
        # Create a test collection name
        test_collection = f"test_rag_{uuid.uuid4().hex[:8]}"
        
        # Initialize KB with test collection
        kb = RAGKnowledgeBase()
        kb.config.collection_name = test_collection
        
        try:
            # Run tests
            await test_collection_info(kb, test_collection)
            print("✓ Collection info test passed")
            
            await test_document_ingestion(kb, test_collection)
            print("✓ Document ingestion test passed")
            
            await test_semantic_search(kb, test_collection)
            print("✓ Semantic search test passed")
            
            await test_document_deletion(kb, test_collection)
            print("✓ Document deletion test passed")
            
            print("\nAll tests passed!")
            
        finally:
            # Cleanup
            try:
                await kb.vector_store.client.delete_collection(test_collection)
                print(f"✓ Cleaned up test collection: {test_collection}")
            except Exception as e:
                print(f"Warning: Failed to delete test collection: {e}")
    
    asyncio.run(run_tests())
