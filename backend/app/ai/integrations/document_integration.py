"""
Document Integration Module for Sales Agent.

This module provides functionality to manage documents across various storage providers.
Currently supports Google Drive and local filesystem with a base interface for others.
"""

import os
import io
import logging
import json
import tempfile
from pathlib import Path
from typing import Dict, List, Optional, Union, Any, BinaryIO, Tuple
from datetime import datetime
from enum import Enum
from pydantic import BaseModel, Field, HttpUrl, validator

logger = logging.getLogger(__name__)

class DocumentType(str, Enum):
    """Supported document types."""
    DOCUMENT = "document"
    SPREADSHEET = "spreadsheet"
    PRESENTATION = "presentation"
    PDF = "pdf"
    IMAGE = "image"
    FOLDER = "folder"
    OTHER = "other"

class DocumentPermission(str, Enum):
    """Document permission levels."""
    VIEW = "view"
    COMMENT = "comment"
    EDIT = "edit"
    OWNER = "owner"

class DocumentMetadata(BaseModel):
    """Metadata for a document."""
    id: str
    name: str
    type: DocumentType
    mime_type: Optional[str] = None
    size: Optional[int] = None
    created_at: Optional[datetime] = None
    modified_at: Optional[datetime] = None
    web_url: Optional[HttpUrl] = None
    parent_id: Optional[str] = None
    owner: Optional[Dict[str, str]] = None
    permissions: List[DocumentPermission] = Field(default_factory=list)
    custom_properties: Dict[str, Any] = Field(default_factory=dict)

class DocumentContent(BaseModel):
    """Document content and metadata."""
    metadata: DocumentMetadata
    content: Union[bytes, str, None] = None
    download_url: Optional[HttpUrl] = None

class DocumentTemplate(BaseModel):
    """Document template definition."""
    id: str
    name: str
    description: Optional[str] = None
    type: DocumentType
    content: Optional[Union[bytes, str]] = None
    metadata: Dict[str, Any] = Field(default_factory=dict)
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)

class DocumentIntegration:
    """Base class for document integrations."""
    
    def __init__(self, **kwargs):
        """Initialize the document integration."""
        self._setup_logging()
    
    def _setup_logging(self):
        """Configure logging for the integration."""
        self.logger = logging.getLogger(f"{__name__}.{self.__class__.__name__}")
    
    async def upload_document(
        self,
        name: str,
        content: Union[bytes, str, BinaryIO],
        parent_id: Optional[str] = None,
        mime_type: Optional[str] = None,
        **kwargs
    ) -> DocumentMetadata:
        """Upload a document.
        
        Args:
            name: Name of the document
            content: Document content (bytes, string, or file-like object)
            parent_id: ID of the parent folder
            mime_type: MIME type of the document
            
        Returns:
            DocumentMetadata for the uploaded document
        """
        raise NotImplementedError("Subclasses must implement this method")
    
    async def download_document(self, document_id: str, **kwargs) -> DocumentContent:
        """Download a document by ID.
        
        Args:
            document_id: ID of the document to download
            
        Returns:
            DocumentContent containing the document data and metadata
        """
        raise NotImplementedError("Subclasses must implement this method")
    
    async def get_document_metadata(self, document_id: str, **kwargs) -> DocumentMetadata:
        """Get metadata for a document.
        
        Args:
            document_id: ID of the document
            
        Returns:
            DocumentMetadata for the document
        """
        raise NotImplementedError("Subclasses must implement this method")
    
    async def update_document(
        self,
        document_id: str,
        content: Optional[Union[bytes, str, BinaryIO]] = None,
        metadata: Optional[Dict[str, Any]] = None,
        **kwargs
    ) -> DocumentMetadata:
        """Update a document's content and/or metadata.
        
        Args:
            document_id: ID of the document to update
            content: New document content (optional)
            metadata: Updated metadata (optional)
            
        Returns:
            Updated DocumentMetadata
        """
        raise NotImplementedError("Subclasses must implement this method")
    
    async def delete_document(self, document_id: str, **kwargs) -> bool:
        """Delete a document.
        
        Args:
            document_id: ID of the document to delete
            
        Returns:
            True if successful, False otherwise
        """
        raise NotImplementedError("Subclasses must implement this method")
    
    async def list_documents(
        self,
        parent_id: Optional[str] = None,
        document_type: Optional[DocumentType] = None,
        **kwargs
    ) -> List[DocumentMetadata]:
        """List documents in a folder.
        
        Args:
            parent_id: ID of the parent folder (None for root)
            document_type: Filter by document type
            
        Returns:
            List of DocumentMetadata objects
        """
        raise NotImplementedError("Subclasses must implement this method")
    
    async def create_folder(
        self,
        name: str,
        parent_id: Optional[str] = None,
        **kwargs
    ) -> DocumentMetadata:
        """Create a new folder.
        
        Args:
            name: Name of the folder
            parent_id: ID of the parent folder (None for root)
            
        Returns:
            DocumentMetadata for the created folder
        """
        raise NotImplementedError("Subclasses must implement this method")
    
    async def share_document(
        self,
        document_id: str,
        email: str,
        role: DocumentPermission,
        message: Optional[str] = None,
        **kwargs
    ) -> bool:
        """Share a document with a user.
        
        Args:
            document_id: ID of the document to share
            email: Email address of the user to share with
            role: Permission level to grant
            message: Optional message to include in the share notification
            
        Returns:
            True if successful, False otherwise
        """
        raise NotImplementedError("Subclasses must implement this method")

