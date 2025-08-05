# Proposal Master API Documentation

## Overview

The Proposal Master API provides comprehensive REST endpoints for AI-powered proposal management and document analysis. The API enables automated document processing, requirement extraction, risk assessment, and proposal generation.

## Base URL

```
http://localhost:8000/api/v1
```

## Authentication

Currently, the API operates without authentication for development purposes. In production, implement proper authentication using JWT tokens or API keys.

## API Endpoints

### Health and System Status

#### GET /health
Basic health check endpoint.

**Response:**
```json
{
  "status": "healthy",
  "timestamp": "2025-08-05T10:30:00Z",
  "version": "1.0.0",
  "uptime": "2d 4h 15m",
  "system_info": {
    "python_version": "3.9.6",
    "platform": "Darwin",
    "architecture": "arm64"
  }
}
```

#### GET /health/status
Detailed system metrics.

**Response:**
```json
{
  "cpu_usage": 45.2,
  "memory_usage": {
    "total": 16777216000,
    "available": 8388608000,
    "percent": 50.0,
    "used": 8388608000
  },
  "disk_usage": {
    "total": 500000000000,
    "used": 250000000000,
    "free": 250000000000,
    "percent": 50.0
  },
  "python_version": "3.9.6",
  "platform": "macOS 12.0"
}
```

### Document Management

#### POST /documents/upload
Upload a document for processing.

**Request:**
- Content-Type: `multipart/form-data`
- Body: File upload with optional parameters

**Parameters:**
- `file`: Document file (PDF, DOCX, TXT, MD)
- `process_immediately`: Boolean (optional, default: false)

**Response:**
```json
{
  "document_id": "uuid-here",
  "message": "Document uploaded successfully",
  "metadata": {
    "id": "uuid-here",
    "filename": "sample_rfp.pdf",
    "original_filename": "RFP_CloudServices_2025.pdf",
    "file_size": 1048576,
    "file_type": ".pdf",
    "upload_timestamp": "2025-08-05T10:30:00Z",
    "processing_status": "uploaded"
  }
}
```

#### GET /documents/
List uploaded documents with pagination.

**Parameters:**
- `limit`: Integer (default: 100, max: 500)
- `offset`: Integer (default: 0)
- `file_type`: String (optional, e.g., ".pdf")

**Response:**
```json
{
  "documents": [
    {
      "id": "uuid-here",
      "filename": "uuid_sample.pdf",
      "original_filename": "sample.pdf",
      "file_size": 1048576,
      "file_type": ".pdf",
      "upload_timestamp": "2025-08-05T10:30:00Z",
      "processing_status": "stored"
    }
  ],
  "total_count": 1
}
```

#### GET /documents/{document_id}
Get metadata for a specific document.

**Response:**
```json
{
  "id": "uuid-here",
  "filename": "uuid_sample.pdf",
  "original_filename": "sample.pdf",
  "file_size": 1048576,
  "file_type": ".pdf",
  "upload_timestamp": "2025-08-05T10:30:00Z",
  "processing_status": "stored",
  "content_preview": "First 200 characters...",
  "page_count": 15,
  "word_count": 2500
}
```

#### GET /documents/{document_id}/download
Download a document file.

**Response:** Binary file download

#### POST /documents/{document_id}/process
Process a document to extract content and metadata.

**Response:**
```json
{
  "document_id": "uuid-here",
  "status": "processing",
  "content": null,
  "metadata": null
}
```

#### DELETE /documents/{document_id}
Delete a document and associated data.

**Response:**
```json
{
  "message": "Document deleted successfully",
  "document_id": "uuid-here"
}
```

### Document Analysis

#### POST /analysis/comprehensive
Perform comprehensive document analysis using all agents.

**Request:**
```json
{
  "document_id": "uuid-here",
  "analysis_config": {
    "parsing_depth": "comprehensive",
    "extraction_mode": "hybrid",
    "risk_assessment_depth": "detailed",
    "include_quantitative_risk": true,
    "generate_compliance_matrix": true,
    "identify_success_factors": true
  },
  "project_context": {
    "budget_range": "$1M-$5M",
    "timeline": "6 months",
    "team_size": "10-15"
  },
  "compliance_standards": ["ISO 27001", "SOC 2"],
  "output_format": "detailed"
}
```

