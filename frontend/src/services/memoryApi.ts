import { api } from './api';
import { toast } from 'react-hot-toast';

// Types
export interface DocumentChunk {
  id: string;
  content: string;
  metadata: {
    document_id: string;
    source: string;
    page?: number;
    chunk_index: number;
    [key: string]: any;
  };
  score?: number;
}

export interface Document {
  updated_at: string;
  name: string;
  size: any;
  id: string;
  filename: string;
  content_type: string;
  document_type: string;
  upload_date: string;
  metadata: Record<string, any>;
  chunk_count: number;
}

export interface KnowledgeBaseInfo {
  document_count: number;
  total_chunks: number;
  vector_store: string;
  embedding_model: string;
  status: 'ready' | 'indexing' | 'error';
  last_updated: string;
}

// API Functions
export const memoryApi = {
  // Search documents
  async searchDocuments(query: string, limit: number = 10, minScore: number = 0.5): Promise<DocumentChunk[]> {
    try {
      const response = await api.get('/rag/documents/search', {
        params: { query, limit, min_score: minScore }
      });
      return response.data;
    } catch (error: any) {
      console.error('Error searching documents:', error);
      toast.error(error.response?.data?.detail || 'Failed to search documents');
      throw error;
    }
  },

  // Upload document
  async uploadDocument(file: File, documentType: string = 'TEXT', metadata: Record<string, any> = {}): Promise<{ document_id: string }> {
    const formData = new FormData();
    formData.append('file', file);
    formData.append('document_type', documentType);
    formData.append('metadata', JSON.stringify(metadata));

    try {
      const response = await api.post('/rag/documents', formData, {
        headers: {
          'Content-Type': 'multipart/form-data',
        },
      });
      toast.success('Document uploaded successfully');
      return response.data;
    } catch (error: any) {
      console.error('Error uploading document:', error);
      toast.error(error.response?.data?.detail || 'Failed to upload document');
      throw error;
    }
  },

  // Get document chunks
  async getDocumentChunks(documentId: string, limit: number = 100, offset: number = 0): Promise<DocumentChunk[]> {
    try {
      const response = await api.get(`/rag/documents/${documentId}/chunks`, {
        params: { limit, offset }
      });
      return response.data;
    } catch (error: any) {
      console.error('Error fetching document chunks:', error);
      toast.error(error.response?.data?.detail || 'Failed to fetch document chunks');
      throw error;
    }
  },

  // Get knowledge base info
  async getKnowledgeBaseInfo(): Promise<KnowledgeBaseInfo> {
    try {
      const response = await api.get('/rag/info');
      return response.data;
    } catch (error: any) {
      console.error('Error fetching knowledge base info:', error);
      toast.error('Failed to fetch knowledge base info');
      throw error;
    }
  },

  // Delete document
  async deleteDocument(documentId: string): Promise<void> {
    try {
      await api.delete(`/rag/documents/${documentId}`);
      toast.success('Document deleted successfully');
    } catch (error: any) {
      console.error('Error deleting document:', error);
      toast.error(error.response?.data?.detail || 'Failed to delete document');
      throw error;
    }
  },

  // Get all documents
  async listDocuments(limit: number = 100, offset: number = 0): Promise<{ documents: Document[]; total: number }> {
    try {
      // Note: You'll need to implement this endpoint in your backend
      const response = await api.get('/rag/documents', {
        params: { limit, offset }
      });
      return response.data;
    } catch (error: any) {
      console.error('Error listing documents:', error);
      toast.error('Failed to list documents');
      throw error;
    }
  },
};

export default memoryApi;
