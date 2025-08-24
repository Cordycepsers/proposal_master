import { useState, useEffect } from 'react'
import { Card, CardContent, CardHeader, CardTitle } from "./ui/card"
import { Button } from "./ui/button"
import { Input } from "./ui/input"
import { Badge } from "./ui/badge"
import { Progress } from "./ui/progress"
import { Separator } from "./ui/separator"
import { Upload, FileText, Search, Download, AlertCircle, CheckCircle, Clock, Trash2 } from "lucide-react"

// Mock API service (replace with actual API calls)
const mockApiService = {
  async getDocuments() {
    return {
      data: {
        documents: [
          {
            id: "1",
            filename: "rfp_proposal_2024.pdf",
            original_filename: "RFP_Government_Contract_2024.pdf",
            file_size: 2048576,
            file_type: "pdf",
            upload_timestamp: new Date().toISOString(),
            processing_status: "completed",
            content_preview: "Request for Proposal for Government IT Services...",
            page_count: 25,
            word_count: 5432
          },
          {
            id: "2", 
            filename: "tech_requirements.docx",
            original_filename: "Technical_Requirements_Document.docx",
            file_size: 1024000,
            file_type: "docx",
            upload_timestamp: new Date().toISOString(),
            processing_status: "processing",
            page_count: 12,
            word_count: 2876
          }
        ],
        total: 2
      }
    }
  },

  async uploadDocument(file: File) {
    return {
      data: {
        document_id: Math.random().toString(36),
        filename: file.name,
        status: "uploaded",
        message: "Document uploaded successfully"
      }
    }
  },

  async searchDocuments(query: string) {
    return {
      data: {
        query,
        results: [
          {
            id: "1",
            content: "This section outlines the technical requirements for the proposed solution...",
            metadata: { filename: "rfp_proposal_2024.pdf", page: 5 },
            similarity_score: 0.85
          }
        ],
        total_results: 1
      }
    }
  }
}

interface Document {
  id: string
  filename: string
  original_filename: string
  file_size: number
  file_type: string
  upload_timestamp: string
  processing_status: string
  content_preview?: string
  page_count?: number
  word_count?: number
}

export function DocumentManagement() {
  const [documents, setDocuments] = useState<Document[]>([])
  const [loading, setLoading] = useState(true)
  const [uploading, setUploading] = useState(false)
  const [searchQuery, setSearchQuery] = useState("")
  const [searchResults, setSearchResults] = useState<any[]>([])
  const [searchLoading, setSearchLoading] = useState(false)

  useEffect(() => {
    fetchDocuments()
  }, [])

  const fetchDocuments = async () => {
    setLoading(true)
    try {
      const response = await mockApiService.getDocuments()
      if (response.data) {
        setDocuments(response.data.documents)
      }
    } catch (error) {
      console.error('Failed to fetch documents:', error)
    } finally {
      setLoading(false)
    }
  }

  const handleFileUpload = async (event: React.ChangeEvent<HTMLInputElement>) => {
    const file = event.target.files?.[0]
    if (!file) return

    setUploading(true)
    try {
      await mockApiService.uploadDocument(file)
      await fetchDocuments() // Refresh the list
    } catch (error) {
      console.error('Upload failed:', error)
    } finally {
      setUploading(false)
    }
  }

  const handleSearch = async () => {
    if (!searchQuery.trim()) return

    setSearchLoading(true)
    try {
      const response = await mockApiService.searchDocuments(searchQuery)
      if (response.data) {
        setSearchResults(response.data.results)
      }
    } catch (error) {
      console.error('Search failed:', error)
    } finally {
      setSearchLoading(false)
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
          <div className="flex items-center gap-4">
            <Input
              type="file"
              accept=".pdf,.docx,.txt,.md"
              onChange={handleFileUpload}
              disabled={uploading}
              className="flex-1"
            />
            {uploading && (
              <div className="flex items-center gap-2">
                <Progress value={65} className="w-32" />
                <span className="text-sm text-muted-foreground">Uploading...</span>
              </div>
            )}
          </div>
          <p className="text-sm text-muted-foreground mt-2">
            Supported formats: PDF, DOCX, TXT, MD (Max size: 50MB)
          </p>
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
                  <p className="text-sm">{result.content}</p>
                  <div className="flex justify-between items-center mt-2">
                    <span className="text-xs text-muted-foreground">
                      {result.metadata.filename} - Page {result.metadata.page}
                    </span>
                    <Badge variant="outline">
                      {Math.round(result.similarity_score * 100)}% match
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
                      <Button variant="outline" size="sm">
                        <Download className="h-4 w-4" />
                      </Button>
                      <Button variant="outline" size="sm" className="text-red-600 hover:text-red-700">
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