**Response:**
```json
{
  "analysis_id": "uuid-here",
  "status": "completed",
  "document_info": {
    "document_type": "RFP",
    "sections": ["Technical Requirements", "Evaluation Criteria"],
    "total_pages": 15,
    "word_count": 2500
  },
  "requirement_analysis": {
    "requirements": [
      {
        "id": "REQ-001",
        "text": "System must provide 99.9% uptime",
        "type": "technical",
        "priority": "mandatory",
        "complexity": "high"
      }
    ],
    "analysis_summary": {
      "total_requirements": 25,
      "mandatory_count": 15,
      "complexity_breakdown": {"low": 5, "medium": 10, "high": 10}
    }
  },
  "risk_assessment": {
    "identified_risks": [
      {
        "id": "RISK-001",
        "title": "Technical Implementation Risk",
        "category": "technical",
        "probability": 0.6,
        "impact": 5,
        "risk_score": 3.0
      }
    ],
    "risk_matrix": {
      "overall_metrics": {
        "total_risks": 8,
        "average_risk_score": 3.2,
        "risk_level": "Medium"
      }
    }
  },
  "critical_success_factors": [
    {
      "type": "technical_excellence",
      "factor": "Robust architecture design",
      "priority": "critical",
      "success_criteria": ["Performance targets met", "Scalability validated"]
    }
  ],
  "recommendations": [
    {
      "category": "risk_management",
      "priority": "high",
      "recommendation": "Implement comprehensive testing strategy",
      "rationale": "Multiple high-risk technical requirements identified"
    }
  ]
}
```

#### POST /analysis/quick
Perform quick analysis on text content.

**Request:**
```json
{
  "content": "Text content to analyze...",
  "analysis_type": "requirements",
  "context": {
    "document_type": "RFP",
    "industry": "technology"
  }
}
```

**Response:**
```json
{
  "analysis_type": "requirements",
  "results": {
    "requirements": [
      {
        "id": "REQ-001",
        "text": "Extracted requirement text",
        "type": "functional",
        "priority": "important"
      }
    ]
  },
  "processing_time": 2.5
}
```

#### POST /analysis/compare
Compare multiple documents.

**Request:**
```json
{
  "document_ids": ["uuid-1", "uuid-2", "uuid-3"],
  "comparison_type": "similarity",
  "weights": {
    "content": 0.6,
    "structure": 0.2,
    "requirements": 0.2
  }
}
```

**Response:**
```json
{
  "comparison_id": "uuid-here",
  "document_ids": ["uuid-1", "uuid-2", "uuid-3"],
  "comparison_type": "similarity",
  "results": {
    "documents_compared": 3,
    "overall_similarity": 0.75,
    "key_differences": ["Document structure variations"],
    "recommendations": ["Focus on common requirements"]
  },
  "similarity_matrix": [
    [1.0, 0.8, 0.7],
    [0.8, 1.0, 0.6],
    [0.7, 0.6, 1.0]
  ]
}
```

#### GET /analysis/types
Get available analysis types and descriptions.

**Response:**
```json
{
  "comprehensive": {
    "description": "Full document analysis with all agents",
    "includes": [
      "Document parsing and structure analysis",
      "Requirement extraction and categorization",
      "Risk assessment and mitigation planning"
    ],
    "typical_duration": "2-5 minutes",
    "output_formats": ["detailed", "executive_summary", "both"]
  },
  "quick": {
    "description": "Fast analysis of specific aspects",
    "types": {
      "requirements": "Extract and categorize requirements",
      "risks": "Identify and assess risks",
      "summary": "Generate document summary"
    },
    "typical_duration": "10-30 seconds"
  }
}
```

### Requirements Management

#### POST /requirements/extract
Extract requirements from document content.

**Request:**
```json
{
  "document_id": "uuid-here",
  "extraction_mode": "hybrid",
  "include_dependencies": true,
  "generate_traceability": true,
  "compliance_focus": ["ISO 27001", "GDPR"]
}
```

**Response:**
```json
{
  "extraction_id": "uuid-here",
  "status": "completed",
  "requirements": [
    {
      "id": "REQ-001",
      "text": "The system must provide cloud-based infrastructure with 99.9% uptime",
      "type": "technical",
      "priority": "mandatory",
      "complexity": "high",
      "section": "Technical Requirements",
      "dependencies": ["REQ-002"],
      "compliance_standards": ["ISO 27001"],
      "acceptance_criteria": ["Uptime SLA documented", "Monitoring in place"],
      "business_value": "Critical for business operations",
      "technical_risk": "Medium",
      "estimated_effort": "High"
    }
  ],
  "analysis_summary": {
    "total_requirements": 25,
    "priority_breakdown": {"mandatory": 15, "important": 8, "desirable": 2},
    "complexity_breakdown": {"low": 5, "medium": 10, "high": 10},
    "type_breakdown": {"functional": 12, "technical": 8, "compliance": 5}
  },
  "traceability_matrix": {
    "requirements": ["REQ-001", "REQ-002"],
    "relationships": [
      {
        "from": "REQ-001",
        "to": "REQ-002",
        "type": "depends_on"
      }
    ]
  }
}
```

