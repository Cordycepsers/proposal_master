import { useState, useEffect } from 'react'
import { Card, CardContent, CardHeader, CardTitle } from "./ui/card"
import { Button } from "./ui/button"
import { Input } from "./ui/input"
import { Badge } from "./ui/badge"
import { FileUpload } from "./FileUpload"
import { documentService, Document as DocumentType } from '../services'
import { Upload, FileText, Search, Download, AlertCircle, CheckCircle, Clock, Trash2 } from "lucide-react"
import { toast } from 'sonner'

// Define a Document interface compatible with the current component
interface Document {
  id: string
  filename: string
  original_filename?: string
  file_size: number
  file_type: string
  upload_timestamp: string
  processing_status: string
  content_preview?: string
  page_count?: number
  word_count?: number
}

interface SearchResult {
  document_id: string
  relevance_score: number
  highlighted_content: string
}

export function DocumentManagement() {
  const [documents, setDocuments] = useState<Document[]>([])
  const [loading, setLoading] = useState(true)
  const [searchQuery, setSearchQuery] = useState("")
  const [searchResults, setSearchResults] = useState<SearchResult[]>([])
  const [searchLoading, setSearchLoading] = useState(false)

  useEffect(() => {
    fetchDocuments()
  }, [])

  const fetchDocuments = async () => {
    setLoading(true)
    try {
      const documentsData = await documentService.getDocuments()
      // Map the service documents to our component interface
      const mappedDocuments: Document[] = documentsData.map(doc => ({
        id: doc.id,
        filename: doc.filename,
        original_filename: doc.filename,
        file_size: doc.file_size,
        file_type: doc.content_type || 'unknown',
        upload_timestamp: doc.upload_date,
        processing_status: doc.status,
        content_preview: undefined,
        page_count: undefined,
        word_count: undefined
      }))
      setDocuments(mappedDocuments)
    } catch (error) {
      toast.error('Failed to fetch documents')
      console.error('Failed to fetch documents:', error)
    } finally {
      setLoading(false)
    }
  }

  const handleUploadSuccess = async (uploadedDocuments: DocumentType[]) => {
    toast.success(`Successfully uploaded ${uploadedDocuments.length} document(s)`)
    await fetchDocuments() // Refresh the list
  }

  const handleUploadError = (error: string) => {
    toast.error('Upload failed', { description: error })
  }

  const handleSearch = async () => {
    if (!searchQuery.trim()) {
      toast.error('Please enter a search query')
      return
    }

    setSearchLoading(true)
    try {
      // Since we don't have a search endpoint in the service yet, simulate it
      await new Promise(resolve => setTimeout(resolve, 1000))
      
      // Mock search results for now
      const mockResults: SearchResult[] = documents
        .filter(doc => 
          doc.filename.toLowerCase().includes(searchQuery.toLowerCase()) ||
          doc.content_preview?.toLowerCase().includes(searchQuery.toLowerCase())
        )
        .map(doc => ({
          document_id: doc.id,
          relevance_score: Math.random(),
          highlighted_content: doc.content_preview || `Content from ${doc.filename}`
        }))
      
      setSearchResults(mockResults)
      toast.success(`Found ${mockResults.length} results`)
    } catch (error) {
      toast.error('Search failed')
      console.error('Search failed:', error)
    } finally {
      setSearchLoading(false)
    }
  }

  const handleDelete = async (documentId: string) => {
    try {
      const success = await documentService.deleteDocument(documentId)
      if (success) {
        await fetchDocuments()
      }
    } catch (error) {
      console.error('Delete failed:', error)
    }
  }

  const handleDownload = async (documentId: string, filename: string) => {
    try {
      await documentService.downloadDocument(documentId, filename)
    } catch (error) {
      console.error('Download failed:', error)
    }
  }

  const formatFileSize = (bytes: number) => {
    if (bytes === 0) return '0 Bytes'
    const k = 1024
    const sizes = ['Bytes', 'KB', 'MB', 'GB']
    const i = Math.floor(Math.log(bytes) / Math.log(k))
    return parseFloat((bytes / Math.pow(k, i)).toFixed(2)) + ' ' + sizes[i]
  }

  const getStatusIcon = (status: string) => {
    switch (status) {
      case 'completed':
        return <CheckCircle className="h-4 w-4 text-green-500" />
      case 'processing':
        return <Clock className="h-4 w-4 text-yellow-500" />
      case 'failed':
        return <AlertCircle className="h-4 w-4 text-red-500" />
      default:
        return <Clock className="h-4 w-4 text-gray-500" />
    }
  }

  const getStatusBadge = (status: string) => {
    const variants = {
      completed: 'default',
      processing: 'secondary', 
      failed: 'destructive'
    } as const
    
    return (
      <Badge variant={variants[status as keyof typeof variants] || 'secondary'}>
        {status}
      </Badge>
    )
  }

  return (
    <div className="space-y-6">
      {/* Upload Section */}
      <Card>
        <CardHeader>
          <CardTitle className="flex items-center gap-2">
            <Upload className="h-5 w-5" />
            Upload Documents
          </CardTitle>
        </CardHeader>
        <CardContent>
          <FileUpload
            onUploadSuccess={handleUploadSuccess}
            onUploadError={handleUploadError}
            acceptedFileTypes={['.pdf', '.docx', '.txt', '.md']}
            maxSize={50 * 1024 * 1024} // 50MB
            maxFiles={10}
          />
        </CardContent>
      </Card>

      {/* Search Section */}
      <Card>
        <CardHeader>
          <CardTitle className="flex items-center gap-2">
            <Search className="h-5 w-5" />
            Search Documents
          </CardTitle>
        </CardHeader>
        <CardContent>
          <div className="flex gap-2">
            <Input
              placeholder="Search for requirements, keywords, or content..."
              value={searchQuery}
              onChange={(e) => setSearchQuery(e.target.value)}
              onKeyPress={(e) => e.key === 'Enter' && handleSearch()}
              className="flex-1"
            />
            <Button onClick={handleSearch} disabled={searchLoading}>
              {searchLoading ? 'Searching...' : 'Search'}
            </Button>
          </div>
          
          {searchResults.length > 0 && (
            <div className="mt-4 space-y-2">
              <h4 className="font-medium">Search Results:</h4>
              {searchResults.map((result, index) => (
                <div key={index} className="p-3 border rounded-lg">
                  <p className="text-sm">{result.highlighted_content}</p>
                  <div className="flex justify-between items-center mt-2">
                    <span className="text-xs text-muted-foreground">
                      Document ID: {result.document_id}
                    </span>
                    <Badge variant="outline">
                      {Math.round(result.relevance_score * 100)}% match
                    </Badge>
                  </div>
                </div>
              ))}
            </div>
          )}
        </CardContent>
      </Card>

      {/* Documents List */}
      <Card>
        <CardHeader>
          <CardTitle className="flex items-center gap-2">
            <FileText className="h-5 w-5" />
            Document Library
          </CardTitle>
        </CardHeader>
        <CardContent>
          {loading ? (
            <div className="text-center py-8">
              <p>Loading documents...</p>
            </div>
          ) : documents.length === 0 ? (
            <div className="text-center py-8 text-muted-foreground">
              <FileText className="h-12 w-12 mx-auto mb-4 opacity-50" />
              <p>No documents uploaded yet</p>
              <p className="text-sm">Upload your first RFP document to get started</p>
            </div>
          ) : (
            <div className="space-y-4">
              {documents.map((doc) => (
                <div key={doc.id} className="border rounded-lg p-4">
                  <div className="flex items-start justify-between">
                    <div className="flex-1">
                      <div className="flex items-center gap-2 mb-2">
                        <FileText className="h-4 w-4" />
                        <h4 className="font-medium">{doc.original_filename}</h4>
                        {getStatusIcon(doc.processing_status)}
                        {getStatusBadge(doc.processing_status)}
                      </div>
                      
                      <div className="grid grid-cols-2 md:grid-cols-4 gap-4 text-sm text-muted-foreground mb-3">
                        <div>Size: {formatFileSize(doc.file_size)}</div>
                        <div>Type: {doc.file_type.toUpperCase()}</div>
                        {doc.page_count && <div>Pages: {doc.page_count}</div>}
                        {doc.word_count && <div>Words: {doc.word_count.toLocaleString()}</div>}
                      </div>

                      {doc.content_preview && (
                        <div className="text-sm">
                          <span className="font-medium">Preview: </span>
                          <span className="text-muted-foreground">
                            {doc.content_preview.substring(0, 150)}...
                          </span>
                        </div>
                      )}
                    </div>

                    <div className="flex gap-2 ml-4">
                      <Button 
                        variant="outline" 
                        size="sm"
                        onClick={() => handleDownload(doc.id, doc.filename)}
                      >
                        <Download className="h-4 w-4" />
                      </Button>
                      <Button 
                        variant="outline" 
                        size="sm" 
                        className="text-red-600 hover:text-red-700"
                        onClick={() => handleDelete(doc.id)}
                      >
                        <Trash2 className="h-4 w-4" />
                      </Button>
                    </div>
                  </div>
                </div>
              ))}
            </div>
          )}
        </CardContent>
      </Card>
    </div>
  )
}
