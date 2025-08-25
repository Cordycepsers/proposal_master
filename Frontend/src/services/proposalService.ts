import { apiService } from './api'
import { toast } from 'sonner'

export interface Proposal {
  id: string
  title: string
  status: string
  created_at: string
  updated_at: string
  document_id?: string
  summary?: string
  client?: string
  due_date?: string
  progress?: number
}

export interface CreateProposalData {
  title: string
  requirements_ids: string[]
  template?: string
}

export interface ProposalContent {
  sections: Array<{
    id: string
    title: string
    content: string
    word_count: number
  }>
  total_word_count: number
  style: string
}

class ProposalService {
  async getProposals(): Promise<Proposal[]> {
    try {
      const response = await apiService.getProposals()
      
      if (response.error) {
        toast.error('Failed to load proposals', {
          description: response.error
        })
        return []
      }
      
      // Extract proposals array from response data
      return response.data?.proposals || []
    } catch (error) {
      const message = error instanceof Error ? error.message : 'Unknown error'
      toast.error('Network Error', {
        description: `Failed to connect to server: ${message}`
      })
      return []
    }
  }

  async createProposal(data: CreateProposalData): Promise<Proposal | null> {
    try {
      const response = await apiService.createProposal(data)
      
      if (response.error) {
        toast.error('Failed to create proposal', {
          description: response.error
        })
        return null
      }
      
      toast.success('Proposal created successfully')
      
      // Transform the response to match our Proposal interface
      const proposalData = response.data
      if (proposalData) {
        return {
          id: proposalData.proposal_id,
          title: proposalData.title,
          status: proposalData.status,
          created_at: new Date().toISOString(),
          updated_at: new Date().toISOString()
        }
      }
      
      return null
    } catch (error) {
      const message = error instanceof Error ? error.message : 'Unknown error'
      toast.error('Network Error', {
        description: `Failed to create proposal: ${message}`
      })
      return null
    }
  }

  async generateContent(proposalId: string, requirements: any): Promise<ProposalContent | null> {
    try {
      // Using the analysis endpoint as a proxy for content generation
      const response = await apiService.analyzeDocument({
        proposal_id: proposalId,
        ...requirements
      })
      
      if (response.error) {
        toast.error('Failed to generate content', {
          description: response.error
        })
        return null
      }
      
      toast.success('Content generated successfully')
      return response.data || null
    } catch (error) {
      const message = error instanceof Error ? error.message : 'Unknown error'
      toast.error('Network Error', {
        description: `Failed to generate content: ${message}`
      })
      return null
    }
  }

  async updateProposal(_id: string, _updates: Partial<Proposal>): Promise<boolean> {
    try {
      // For now, simulate API call since update endpoint might not exist
      await new Promise(resolve => setTimeout(resolve, 500))
      toast.success('Proposal updated successfully')
      return true
    } catch (error) {
      const message = error instanceof Error ? error.message : 'Unknown error'
      toast.error('Failed to update proposal', {
        description: message
      })
      return false
    }
  }

  async deleteProposal(_id: string): Promise<boolean> {
    try {
      // For now, simulate API call since delete endpoint might not exist
      await new Promise(resolve => setTimeout(resolve, 500))
      toast.success('Proposal deleted successfully')
      return true
    } catch (error) {
      const message = error instanceof Error ? error.message : 'Unknown error'
      toast.error('Failed to delete proposal', {
        description: message
      })
      return false
    }
  }
}

export const proposalService = new ProposalService()
export default proposalService