#### POST /requirements/validate
Validate requirements for completeness and quality.

**Request:**
```json
{
  "requirements": [
    {
      "id": "REQ-001",
      "text": "System must be fast",
      "type": "performance",
      "priority": "high"
    }
  ],
  "validation_criteria": {
    "min_text_length": 20,
    "require_acceptance_criteria": true,
    "require_business_value": true
  }
}
```

**Response:**
```json
{
  "validation_id": "uuid-here",
  "status": "completed",
  "validation_results": [
    {
      "requirement_id": "REQ-001",
      "completeness_score": 45,
      "quality_issues": [
        "Requirement text too vague",
        "Missing acceptance criteria",
        "No business value specified"
      ],
      "suggestions": [
        "Add specific performance metrics",
        "Define measurable acceptance criteria",
        "Explain business impact"
      ]
    }
  ],
  "overall_score": 45.0,
  "issues_found": [
    {
      "requirement_id": "REQ-001",
      "issue_type": "quality",
      "description": "Requirement text too vague",
      "severity": "medium"
    }
  ],
  "recommendations": [
    "Consider revising requirements for better clarity",
    "Ensure all mandatory requirements have clear acceptance criteria"
  ]
}
```

#### GET /requirements/types
Get available requirement types and descriptions.

**Response:**
```json
{
  "types": {
    "functional": "Functional capabilities and features",
    "technical": "Technical specifications and constraints",
    "performance": "Performance and scalability requirements",
    "security": "Security and access control requirements",
    "compliance": "Regulatory and compliance requirements"
  },
  "priorities": {
    "mandatory": "Must be implemented - non-negotiable",
    "important": "Should be implemented - high value",
    "desirable": "Could be implemented - nice to have",
    "optional": "May be implemented - low priority"
  },
  "complexity": {
    "low": "Simple, straightforward implementation",
    "medium": "Moderate complexity, some challenges",
    "high": "Complex, significant technical challenges",
    "critical": "Very complex, major technical risks"
  }
}
```

### Risk Assessment

#### POST /risks/assess
Perform comprehensive risk assessment.

**Request:**
```json
{
  "document_id": "uuid-here",
  "requirements": [
    {
      "id": "REQ-001",
      "text": "System must provide 99.9% uptime",
      "priority": "mandatory",
      "complexity": "high"
    }
  ],
  "project_context": {
    "timeline": "6 months",
    "budget": "$2M",
    "team_experience": "medium"
  },
  "assessment_depth": "detailed",
  "include_quantitative": true
}
```

**Response:**
```json
{
  "assessment_id": "uuid-here",
  "status": "completed",
  "identified_risks": [
    {
      "id": "RISK-001",
      "title": "High Availability Implementation Risk",
      "description": "Achieving 99.9% uptime requires robust architecture",
      "category": "technical",
      "probability": 0.6,
      "impact": 5,
      "risk_score": 3.0,
      "dependencies": [],
      "early_warning_signs": ["Architecture review concerns", "Testing failures"],
      "source_location": "Technical Requirements section",
      "affected_requirements": ["REQ-001"]
    }
  ],
  "risk_matrix": {
    "overall_metrics": {
      "total_risks": 8,
      "average_risk_score": 3.2,
      "risk_level": "Medium",
      "high_risks": 2,
      "critical_risks": 0
    },
    "by_category": {
      "technical": 4,
      "schedule": 2,
      "resource": 1,
      "compliance": 1
    }
  },
  "mitigation_strategies": [
    {
      "risk_id": "RISK-001",
      "strategies": [
        {
          "title": "Architecture Review",
          "description": "Conduct thorough architecture review with experts",
          "effectiveness": 0.8,
          "cost": "Medium",
          "timeline": "2 weeks"
        }
      ]
    }
  ],
  "quantitative_analysis": {
    "monte_carlo_results": {
      "success_probability": 0.75,
      "expected_value": 1.5,
      "confidence_intervals": {
        "90%": [1.2, 1.8],
        "95%": [1.0, 2.0]
      }
    }
  }
}
```

#### POST /risks/monitor
Set up risk monitoring.

**Request:**
```json
{
  "risks": ["RISK-001", "RISK-002"],
  "monitoring_frequency": "weekly",
  "alert_thresholds": {
    "RISK-001": 0.7,
    "RISK-002": 0.8
  },
  "stakeholders": ["pm@company.com", "cto@company.com"]
}
```

