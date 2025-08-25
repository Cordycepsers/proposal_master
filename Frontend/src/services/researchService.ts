import { apiService } from './api'
import { toast } from 'sonner'

export interface ResearchResult {
  title: string
  content: string
  source: string
  url?: string
  relevance_score: number
}

export interface ResearchResponse {
  query: string
  results: ResearchResult[]
  summary: string
}

export interface FeedbackData {
  type: string
  content: string
  rating?: number
  metadata?: Record<string, any>
}

export interface FeedbackResponse {
  feedback_id: string
  message: string
}

class ResearchService {
  async conductResearch(query: string): Promise<ResearchResponse | null> {
    if (!query.trim()) {
      toast.error('Please enter a research query')
      return null
    }

    try {
      toast.info('Conducting research...', {
        description: 'This may take a few moments'
      })

      const response = await apiService.conductResearch(query)
      
      if (response.error) {
        toast.error('Research failed', {
          description: response.error
        })
        return null
      }
      
      const resultCount = response.data?.results?.length || 0
      toast.success('Research completed', {
        description: `Found ${resultCount} relevant results`
      })
      
      return response.data || null
    } catch (error) {
      const message = error instanceof Error ? error.message : 'Unknown error'
      toast.error('Research Error', {
        description: `Failed to conduct research: ${message}`
      })
      return null
    }
  }

  async submitFeedback(data: FeedbackData): Promise<FeedbackResponse | null> {
    if (!data.content.trim()) {
      toast.error('Please provide feedback content')
      return null
    }

    try {
      const response = await apiService.submitFeedback(data)
      
      if (response.error) {
        toast.error('Failed to submit feedback', {
          description: response.error
        })
        return null
      }
      
      toast.success('Feedback submitted successfully', {
        description: 'Thank you for your feedback!'
      })
      
      return response.data || null
    } catch (error) {
      const message = error instanceof Error ? error.message : 'Unknown error'
      toast.error('Submission Error', {
        description: `Failed to submit feedback: ${message}`
      })
      return null
    }
  }

  async saveResearch(query: string, results: ResearchResult[]): Promise<boolean> {
    try {
      // Simulate saving research data locally or to backend
      const researchData = {
        id: Date.now().toString(),
        query,
        results,
        timestamp: new Date().toISOString()
      }
      
      // Store in localStorage for now
      const savedResearch = localStorage.getItem('saved_research')
      const researchList = savedResearch ? JSON.parse(savedResearch) : []
      researchList.push(researchData)
      localStorage.setItem('saved_research', JSON.stringify(researchList))
      
      toast.success('Research saved', {
        description: 'Research results have been saved for later reference'
      })
      
      return true
    } catch (error) {
      const message = error instanceof Error ? error.message : 'Unknown error'
      toast.error('Failed to save research', {
        description: message
      })
      return false
    }
  }

  async getSavedResearch(): Promise<any[]> {
    try {
      const savedResearch = localStorage.getItem('saved_research')
      return savedResearch ? JSON.parse(savedResearch) : []
    } catch (error) {
      console.error('Failed to load saved research:', error)
      return []
    }
  }

  async deleteSavedResearch(researchId: string): Promise<boolean> {
    try {
      const savedResearch = localStorage.getItem('saved_research')
      if (!savedResearch) return false
      
      const researchList = JSON.parse(savedResearch)
      const filteredList = researchList.filter((item: any) => item.id !== researchId)
      localStorage.setItem('saved_research', JSON.stringify(filteredList))
      
      toast.success('Research deleted')
      return true
    } catch (error) {
      const message = error instanceof Error ? error.message : 'Unknown error'
      toast.error('Failed to delete research', {
        description: message
      })
      return false
    }
  }
}

export const researchService = new ResearchService()
export default researchService
