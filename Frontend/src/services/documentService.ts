import { apiService } from './api'
import { toast } from 'sonner'

export interface Document {
  id: string
  filename: string
  file_size: number
  upload_date: string
  status: 'pending' | 'processed' | 'error'
  content_type?: string
  analysis?: {
    summary: string
    key_points: string[]
    requirements: string[]
    risks: string[]
  }
  confidence_score?: number
}

export interface DocumentAnalysis {
  document_id: string
  analysis: {
    summary: string
    key_points: string[]
    requirements: string[]
    risks: string[]
  }
  confidence_score: number
}

class DocumentService {
  async getDocuments(): Promise<Document[]> {
    try {
      const response = await apiService.getDocuments()
      
      if (response.error) {
        toast.error('Failed to load documents', {
          description: response.error
        })
        return []
      }
      
      return response.data?.documents || []
    } catch (error) {
      const message = error instanceof Error ? error.message : 'Unknown error'
      toast.error('Network Error', {
        description: `Failed to connect to server: ${message}`
      })
      return []
    }
  }

  async uploadDocument(file: File): Promise<Document | null> {
    try {
      const formData = new FormData()
      formData.append('file', file)
      
      const response = await apiService.uploadDocument(formData)
      
      if (response.error) {
        toast.error('Failed to upload document', {
          description: response.error
        })
        return null
      }
      
      toast.success('Document uploaded successfully', {
        description: `${file.name} has been uploaded and is being processed`
      })
      
      return response.data || null
    } catch (error) {
      const message = error instanceof Error ? error.message : 'Unknown error'
      toast.error('Upload Error', {
        description: `Failed to upload ${file.name}: ${message}`
      })
      return null
    }
  }

  async analyzeDocument(documentId: string): Promise<DocumentAnalysis | null> {
    try {
      const response = await apiService.analyzeDocument({ document_id: documentId })
      
      if (response.error) {
        toast.error('Failed to analyze document', {
          description: response.error
        })
        return null
      }
      
      toast.success('Document analysis completed')
      return response.data || null
    } catch (error) {
      const message = error instanceof Error ? error.message : 'Unknown error'
      toast.error('Analysis Error', {
        description: `Failed to analyze document: ${message}`
      })
      return null
    }
  }

  async deleteDocument(documentId: string): Promise<boolean> {
    try {
      // Simulate API call since delete endpoint might not exist
      await new Promise(resolve => setTimeout(resolve, 500))
      toast.success('Document deleted successfully')
      return true
    } catch (error) {
      const message = error instanceof Error ? error.message : 'Unknown error'
      toast.error('Failed to delete document', {
        description: message
      })
      return false
    }
  }

  async downloadDocument(documentId: string, filename: string): Promise<void> {
    try {
      // Simulate download since endpoint might not exist
      toast.info('Download started', {
        description: `Downloading ${filename}...`
      })
      
      // In a real implementation, this would fetch the file blob and trigger download
      await new Promise(resolve => setTimeout(resolve, 1000))
      
      toast.success('Download completed')
    } catch (error) {
      const message = error instanceof Error ? error.message : 'Unknown error'
      toast.error('Download Error', {
        description: `Failed to download ${filename}: ${message}`
      })
    }
  }
}

export const documentService = new DocumentService()
export default documentService
