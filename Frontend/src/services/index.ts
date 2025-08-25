// Service layer exports
export { apiService } from './api'
export { proposalService } from './proposalService'
export { documentService } from './documentService'
export { researchService } from './researchService'

// Type exports
export type { Proposal, CreateProposalData, ProposalContent } from './proposalService'
export type { Document, DocumentAnalysis } from './documentService'
export type { ResearchResult, ResearchResponse, FeedbackData, FeedbackResponse } from './researchService'
