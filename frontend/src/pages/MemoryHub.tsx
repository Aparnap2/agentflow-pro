import React, { useState, useCallback, useMemo } from 'react';
import { useMemoryHub } from '../hooks/useMemoryHub';
import { 
  Trash2, 
  Eye, 
  BarChart3, 
  FileIcon,
  Plus,
  TrendingUp,
  Search
} from 'lucide-react';
import { toast } from 'react-hot-toast';
import { Document, DocumentChunk } from '../services/memoryApi';

// Helper function to get file icon based on file extension
const getFileIcon = (fileName: string) => {
  const extension = fileName.split('.').pop()?.toLowerCase() || '';
  
  // Return appropriate icon based on file extension
  if (['pdf'].includes(extension)) {
    return <FileIcon className="h-5 w-5 text-red-500" />;
  }
  if (['doc', 'docx'].includes(extension)) {
    return <FileIcon className="h-5 w-5 text-blue-600" />;
  }
  if (['xls', 'xlsx'].includes(extension)) {
    return <FileIcon className="h-5 w-5 text-green-600" />;
  }
  if (['jpg', 'jpeg', 'png', 'gif'].includes(extension)) {
    return <FileIcon className="h-5 w-5 text-purple-500" />;
  }
  if (['json'].includes(extension)) {
    return <FileIcon className="h-5 w-5 text-yellow-500" />;
  }
  if (['mp3', 'wav', 'ogg'].includes(extension)) {
    return <FileIcon className="h-5 w-5 text-pink-500" />;
  }
  if (['mp4', 'avi', 'mov'].includes(extension)) {
    return <FileIcon className="h-5 w-5 text-indigo-500" />;
  }
  if (['zip', 'rar', '7z'].includes(extension)) {
    return <FileIcon className="h-5 w-5 text-orange-500" />;
  }
  
  return <FileIcon className="h-5 w-5 text-gray-400" />;
};

// Helper function to format file size
const formatFileSize = (bytes: number): string => {
  if (bytes === 0) return '0 Bytes';
  const k = 1024;
  const sizes = ['Bytes', 'KB', 'MB', 'GB', 'TB'];
  const i = Math.floor(Math.log(bytes) / Math.log(k));
  return parseFloat((bytes / Math.pow(k, i)).toFixed(2)) + ' ' + sizes[i];
};

// Types
interface KnowledgeBaseInfo {
  activeContexts?: number;
  storageUsed?: number;
  storageLimit?: number;
  avgRetrievalTime?: string;
  memoryAccuracy?: number;
}

interface MemoryItemProps {
  id: string;
  type: string;
  content: string;
  metadata?: Record<string, any>;
  timestamp?: string;
}

// Component props
type MemoryHubProps = {
  // Add any props here if needed
};

