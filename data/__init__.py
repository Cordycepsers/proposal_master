"""
Proposal Master System Data Directory

This directory contains the data storage structure for the Proposal Master system.

Directory Structure:
- embeddings/: Vector embeddings and RAG indices
- documents/: Document collections organized by type
  - rfp_samples/: Sample RFP documents for analysis
  - case_studies/: Successful proposal case studies
  - industry_reports/: Industry knowledge and reports
  - templates/: Proposal and document templates
- cache/: Temporary files and processing cache

Usage Notes:
- The RAG system will automatically create embeddings in the embeddings/ folder
- Documents should be organized by type for better retrieval performance
- Templates support dynamic content generation
- Cache files are automatically managed by the system
"""
