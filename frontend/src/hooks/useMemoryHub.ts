import { useState, useEffect, useCallback } from 'react';
import { memoryApi, Document, DocumentChunk, KnowledgeBaseInfo } from '../services/memoryApi';

export const useMemoryHub = () => {
  // State
  const [documents, setDocuments] = useState<Document[]>([]);
  const [searchResults, setSearchResults] = useState<DocumentChunk[]>([]);
  const [selectedDocument, setSelectedDocument] = useState<Document | null>(null);
  const [documentChunks, setDocumentChunks] = useState<DocumentChunk[]>([]);
  const [knowledgeBaseInfo, setKnowledgeBaseInfo] = useState<KnowledgeBaseInfo | null>(null);
  const [loading, setLoading] = useState<boolean>(false);
  const [error, setError] = useState<string | null>(null);
  const [searchQuery, setSearchQuery] = useState<string>('');

  // Fetch all documents
  const fetchDocuments = useCallback(async () => {
    setLoading(true);
    setError(null);
    try {
      const { documents } = await memoryApi.listDocuments();
      setDocuments(documents);
    } catch (err: any) {
      setError(err.message || 'Failed to fetch documents');
      console.error('Error fetching documents:', err);
    } finally {
      setLoading(false);
    }
  }, []);

  // Search documents
  const searchDocuments = useCallback(async (query: string) => {
    if (!query.trim()) {
      setSearchResults([]);
      return;
    }

    setLoading(true);
    setError(null);
    try {
      const results = await memoryApi.searchDocuments(query);
      setSearchResults(results);
    } catch (err: any) {
      setError(err.message || 'Search failed');
      console.error('Error searching documents:', err);
    } finally {
      setLoading(false);
    }
  }, []);

  // Upload document
  const uploadDocument = useCallback(async (file: File, documentType: string = 'TEXT', metadata: Record<string, any> = {}) => {
    setLoading(true);
    setError(null);
    try {
      await memoryApi.uploadDocument(file, documentType, metadata);
      await fetchDocuments(); // Refresh the document list
    } catch (err: any) {
      setError(err.message || 'Upload failed');
      console.error('Error uploading document:', err);
      throw err;
    } finally {
      setLoading(false);
    }
  }, [fetchDocuments]);

  // Fetch document chunks
  const fetchDocumentChunks = useCallback(async (documentId: string) => {
    setLoading(true);
    setError(null);
    try {
      const chunks = await memoryApi.getDocumentChunks(documentId);
      setDocumentChunks(chunks);
      return chunks;
    } catch (err: any) {
      setError(err.message || 'Failed to fetch document chunks');
      console.error('Error fetching document chunks:', err);
      throw err;
    } finally {
      setLoading(false);
    }
  }, []);

  // Delete document
  const deleteDocument = useCallback(async (documentId: string) => {
    setLoading(true);
    setError(null);
    try {
      await memoryApi.deleteDocument(documentId);
      await fetchDocuments(); // Refresh the document list
    } catch (err: any) {
      setError(err.message || 'Deletion failed');
      console.error('Error deleting document:', err);
      throw err;
    } finally {
      setLoading(false);
    }
  }, [fetchDocuments]);

  // Fetch knowledge base info
  const fetchKnowledgeBaseInfo = useCallback(async () => {
    setLoading(true);
    setError(null);
    try {
      const info = await memoryApi.getKnowledgeBaseInfo();
      setKnowledgeBaseInfo(info);
      return info;
    } catch (err: any) {
      setError(err.message || 'Failed to fetch knowledge base info');
      console.error('Error fetching knowledge base info:', err);
      throw err;
    } finally {
      setLoading(false);
    }
  }, []);

  // Initialize
  useEffect(() => {
    fetchDocuments();
    fetchKnowledgeBaseInfo();
  }, [fetchDocuments, fetchKnowledgeBaseInfo]);

  // Handle search query changes with debounce
  useEffect(() => {
    const timer = setTimeout(() => {
      if (searchQuery) {
        searchDocuments(searchQuery);
      } else {
        setSearchResults([]);
      }
    }, 500);

    return () => clearTimeout(timer);
  }, [searchQuery, searchDocuments]);

  return {
    // State
    documents,
    searchResults,
    selectedDocument,
    documentChunks,
    knowledgeBaseInfo,
    loading,
    error,
    searchQuery,
    
    // Actions
    setSearchQuery,
    setSelectedDocument,
    uploadDocument,
    deleteDocument,
    fetchDocumentChunks,
    refresh: fetchDocuments,
  };
};

export default useMemoryHub;