const MemoryHub: React.FC<MemoryHubProps> = () => {
  // Use the memory hub hook
  const { 
    documents, 
    loading, 
    error, 
    uploadDocument, 
    deleteDocument, 
    fetchDocumentChunks,
    searchResults,
    setSearchQuery,
    searchQuery,
    refresh: refreshDocuments
  } = useMemoryHub();
  
  // Track selected document and its chunks
  const [selectedDocument, setSelectedDocument] = useState<Document | null>(null);
  const [isUploading, setIsUploading] = useState(false);
  const [activeTab, setActiveTab] = useState('knowledge');
  
  // Handle search term changes with debounce
  const handleSearchChange = useCallback((e: React.ChangeEvent<HTMLInputElement>) => {
    setSearchQuery(e.target.value);
  }, [setSearchQuery]);

  const handleFileUpload = async (event: React.ChangeEvent<HTMLInputElement>) => {
    const files = event.target.files;
    if (!files || files.length === 0) return;
    
    setIsUploading(true);
    try {
      // Use the document type from the file extension or default to 'TEXT'
      const file = files[0];
      const fileExtension = file.name.split('.').pop()?.toLowerCase() || '';
      const documentType = ['pdf', 'doc', 'docx', 'txt'].includes(fileExtension) ? 'TEXT' : 'BINARY';
      
      await uploadDocument(file, documentType);
      toast.success('File uploaded successfully');
      // Refresh documents list after upload
      await refreshDocuments();
    } catch (error) {
      console.error('Error uploading file:', error);
      toast.error('Failed to upload file');
    } finally {
      setIsUploading(false);
      // Reset file input
      if (event.target) {
        event.target.value = '';
      }
    }
  };

  const handleDocumentSelect = useCallback(async (doc: Document) => {
    setSelectedDocument(doc);
    try {
      // We'll fetch chunks if needed in the future
      // const chunks = await fetchDocumentChunks(doc.id);
    } catch (error) {
      console.error('Error fetching document chunks:', error);
      toast.error('Failed to load document chunks');
    }
  }, [fetchDocumentChunks]);

  const handleDeleteDocument = useCallback(async (docId: string, e: React.MouseEvent) => {
    e.stopPropagation();
    if (!window.confirm('Are you sure you want to delete this document?')) return;
    
    try {
      await deleteDocument(docId);
      toast.success('Document deleted successfully');
      
      // Clear selection if deleted document is currently selected
      if (selectedDocument?.id === docId) {
        setSelectedDocument(null);
        setDocumentChunks([]);
      }
      
      // Refresh documents list
      await refreshDocuments();
    } catch (error) {
      console.error('Error deleting document:', error);
      toast.error('Failed to delete document');
    }
  }, [deleteDocument, selectedDocument, refreshDocuments]);

  const handleSearchChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    const value = e.target.value;
    setSearchTerm(value);
  };

  const renderKnowledgeBaseTab = () => {
    const errorMessage = error ? (typeof error === 'object' && error !== null && 'message' in error 
      ? String(error.message) 
      : String(error)) 
      : 'Unknown error';
    
    return (
      <div className="space-y-4">
        {/* Upload Section */}
        <div className="bg-white p-4 rounded-lg shadow">
          <div className="flex items-center justify-between">
            <h3 className="text-lg font-medium">Upload Documents</h3>
            <label 
              className={`inline-flex items-center px-4 py-2 border border-transparent text-sm font-medium rounded-md shadow-sm text-white bg-blue-600 hover:bg-blue-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-blue-500 cursor-pointer ${isUploading ? 'opacity-50 cursor-not-allowed' : ''}`}
            >
              <Plus className="-ml-1 mr-2 h-5 w-5" />
              {isUploading ? 'Uploading...' : 'Upload File'}
              <input
                type="file"
                className="hidden"
                onChange={handleFileUpload}
                disabled={isUploading}
              />
            </label>
          </div>
          
          <p className="mt-2 text-sm text-gray-500">
            Upload documents to add to your knowledge base. Supported formats: PDF, DOCX, TXT, CSV
          </p>
          
          {error && (
            <div className="mt-4 p-3 bg-red-50 text-red-700 rounded-md text-sm">
              <div className="flex items-center">
                <span className="mr-2">⚠️</span>
                {errorMessage}
              </div>
            </div>
          )}
        </div>
        
        {/* Documents List */}
        <div className="bg-white rounded-lg shadow overflow-hidden">
          <div className="px-4 py-5 sm:px-6 border-b border-gray-200">
            <h3 className="text-lg leading-6 font-medium text-gray-900">Knowledge Base</h3>
            <p className="mt-1 max-w-2xl text-sm text-gray-500">
              Documents in your knowledge base
            </p>
          </div>
          
          <div className="overflow-x-auto">
            <table className="min-w-full divide-y divide-gray-200">
              <thead className="bg-gray-50">
                <tr>
                  <th scope="col" className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                    Name
                  </th>
                  <th scope="col" className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                    Type
                  </th>
                  <th scope="col" className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                    Size
                  </th>
                  <th scope="col" className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                    Uploaded
                  </th>
                  <th scope="col" className="relative px-6 py-3">
                    <span className="sr-only">Actions</span>
                  </th>
                </tr>
              </thead>
              <tbody className="bg-white divide-y divide-gray-200">
                {loading ? (
                  <tr>
                    <td colSpan={5} className="px-6 py-4 text-center text-sm text-gray-500">
                      Loading documents...
                    </td>
                  </tr>
                ) : documents.length === 0 ? (
                  <tr>
                    <td colSpan={5} className="px-6 py-4 text-center text-sm text-gray-500">
                      No documents found. Upload a document to get started.
                    </td>
                  </tr>
                ) : (
                  documents.map((doc) => {
                    const docMetadata = doc.metadata || {};
                    const docName = docMetadata.name || 'Untitled Document';
                    const docType = docMetadata.content_type || 'Unknown type';
                    const docSize = docMetadata.size ? formatFileSize(docMetadata.size) : 'N/A';
                    const uploadDate = doc.upload_date ? new Date(doc.upload_date).toLocaleDateString() : 'N/A';
                    
                    return (
                      <tr 
                        key={doc.id} 
                        className={`hover:bg-gray-50 cursor-pointer ${selectedDocument?.id === doc.id ? 'bg-blue-50' : ''}`}
                        onClick={() => handleDocumentSelect(doc)}
                      >
                        <td className="px-6 py-4 whitespace-nowrap">
                          <div className="flex items-center">
                            <div className="flex-shrink-0 h-10 w-10 flex items-center justify-center">
                              {getFileIcon(docName)}
                            </div>
                            <div className="ml-4">
                              <div className="text-sm font-medium text-gray-900">
                                {docName}
                              </div>
                              <div className="text-sm text-gray-500">
                                {docType}
                              </div>
                            </div>
                          </div>
                        </td>
                        <td className="px-6 py-4 whitespace-nowrap">
                          <div className="text-sm text-gray-900">{docType}</div>
                        </td>
                        <td className="px-6 py-4 whitespace-nowrap">
                          <div className="text-sm text-gray-900">
                            {docSize}
                          </div>
                        </td>
                        <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-500">
                          {uploadDate}
                        </td>
                        <td className="px-6 py-4 whitespace-nowrap text-right text-sm font-medium">
                          <div className="flex space-x-2 justify-end">
                            <button
                              onClick={(e) => {
                                e.stopPropagation();
                                handleDocumentSelect(doc);
                              }}
                              className="text-blue-600 hover:text-blue-900"
                              title="View document"
                            >
                              <Eye className="h-4 w-4" />
                            </button>
                            <button
                              onClick={(e) => handleDeleteDocument(doc.id, e)}
                              className="text-red-600 hover:text-red-900"
                              title="Delete document"
                            >
                              <Trash2 className="h-4 w-4" />
                            </button>
                          </div>
                        </td>
                      </tr>
                    );
                  })
                )}
              </tbody>
            </table>
          </div>
        </div>
      </div>
    );
  };



  const renderMemoryAnalyticsTab = () => {
    // Calculate document type distribution
    const documentTypes = documents.reduce((acc, doc) => {
      const type = doc.metadata?.content_type || 'Unknown';
      acc[type] = (acc[type] || 0) + 1;
      return acc;
    }, {} as Record<string, number>);
    
    // Get top 5 most recent documents
    const recentDocuments = [...documents]
      .sort((a, b) => {
        const dateA = a.updated_at || a.upload_date || 0;
        const dateB = b.updated_at || b.upload_date || 0;
        return new Date(dateB).getTime() - new Date(dateA).getTime();
      })
      .slice(0, 5);

    return (
      <div className="space-y-6">
        <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
          {/* Total Documents */}
          <div className="bg-blue-50 p-4 rounded-lg">
            <div className="flex items-center">
              <div className="p-3 rounded-full bg-blue-100 text-blue-600">
                <FileIcon className="h-6 w-6" />
              </div>
              <div className="ml-4">
                <p className="text-sm font-medium text-gray-500">Total Documents</p>
                <p className="text-2xl font-semibold text-gray-900">
                  {documents.length}
                </p>
              </div>
            </div>
          </div>
          
          {/* Total Chunks */}
          <div className="bg-green-50 p-4 rounded-lg">
            <div className="flex items-center">
              <div className="p-3 rounded-full bg-green-100 text-green-600">
                <FileIcon className="h-6 w-6" />
              </div>
              <div className="ml-4">
                <p className="text-sm font-medium text-gray-500">Total Chunks</p>
                <p className="text-2xl font-semibold text-gray-900">
                  {documents.reduce((acc, doc) => acc + (doc.chunk_count || 0), 0)}
                </p>
              </div>
            </div>
          </div>
          
          {/* Total Size */}
          <div className="bg-purple-50 p-4 rounded-lg">
            <div className="flex items-center">
              <div className="p-3 rounded-full bg-purple-100 text-purple-600">
                <TrendingUp className="h-6 w-6" />
              </div>
              <div className="ml-4">
                <p className="text-sm font-medium text-gray-500">Total Size</p>
                <p className="text-2xl font-semibold text-gray-900">
                  {formatFileSize(documents.reduce((acc, doc) => acc + (doc.metadata?.size || 0), 0))}
                </p>
              </div>
            </div>
          </div>
        </div>
        
        {/* Document Types Distribution */}
        <div className="mt-8">
          <h4 className="text-base font-medium text-gray-900 mb-4">Document Types</h4>
          <div className="bg-white border border-gray-200 rounded-lg p-4">
            <div className="grid grid-cols-2 md:grid-cols-3 lg:grid-cols-5 gap-4">
              {Object.entries(documentTypes).map(([type, count], index) => {
                const percentage = (count / documents.length) * 100;
                
                return (
                  <div key={index} className="text-center">
                    <div className="text-2xl font-semibold text-gray-900">{count}</div>
                    <div className="text-sm text-gray-500">{type || 'Unknown'}</div>
                    <div className="mt-1 w-full bg-gray-200 rounded-full h-2">
                      <div 
                        className="h-2 rounded-full bg-blue-600" 
                        style={{ width: `${percentage}%` }}
                      ></div>
                    </div>
                    <div className="text-xs text-gray-400 mt-1">{percentage.toFixed(1)}%</div>
                  </div>
                );
              })}
            </div>
          </div>
        </div>
        
        {/* Recent Activity */}
        <div className="mt-8">
          <h4 className="text-base font-medium text-gray-900 mb-4">Recent Activity</h4>
          <div className="bg-white border border-gray-200 rounded-lg overflow-hidden">
            <table className="min-w-full divide-y divide-gray-200">
              <thead className="bg-gray-50">
                <tr>
                  <th scope="col" className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                    Document
                  </th>
                  <th scope="col" className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                    Action
                  </th>
                  <th scope="col" className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                    Timestamp
                  </th>
                </tr>
              </thead>
              <tbody className="bg-white divide-y divide-gray-200">
                {recentDocuments.map((doc, index) => {
                  const docName = doc.metadata?.name || 'Untitled Document';
                  const docType = doc.metadata?.content_type || 'Unknown type';
                  const timestamp = doc.updated_at || doc.upload_date;
                  const action = doc.updated_at ? 'Updated' : 'Uploaded';
                  
                  return (
                    <tr key={index}>
                      <td className="px-6 py-4 whitespace-nowrap">
                        <div className="text-sm font-medium text-gray-900">
                          {docName}
                        </div>
                        <div className="text-sm text-gray-500">
                          {docType}
                        </div>
                      </td>
                      <td className="px-6 py-4 whitespace-nowrap">
                        <span className="px-2 inline-flex text-xs leading-5 font-semibold rounded-full bg-green-100 text-green-800">
                          {action}
                        </span>
                      </td>
                      <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-500">
                        {timestamp ? new Date(timestamp).toLocaleString() : 'N/A'}
                      </td>
                    </tr>
                  );
                })}
              </tbody>
            </table>
          </div>
        </div>
      </div>
    );
  };

  const renderSemanticSearchTab = useCallback(() => {
    return (
      <div className="space-y-4">
        <div className="bg-white p-4 rounded-lg shadow">
          <h3 className="text-lg font-medium mb-4">Semantic Search</h3>
          <div className="flex space-x-4">
            <div className="flex-1 relative">
              <div className="absolute inset-y-0 left-0 pl-3 flex items-center pointer-events-none">
                <Search className="h-5 w-5 text-gray-400" />
              </div>
              <input
                type="text"
                value={searchQuery}
                onChange={handleSearchChange}
                onKeyPress={(e) => e.key === 'Enter' && setSearchQuery(searchQuery)}
                placeholder="Search your knowledge base..."
                className="w-full pl-10 pr-4 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent"
              />
            </div>
          </div>
          
          {searchResults.length > 0 && (
            <div className="mt-6 space-y-4">
              <h4 className="text-sm font-medium text-gray-500 uppercase tracking-wider">
                Search Results
              </h4>
              <div className="bg-gray-50 rounded-lg divide-y divide-gray-200">
                {searchResults.map((result, index) => (
                  <div key={`${result.metadata?.document_id}-${index}`} className="p-4 hover:bg-white transition-colors duration-150">
                    <div className="flex items-start">
                      <div className="flex-shrink-0 h-10 w-10 rounded-full bg-blue-100 flex items-center justify-center">
                        <FileIcon className="h-5 w-5 text-blue-600" />
                      </div>
                      <div className="ml-4">
                        <div className="text-sm font-medium text-gray-900">
                          {result.metadata?.source || 'Document'}
                        </div>
                        <div className="mt-1 text-sm text-gray-500">
                          {result.content?.substring(0, 200)}...
                        </div>
                        {result.score !== undefined && (
                          <div className="mt-2 flex items-center text-xs text-gray-400">
                            <span>Relevance: {(result.score * 100).toFixed(1)}%</span>
                          </div>
                        )}
                      </div>
                    </div>
                  </div>
                ))}
              </div>
            </div>
          )}
          
          {searchQuery && searchResults.length === 0 && !loading && (
            <div className="mt-6 text-center py-8 bg-gray-50 rounded-lg">
              <p className="text-gray-500">No results found for "{searchQuery}"</p>
            </div>
          )}
          
          {loading && activeTab === 'search' && (
            <div className="mt-6 text-center py-8">
              <div className="inline-flex items-center space-x-2">
                <div className="w-4 h-4 rounded-full bg-blue-600 animate-pulse"></div>
                <span className="text-sm text-gray-500">Searching...</span>
              </div>
            </div>
          )}
        </div>
      </div>
    );
  }, [searchQuery, searchResults, loading, activeTab, handleSearchChange, setSearchQuery]);

  // Tabs configuration
  const tabs = useMemo(() => [
    { 
      id: 'knowledge', 
      name: 'Knowledge Base', 
      icon: FileIcon,
      count: documents.length 
    },
    { 
      id: 'search', 
      name: 'Semantic Search', 
      icon: Search, 
      count: searchResults.length 
    },
    { 
      id: 'analytics', 
      name: 'Memory Analytics', 
      icon: BarChart3, 
      count: 0 
    }
  ], [documents.length, searchResults.length]);

  return (
    <div className="h-full flex flex-col">
      {/* Header */}
      <div className="border-b border-gray-200 px-6 py-4">
        <h2 className="text-2xl font-semibold text-gray-900">Memory Hub</h2>
        <p className="mt-1 text-sm text-gray-500">
          Manage your knowledge base and memory systems
        </p>
      </div>
      
      {/* Tabs */}
      <div className="border-b border-gray-200">
        <nav className="-mb-px flex space-x-8 px-6">
          {tabs.map((tab) => (
            <button
              key={tab.id}
              onClick={() => setActiveTab(tab.id)}
              className={`${
                activeTab === tab.id
                  ? 'border-blue-500 text-blue-600'
                  : 'border-transparent text-gray-500 hover:text-gray-700 hover:border-gray-300'
              } whitespace-nowrap py-4 px-1 border-b-2 font-medium text-sm flex items-center`}
            >
              <tab.icon className="h-4 w-4 mr-2" />
              {tab.name}
              {tab.count > 0 && (
                <span className="ml-2 bg-gray-100 text-gray-600 text-xs font-medium px-2 py-0.5 rounded-full">
                  {tab.count}
                </span>
              )}
            </button>
          ))}
        </nav>
      </div>

      {/* Tab Content */}
      <div className="flex-1 overflow-auto p-6">
        {activeTab === 'knowledge' && renderKnowledgeBaseTab()}
        {activeTab === 'search' && renderSemanticSearchTab()}
        {activeTab === 'analytics' && renderMemoryAnalyticsTab()}
      </div>
      
      {/* Hidden file input */}
      <input
        id="file-upload"
        type="file"
        className="hidden"
        onChange={handleFileUpload}
        multiple
      />
    </div>
  );
};

export default MemoryHub;