class FileSystemDocumentIntegration(DocumentIntegration):
    """Local filesystem-based document integration."""
    
    def __init__(self, base_path: str, **kwargs):
        """Initialize filesystem integration.
        
        Args:
            base_path: Base directory path for document storage
        """
        super().__init__(**kwargs)
        self.base_path = Path(base_path).resolve()
        self.base_path.mkdir(parents=True, exist_ok=True)
    
    def _get_document_path(self, document_id: str) -> Path:
        """Get the filesystem path for a document ID."""
        return self.base_path / document_id
    
    def _get_metadata_path(self, document_id: str) -> Path:
        """Get the path for a document's metadata file."""
        return self.base_path / f"{document_id}.meta"
    
    def _load_metadata(self, document_id: str) -> Dict:
        """Load metadata for a document."""
        meta_path = self._get_metadata_path(document_id)
        if not meta_path.exists():
            raise FileNotFoundError(f"Metadata not found for document {document_id}")
        
        with open(meta_path, 'r', encoding='utf-8') as f:
            return json.load(f)
    
    def _save_metadata(self, document_id: str, metadata: Dict):
        """Save metadata for a document."""
        meta_path = self._get_metadata_path(document_id)
        with open(meta_path, 'w', encoding='utf-8') as f:
            json.dump(metadata, f, default=str)
    
    async def upload_document(
        self,
        name: str,
        content: Union[bytes, str, BinaryIO],
        parent_id: Optional[str] = None,
        mime_type: Optional[str] = None,
        **kwargs
    ) -> DocumentMetadata:
        """Upload a document to the filesystem."""
        import uuid
        from mimetypes import guess_type
        
        document_id = str(uuid.uuid4())
        doc_path = self._get_document_path(document_id)
        
        # Handle different content types
        if isinstance(content, str):
            content = content.encode('utf-8')
        
        if isinstance(content, bytes):
            with open(doc_path, 'wb') as f:
                f.write(content)
        elif hasattr(content, 'read'):
            with open(doc_path, 'wb') as f:
                if hasattr(content, 'seek'):
                    content.seek(0)
                f.write(content.read())
        else:
            raise ValueError("Content must be bytes, string, or file-like object")
        
        # Determine MIME type if not provided
        if not mime_type:
            mime_type, _ = guess_type(name)
        
        # Create metadata
        now = datetime.utcnow()
        metadata = {
            'id': document_id,
            'name': name,
            'type': DocumentType.OTHER.value,
            'mime_type': mime_type,
            'size': os.path.getsize(doc_path),
            'created_at': now.isoformat(),
            'modified_at': now.isoformat(),
            'parent_id': parent_id,
            'permissions': [],
            'custom_properties': {}
        }
        
        self._save_metadata(document_id, metadata)
        
        return DocumentMetadata(**metadata)
    
    async def download_document(self, document_id: str, **kwargs) -> DocumentContent:
        """Download a document from the filesystem."""
        doc_path = self._get_document_path(document_id)
        if not doc_path.exists():
            raise FileNotFoundError(f"Document {document_id} not found")
        
        metadata = self._load_metadata(document_id)
        
        with open(doc_path, 'rb') as f:
            content = f.read()
        
        return DocumentContent(
            metadata=DocumentMetadata(**metadata),
            content=content
        )
    
    async def get_document_metadata(self, document_id: str, **kwargs) -> DocumentMetadata:
        """Get metadata for a document."""
        metadata = self._load_metadata(document_id)
        return DocumentMetadata(**metadata)
    
    async def update_document(
        self,
        document_id: str,
        content: Optional[Union[bytes, str, BinaryIO]] = None,
        metadata_updates: Optional[Dict[str, Any]] = None,
        **kwargs
    ) -> DocumentMetadata:
        """Update a document's content and/or metadata."""
        doc_path = self._get_document_path(document_id)
        if not doc_path.exists():
            raise FileNotFoundError(f"Document {document_id} not found")
        
        metadata = self._load_metadata(document_id)
        
        # Update content if provided
        if content is not None:
            if isinstance(content, str):
                content = content.encode('utf-8')
            
            if isinstance(content, bytes):
                with open(doc_path, 'wb') as f:
                    f.write(content)
            elif hasattr(content, 'read'):
                with open(doc_path, 'wb') as f:
                    if hasattr(content, 'seek'):
                        content.seek(0)
                    f.write(content.read())
            
            metadata['size'] = os.path.getsize(doc_path)
            metadata['modified_at'] = datetime.utcnow().isoformat()
        
        # Update metadata if provided
        if metadata_updates:
            if 'name' in metadata_updates:
                metadata['name'] = metadata_updates['name']
            if 'custom_properties' in metadata_updates:
                metadata['custom_properties'].update(metadata_updates['custom_properties'])
            metadata['modified_at'] = datetime.utcnow().isoformat()
        
        self._save_metadata(document_id, metadata)
        
        return DocumentMetadata(**metadata)
    
    async def delete_document(self, document_id: str, **kwargs) -> bool:
        """Delete a document."""
        doc_path = self._get_document_path(document_id)
        meta_path = self._get_metadata_path(document_id)
        
        try:
            if doc_path.exists():
                os.remove(doc_path)
            if meta_path.exists():
                os.remove(meta_path)
            return True
        except OSError as e:
            self.logger.error(f"Failed to delete document {document_id}: {e}")
            return False
    
    async def list_documents(
        self,
        parent_id: Optional[str] = None,
        document_type: Optional[DocumentType] = None,
        **kwargs
    ) -> List[DocumentMetadata]:
        """List documents in the filesystem."""
        results = []
        
        for meta_file in self.base_path.glob("*.meta"):
            try:
                with open(meta_file, 'r', encoding='utf-8') as f:
                    metadata = json.load(f)
                
                # Filter by parent_id if specified
                if parent_id is not None and metadata.get('parent_id') != parent_id:
                    continue
                
                # Filter by document_type if specified
                if document_type is not None and metadata.get('type') != document_type.value:
                    continue
                
                results.append(DocumentMetadata(**metadata))
            except (json.JSONDecodeError, KeyError) as e:
                self.logger.warning(f"Invalid metadata file {meta_file}: {e}")
        
        return results
    
    async def create_folder(
        self,
        name: str,
        parent_id: Optional[str] = None,
        **kwargs
    ) -> DocumentMetadata:
        """Create a new folder."""
        import uuid
        
        folder_id = str(uuid.uuid4())
        folder_path = self.base_path / folder_id
        folder_path.mkdir(exist_ok=True)
        
        # Create a special metadata file for the folder
        now = datetime.utcnow()
        metadata = {
            'id': folder_id,
            'name': name,
            'type': DocumentType.FOLDER.value,
            'mime_type': 'inode/directory',
            'size': 0,
            'created_at': now.isoformat(),
            'modified_at': now.isoformat(),
            'parent_id': parent_id,
            'permissions': [],
            'custom_properties': {}
        }
        
        self._save_metadata(folder_id, metadata)
        
        return DocumentMetadata(**metadata)
    
    async def share_document(
        self,
        document_id: str,
        email: str,
        role: DocumentPermission,
        message: Optional[str] = None,
        **kwargs
    ) -> bool:
        """Share a document with a user (stub implementation)."""
        # In a real implementation, this would update the permissions
        # For the filesystem implementation, we'll just log the share
        self.logger.info(
            f"Shared document {document_id} with {email} as {role}. "
            f"Message: {message or 'No message'}"
        )
        return True

# Factory function for creating the appropriate document integration
def create_document_integration(provider: str, **kwargs) -> DocumentIntegration:
    """Create a document integration instance based on the provider.
    
    Args:
        provider: Document provider name ('filesystem', 'google', etc.)
        **kwargs: Provider-specific arguments
        
    Returns:
        An instance of the appropriate document integration class
    """
    provider = provider.lower()
    
    if provider == 'filesystem':
        if 'base_path' not in kwargs:
            raise ValueError("base_path is required for filesystem document integration")
        return FileSystemDocumentIntegration(**kwargs)
    else:
        raise ValueError(f"Unsupported document provider: {provider}")
