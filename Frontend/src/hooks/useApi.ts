import { useState, useEffect } from 'react';
import { apiService } from '../services/api';

export interface Document {
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
}

export interface Proposal {
  id: string;
  title: string;
  status: string;
  created_at: string;
  updated_at: string;
  document_id?: string;
  summary?: string;
}

export interface SystemHealth {
  status: string;
  timestamp: string;
  version: string;
  uptime: string;
  system_info: Record<string, any>;
}

export function useDocuments() {
  const [documents, setDocuments] = useState<Document[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  const fetchDocuments = async () => {
    setLoading(true);
    setError(null);
    
    try {
      const response = await apiService.getDocuments();
      if (response.error) {
        setError(response.error);
      } else if (response.data) {
        setDocuments(response.data.documents);
      }
    } catch (err) {
      setError('Failed to fetch documents');
    } finally {
      setLoading(false);
    }
  };

  const uploadDocument = async (file: File) => {
    const response = await apiService.uploadDocument(file);
    if (response.data) {
      await fetchDocuments(); // Refresh the list
      return response.data;
    }
    throw new Error(response.error || 'Upload failed');
  };

  useEffect(() => {
    fetchDocuments();
  }, []);

  return {
    documents,
    loading,
    error,
    fetchDocuments,
    uploadDocument,
  };
}

export function useProposals() {
  const [proposals, setProposals] = useState<Proposal[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  const fetchProposals = async () => {
    setLoading(true);
    setError(null);
    
    try {
      const response = await apiService.getProposals();
      if (response.error) {
        setError(response.error);
      } else if (response.data) {
        setProposals(response.data.proposals);
      }
    } catch (err) {
      setError('Failed to fetch proposals');
    } finally {
      setLoading(false);
    }
  };

  const createProposal = async (data: {
    title: string;
    requirements_ids: string[];
    template?: string;
  }) => {
    const response = await apiService.createProposal(data);
    if (response.data) {
      await fetchProposals(); // Refresh the list
      return response.data;
    }
    throw new Error(response.error || 'Failed to create proposal');
  };

  useEffect(() => {
    fetchProposals();
  }, []);

  return {
    proposals,
    loading,
    error,
    fetchProposals,
    createProposal,
  };
}

export function useSystemHealth() {
  const [health, setHealth] = useState<SystemHealth | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  const fetchHealth = async () => {
    setLoading(true);
    setError(null);
    
    try {
      const response = await apiService.getHealth();
      if (response.error) {
        setError(response.error);
      } else if (response.data) {
        setHealth(response.data);
      }
    } catch (err) {
      setError('Failed to fetch system health');
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchHealth();
    
    // Refresh health every 30 seconds
    const interval = setInterval(fetchHealth, 30000);
    return () => clearInterval(interval);
  }, []);

  return {
    health,
    loading,
    error,
    fetchHealth,
  };
}

export function useSearch() {
  const [results, setResults] = useState<any[]>([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const search = async (query: string, topK: number = 5) => {
    if (!query.trim()) return;
    
    setLoading(true);
    setError(null);
    
    try {
      const response = await apiService.searchDocuments(query, topK);
      if (response.error) {
        setError(response.error);
      } else if (response.data) {
        setResults(response.data.results);
      }
    } catch (err) {
      setError('Search failed');
    } finally {
      setLoading(false);
    }
  };

  return {
    results,
    loading,
    error,
    search,
  };
}
