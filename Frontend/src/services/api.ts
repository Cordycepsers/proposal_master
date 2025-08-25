/**
 * API service for Proposal Master backend integration
 */

const API_BASE_URL = (window as any).__ENV__?.VITE_API_URL || 'http://localhost:8000';

interface ApiResponse<T> {
  data?: T;
  error?: string;
  status: number;
}

class ApiService {
  private baseUrl: string;

  constructor() {
    this.baseUrl = API_BASE_URL;
  }

  private async request<T>(
    endpoint: string,
    options: RequestInit = {}
  ): Promise<ApiResponse<T>> {
    try {
      const url = `${this.baseUrl}${endpoint}`;
      const response = await fetch(url, {
        headers: {
          'Content-Type': 'application/json',
          ...options.headers,
        },
        ...options,
      });

      const data = await response.json();

      if (!response.ok) {
        return {
          error: data.detail || 'An error occurred',
          status: response.status,
        };
      }

      return {
        data,
        status: response.status,
      };
    } catch (error) {
      return {
        error: error instanceof Error ? error.message : 'Network error',
        status: 0,
      };
    }
  }

  // Health check
  async getHealth() {
    return this.request<{
      status: string;
      timestamp: string;
      version: string;
      uptime: string;
      system_info: Record<string, any>;
    }>('/health');
  }

  // System status
  async getSystemStatus() {
    return this.request<{
      cpu_usage: number;
      memory_usage: Record<string, any>;
      disk_usage: Record<string, any>;
      python_version: string;
    }>('/health/status');
  }

  // Documents API
  async getDocuments() {
    return this.request<{
      documents: Array<{
        id: string;
        filename: string;
        original_filename: string;
        file_size: number;
        file_type: string;
        upload_timestamp: string;
        processing_status: string;
        content_preview?: string;
        page_count?: number;
        word_count?: number;
      }>;
      total: number;
    }>('/documents');
  }

  async uploadDocument(file: File) {
    const formData = new FormData();
    formData.append('file', file);

    return this.request<{
      document_id: string;
      filename: string;
      status: string;
      message: string;
    }>('/documents/upload', {
      method: 'POST',
      body: formData,
      headers: {}, // Remove Content-Type to let browser set it for FormData
    });
  }

  async getDocumentStatus(documentId: string) {
    return this.request<{
      document_id: string;
      status: string;
      progress: number;
      result?: any;
      error?: string;
    }>(`/documents/${documentId}/status`);
  }

  // Vector search
  async searchDocuments(query: string, topK: number = 5) {
    return this.request<{
      query: string;
      results: Array<{
        id: string;
        content: string;
        metadata: Record<string, any>;
        similarity_score: number;
      }>;
      total_results: number;
    }>('/vector/search', {
      method: 'POST',
      body: JSON.stringify({ query, top_k: topK }),
    });
  }

  // Analysis API
  async analyzeDocument(documentId: string) {
    return this.request<{
      document_id: string;
      analysis: {
        summary: string;
        key_points: string[];
        requirements: string[];
        risks: string[];
      };
      confidence_score: number;
    }>(`/analysis/analyze/${documentId}`, {
      method: 'POST',
    });
  }

  // Requirements API
  async getRequirements(documentId?: string) {
    const endpoint = documentId 
      ? `/requirements?document_id=${documentId}` 
      : '/requirements';
    
    return this.request<{
      requirements: Array<{
        id: string;
        text: string;
        category: string;
        priority: string;
        document_id: string;
        confidence_score: number;
      }>;
      total: number;
    }>(endpoint);
  }

  // Proposals API
  async getProposals() {
    return this.request<{
      proposals: Array<{
        id: string;
        title: string;
        status: string;
        created_at: string;
        updated_at: string;
        document_id?: string;
        summary?: string;
      }>;
      total: number;
    }>('/proposals');
  }

  async createProposal(data: {
    title: string;
    requirements_ids: string[];
    template?: string;
  }) {
    return this.request<{
      proposal_id: string;
      title: string;
      status: string;
      message: string;
    }>('/proposals', {
      method: 'POST',
      body: JSON.stringify(data),
    });
  }

  // Research API
  async conductResearch(query: string) {
    return this.request<{
      query: string;
      results: Array<{
        title: string;
        content: string;
        source: string;
        url?: string;
        relevance_score: number;
      }>;
      summary: string;
    }>('/research/conduct', {
      method: 'POST',
      body: JSON.stringify({ query }),
    });
  }

  // Feedback API
  async submitFeedback(data: {
    type: string;
    content: string;
    rating?: number;
    metadata?: Record<string, any>;
  }) {
    return this.request<{
      feedback_id: string;
      message: string;
    }>('/feedback', {
      method: 'POST',
      body: JSON.stringify(data),
    });
  }
}

export const apiService = new ApiService();
export default apiService;