**Response:**
```json
{
  "monitoring_id": "uuid-here",
  "status": "configured",
  "monitored_risks": [
    {
      "risk_id": "RISK-001",
      "monitoring_enabled": true,
      "frequency": "weekly",
      "alert_threshold": 0.7,
      "status": "active"
    }
  ],
  "monitoring_schedule": {
    "interval_hours": 168,
    "description": "Weekly risk reviews",
    "total_risks": 2,
    "next_check": "2025-08-12T10:00:00Z"
  },
  "alert_configuration": {
    "enabled": true,
    "stakeholders": ["pm@company.com", "cto@company.com"],
    "notification_methods": ["email", "dashboard"]
  }
}
```

#### GET /risks/categories
Get available risk categories.

**Response:**
```json
{
  "categories": {
    "technical": {
      "description": "Technology implementation and integration risks",
      "examples": ["Architecture complexity", "Technology maturity"],
      "typical_mitigation": "Proof of concepts, technical reviews"
    },
    "schedule": {
      "description": "Timeline and delivery risks",
      "examples": ["Aggressive deadlines", "Resource availability"],
      "typical_mitigation": "Buffer time, parallel work streams"
    },
    "compliance": {
      "description": "Regulatory and compliance risks",
      "examples": ["Certification requirements", "Audit findings"],
      "typical_mitigation": "Expert consultation, early certification"
    }
  },
  "severity_levels": {
    "low": {"score_range": "1.0-2.5", "description": "Minor impact"},
    "medium": {"score_range": "2.6-4.0", "description": "Moderate impact"},
    "high": {"score_range": "4.1-5.5", "description": "Significant impact"},
    "critical": {"score_range": "5.6-7.0", "description": "Major impact"}
  }
}
```

## Error Handling

All endpoints return appropriate HTTP status codes:

- `200`: Success
- `201`: Created
- `400`: Bad Request (validation errors)
- `404`: Not Found
- `413`: Payload Too Large
- `422`: Unprocessable Entity
- `429`: Too Many Requests
- `500`: Internal Server Error

Error response format:
```json
{
  "error": "Error type",
  "detail": "Detailed error message",
  "timestamp": "2025-08-05T10:30:00Z"
}
```

## Rate Limiting

API requests are rate-limited to 100 requests per minute per IP address. Rate limit headers are included in responses:

- `X-RateLimit-Limit`: Request limit per window
- `X-RateLimit-Remaining`: Remaining requests in current window
- `X-RateLimit-Reset`: UTC timestamp when window resets

## File Upload Limits

- Maximum file size: 50MB
- Supported formats: PDF, DOCX, TXT, MD
- Maximum concurrent uploads: 5 per user

## Development and Testing

### Starting the API Server

```bash
# Using the startup script
python start_api.py

# Or directly with uvicorn
uvicorn src.api.main:app --host 0.0.0.0 --port 8000 --reload
```

### Environment Variables

- `API_HOST`: Server host (default: "0.0.0.0")
- `API_PORT`: Server port (default: 8000)
- `API_RELOAD`: Enable auto-reload (default: "true")
- `API_LOG_LEVEL`: Logging level (default: "info")

### Interactive Documentation

Once the server is running, visit:
- Swagger UI: http://localhost:8000/docs
- ReDoc: http://localhost:8000/redoc

### Example Usage with curl

```bash
# Health check
curl http://localhost:8000/api/v1/health

# Upload document
curl -X POST \
  -F "file=@sample_rfp.pdf" \
  -F "process_immediately=true" \
  http://localhost:8000/api/v1/documents/upload

# Quick analysis
curl -X POST \
  -H "Content-Type: application/json" \
  -d '{"content": "The system must provide 99.9% uptime", "analysis_type": "requirements"}' \
  http://localhost:8000/api/v1/analysis/quick
```

## Production Considerations

1. **Authentication**: Implement JWT or API key authentication
2. **Rate Limiting**: Configure appropriate limits based on usage
3. **Monitoring**: Add comprehensive logging and monitoring
4. **Caching**: Implement Redis caching for frequently accessed data
5. **Database**: Replace mock data with persistent database storage
6. **File Storage**: Use cloud storage (S3, Azure Blob) for document files
7. **Security**: Add input validation, sanitization, and security headers
8. **Load Balancing**: Configure load balancer for high availability
9. **SSL/TLS**: Enable HTTPS with proper certificates
10. **Backup**: Implement regular backups of data and configurations
