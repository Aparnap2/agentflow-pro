"""Document processing for RAG pipeline."""
import re
import logging
from typing import List, Dict, Any, Optional, Union
from enum import Enum
from pathlib import Path
from dataclasses import dataclass

import PyPDF2
from bs4 import BeautifulSoup
import markdown

from .vector_store import DocumentChunk, DocumentType

logger = logging.getLogger(__name__)

class ChunkingStrategy(str, Enum):
    """Strategies for splitting documents into chunks."""
    SIMPLE = "simple"
    SENTENCE = "sentence"
    PARAGRAPH = "paragraph"

@dataclass
class Document:
    """A document with content and metadata."""
    text: str
    metadata: Dict[str, Any] = None
    document_type: DocumentType = DocumentType.TEXT

class DocumentProcessor:
    """Process documents for RAG applications."""
    
    def __init__(
        self,
        chunk_size: int = 1000,
        chunk_overlap: int = 200,
        chunking_strategy: ChunkingStrategy = ChunkingStrategy.SIMPLE
    ):
        """Initialize the document processor."""
        self.chunk_size = chunk_size
        self.chunk_overlap = chunk_overlap
        self.chunking_strategy = chunking_strategy
    
    async def process_document(
        self,
        content: Union[str, bytes],
        document_type: Optional[DocumentType] = None,
        metadata: Optional[Dict[str, Any]] = None,
        **kwargs
    ) -> List[DocumentChunk]:
        """Process a document into chunks."""
        if metadata is None:
            metadata = {}
        
        # Detect document type if not provided
        if document_type is None:
            document_type = self._detect_document_type(content, metadata)
        
        # Extract text based on document type
        text = await self._extract_text(content, document_type, **kwargs)
        
        # Clean the text
        text = self._clean_text(text)
        
        # Split into chunks
        chunks = self._chunk_text(text, document_type)
        
        # Create document chunks
        document_chunks = []
        for i, chunk_text in enumerate(chunks):
            chunk_metadata = metadata.copy()
            chunk_metadata.update({
                "chunk_index": i,
                "chunk_size": len(chunk_text),
                "document_type": document_type.value,
            })
            
            document_chunks.append(DocumentChunk(
                text=chunk_text,
                metadata=chunk_metadata,
                document_id=metadata.get("document_id", str(id(content))),
                chunk_index=i,
                chunk_size=len(chunk_text),
                document_type=document_type
            ))
        
        return document_chunks
    
    def _detect_document_type(
        self,
        content: Union[str, bytes],
        metadata: Dict[str, Any]
    ) -> DocumentType:
        """Detect the document type from content or metadata."""
        if "document_type" in metadata:
            try:
                return DocumentType(metadata["document_type"])
            except ValueError:
                pass
        
        if isinstance(content, bytes):
            try:
                content = content.decode('utf-8', errors='ignore')
            except UnicodeDecodeError:
                return DocumentType.PDF
        
        if isinstance(content, str):
            if '<html' in content.lower() or '<body' in content.lower():
                return DocumentType.HTML
            if content.lstrip().startswith('# '):
                return DocumentType.MARKDOWN
        
        return DocumentType.TEXT
    
    async def _extract_text(
        self,
        content: Union[str, bytes],
        document_type: DocumentType,
        **kwargs
    ) -> str:
        """Extract text from different document types."""
        try:
            if document_type == DocumentType.PDF:
                return self._extract_pdf_text(content)
            elif document_type == DocumentType.HTML:
                return self._extract_html_text(content)
            elif document_type == DocumentType.MARKDOWN:
                return self._extract_markdown_text(content)
            else:  # TEXT
                return content if isinstance(content, str) else content.decode('utf-8', errors='replace')
        except Exception as e:
            logger.error(f"Error extracting text: {e}")
            return ""
    
    def _extract_pdf_text(self, content: Union[str, bytes]) -> str:
        """Extract text from PDF content."""
        try:
            if isinstance(content, str):
                with open(content, 'rb') as f:
                    reader = PyPDF2.PdfReader(f)
                    return "\n\n".join(page.extract_text() for page in reader.pages)
            else:  # bytes
                reader = PyPDF2.PdfReader(io.BytesIO(content))
                return "\n\n".join(page.extract_text() for page in reader.pages)
        except Exception as e:
            logger.error(f"Error extracting PDF text: {e}")
            return ""
    
    def _extract_html_text(self, content: Union[str, bytes]) -> str:
        """Extract text from HTML content."""
        try:
            if isinstance(content, bytes):
                content = content.decode('utf-8', errors='replace')
            soup = BeautifulSoup(content, 'html.parser')
            for script in soup(["script", "style"]):
                script.decompose()
            return soup.get_text(separator="\n", strip=True)
        except Exception as e:
            logger.error(f"Error extracting HTML text: {e}")
            return ""
    
    def _extract_markdown_text(self, content: Union[str, bytes]) -> str:
        """Extract text from Markdown content."""
        try:
            if isinstance(content, bytes):
                content = content.decode('utf-8', errors='replace')
            html = markdown.markdown(content)
            soup = BeautifulSoup(html, 'html.parser')
            return soup.get_text(separator="\n", strip=True)
        except Exception as e:
            logger.error(f"Error extracting Markdown text: {e}")
            return ""
    
    def _clean_text(self, text: str) -> str:
        """Clean and normalize text."""
        if not text:
            return ""
        text = re.sub(r'\s+', ' ', text)
        text = re.sub(r'[\x00-\x1f\x7f-\x9f]', ' ', text)
        return text.strip()
    
    def _chunk_text(
        self,
        text: str,
        document_type: DocumentType,
    ) -> List[str]:
        """Split text into chunks."""
        if not text:
            return []
            
        if self.chunking_strategy == ChunkingStrategy.SENTENCE:
            return self._chunk_by_sentences(text)
        elif self.chunking_strategy == ChunkingStrategy.PARAGRAPH:
            return self._chunk_by_paragraphs(text)
        else:  # SIMPLE
            return self._chunk_simple(text)
    
    def _chunk_simple(self, text: str) -> List[str]:
        """Simple character-based chunking."""
        chunks = []
        start = 0
        
        while start < len(text):
            end = min(start + self.chunk_size, len(text))
            
            if end < len(text):
                # Try to find a good breaking point
                last_space = text.rfind(' ', start, end + 1)
                if last_space > start and last_space - start > self.chunk_size // 2:
                    end = last_space
            
            chunk = text[start:end].strip()
            if chunk:
                chunks.append(chunk)
            
            start = end - self.chunk_overlap if end - self.chunk_overlap > start else end
            
            if start >= len(text) or start == end:
                break
        
        return chunks
    
    def _chunk_by_sentences(self, text: str) -> List[str]:
        """Chunk text by sentences."""
        try:
            import nltk
            try:
                nltk.data.find('tokenizers/punkt')
            except LookupError:
                nltk.download('punkt')
            
            from nltk.tokenize import sent_tokenize
            
            sentences = sent_tokenize(text)
            chunks = []
            current_chunk = []
            current_length = 0
            
            for sentence in sentences:
                sentence = sentence.strip()
                if not sentence:
                    continue
                
                sentence_length = len(sentence)
                
                if current_chunk and current_length + sentence_length > self.chunk_size:
                    chunks.append(" ".join(current_chunk).strip())
                    current_chunk = []
                    current_length = 0
                
                current_chunk.append(sentence)
                current_length += sentence_length + 1
            
            if current_chunk:
                chunks.append(" ".join(current_chunk).strip())
            
            return chunks
            
        except ImportError:
            logger.warning("nltk not available, falling back to simple chunking")
            return self._chunk_simple(text)
    
    def _chunk_by_paragraphs(self, text: str) -> List[str]:
        """Chunk text by paragraphs."""
        paragraphs = text.split('\n\n')
        chunks = []
        current_chunk = []
        current_length = 0
        
        for paragraph in paragraphs:
            paragraph = paragraph.strip()
            if not paragraph:
                continue
                
            paragraph_length = len(paragraph)
            
            if current_chunk and current_length + paragraph_length > self.chunk_size:
                chunks.append("\n\n".join(current_chunk).strip())
                current_chunk = []
                current_length = 0
            
            current_chunk.append(paragraph)
            current_length += paragraph_length + 2  # +2 for the newlines
        
        if current_chunk:
            chunks.append("\n\n".join(current_chunk).strip())
        
        return chunks

# Global instance for easy import
document_processor = DocumentProcessor()
