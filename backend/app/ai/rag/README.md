# RAG (Retrieval-Augmented Generation) Integration

This module provides a complete RAG (Retrieval-Augmented Generation) implementation using Qdrant as the vector store. It includes document processing, embedding generation, and semantic search capabilities.

## Components

1. **Document Processor** (`document_processor.py`)
   - Handles various document formats (PDF, HTML, Markdown, text, etc.)
   - Splits documents into chunks with configurable strategies
   - Cleans and normalizes text

2. **Embedding Service** (`embedding_service.py`)
   - Supports multiple embedding providers (OpenAI, Hugging Face, local models)
   - Handles batch processing of embeddings
   - Provides a consistent interface for different models

3. **Vector Store** (`vector_store.py`)
   - Manages Qdrant collections
   - Handles document storage, retrieval, and search
   - Supports filtering and metadata querying

4. **RAG Knowledge Base** (`knowledge_base.py`)
   - High-level API for RAG operations
   - Combines document processing, embedding, and vector storage
   - Provides semantic search capabilities

## Setup

1. Install dependencies:
   ```bash
   pip install -r requirements-rag.txt
   ```

2. Set up environment variables (in `.env` or your environment):
   ```
   # Qdrant settings
   QDRANT_URL=http://localhost:6333
   QDRANT_API_KEY=your_api_key_here
   QDRANT_COLLECTION=knowledge_base
   
   # Optional: OpenAI API key if using OpenAI embeddings
   OPENAI_API_KEY=your_openai_api_key
   ```

3. Start Qdrant (using Docker):
   ```bash
   docker run -p 6333:6333 -p 6334:6334 \
     -v $(pwd)/qdrant_storage:/qdrant/storage \
     qdrant/qdrant
   ```

## Usage

### Initialize the Knowledge Base

```python
from app.ai.rag.knowledge_base import RAGKnowledgeBase, DocumentType

# Initialize with default settings
kb = RAGKnowledgeBase()

# Or with custom configuration
from app.ai.rag.embedding_service import EmbeddingModel, EmbeddingProvider
from app.ai.rag.document_processor import ChunkingStrategy

config = {
    "collection_name": "my_knowledge_base",
    "embedding_model": EmbeddingModel.ALL_MINILM_L6_V2,
    "embedding_provider": EmbeddingProvider.LOCAL,
    "chunk_size": 1000,
    "chunk_overlap": 200,
    "chunking_strategy": ChunkingStrategy.SIMPLE,
    "search_limit": 10,
    "min_score": 0.5
}

kb = RAGKnowledgeBase(config=config)
```

### Add Documents

```python
# Add text content
doc_id = await kb.add_document(
    content="""
    This is a sample document about AgentFlow Pro.
    It demonstrates how to use the RAG knowledge base.
    """,
    metadata={
        "title": "Sample Document",
        "author": "System",
        "category": "example"
    },
    document_type=DocumentType.TEXT
)

# Add a file (e.g., PDF, HTML, etc.)
with open("document.pdf", "rb") as f:
    doc_id = await kb.add_document(
        content=f.read(),
        document_type=DocumentType.PDF,
        metadata={"source": "document.pdf"}
    )
```

### Search Documents

```python
# Basic semantic search
results = await kb.search(
    query="How do I use AgentFlow?",
    limit=5
)

# Search with filters
results = await kb.search(
    query="troubleshooting",
    filter_conditions={"category": "troubleshooting"},
    min_score=0.6
)

# Get document chunks
doc_chunks = await kb.get_document_chunks(
    document_id="your_document_id",
    limit=10,
    offset=0
)
```

### Delete Documents

```python
# Delete a document
success = await kb.delete_document("document_id")
```

## API Endpoints

The RAG module exposes the following API endpoints:

- `POST /v1/rag/documents` - Upload a document
- `GET /v1/rag/documents/search` - Search documents
- `GET /v1/rag/documents/{document_id}/chunks` - Get document chunks
- `DELETE /v1/rag/documents/{document_id}` - Delete a document
- `GET /v1/rag/info` - Get knowledge base info

## Testing

Run the test suite:

```bash
pytest tests/test_rag_integration.py -v
```

Or run tests directly:

```bash
python -m tests.test_rag_integration
```

## Configuration

### Environment Variables

| Variable | Description | Default |
|----------|-------------|---------|
| `QDRANT_URL` | Qdrant server URL | `http://localhost:6333` |
| `QDRANT_API_KEY` | Qdrant API key | `None` |
| `QDRANT_COLLECTION` | Default collection name | `knowledge_base` |
| `OPENAI_API_KEY` | OpenAI API key (if using OpenAI embeddings) | `None` |

### Embedding Models

Supported embedding models include:

- `text-embedding-3-small` (OpenAI)
- `text-embedding-3-large` (OpenAI)
- `text-embedding-ada-002` (OpenAI)
- `BAAI/bge-small-en-v1.5` (Hugging Face)
- `BAAI/bge-base-en-v1.5` (Hugging Face)
- `BAAI/bge-large-en-v1.5` (Hugging Face)
- `sentence-transformers/all-MiniLM-L6-v2` (local)
- `sentence-transformers/all-mpnet-base-v2` (local)

## Performance Considerations

- For large document collections, consider using a dedicated Qdrant instance
- Batch document processing for better performance
- Adjust chunk size and overlap based on your use case
- Monitor memory usage when processing large documents

## Troubleshooting

1. **Qdrant connection issues**:
   - Ensure Qdrant is running and accessible
   - Check the `QDRANT_URL` and `QDRANT_API_KEY` environment variables

2. **Embedding generation failures**:
   - Verify API keys for cloud providers
   - Check internet connectivity if using remote models
   - Ensure required Python packages are installed

3. **Document processing errors**:
   - Check document formats and encodings
   - Ensure required libraries are installed (e.g., PyPDF2 for PDFs)
   - Review error logs for specific issues
