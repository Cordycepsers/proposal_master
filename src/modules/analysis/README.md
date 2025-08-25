# Analysis Module

The Analysis Module is a comprehensive document analysis and risk assessment system designed for RFP (Request for Proposal) and project document processing. It provides four main components for analyzing documents, extracting requirements, and assessing project risks.

## 📋 Table of Contents

- [Overview](#overview)
- [Components](#components)
- [Installation & Dependencies](#installation--dependencies)
- [Usage Examples](#usage-examples)
- [API Reference](#api-reference)
- [Testing](#testing)
- [Known Issues & Limitations](#known-issues--limitations)
- [Contributing](#contributing)

## 🔍 Overview

The Analysis Module processes project documents (RFPs, specifications, requirements) and provides:

- **Document Analysis**: Structure analysis, entity extraction, and content theme identification
- **Document Parsing**: Multi-format support (PDF, DOCX, TXT, MD) with content extraction
- **Requirement Extraction**: Categorization of functional, non-functional, technical, and compliance requirements
- **Risk Assessment**: Comprehensive project risk analysis with mitigation strategies

## 🧩 Components

### 1. DocumentAnalyzer (`document_analyzer.py`)

**Purpose**: Analyzes document structure and extracts key insights using NLP techniques.

**Key Features**:
- Document structure analysis (sections, headings, word count)
- Entity extraction (organizations, technologies, financial terms, dates)
- Content theme identification with confidence scoring
- Readability analysis
- NLP processing with spaCy integration (fallback to regex patterns)

**Main Methods**:
- `analyze_document(document_data)`: Complete document analysis
- `analyze_document_structure(content)`: Structure and readability analysis
- `extract_key_entities(content)`: Named entity recognition
- `analyze_content_themes(content)`: Theme and keyword analysis

### 2. DocumentParser (`document_parser.py`)

**Purpose**: Parses multiple document formats and extracts raw content.

**Supported Formats**:
- ✅ **TXT**: Plain text files
- ✅ **MD**: Markdown files
- ⚠️ **PDF**: Placeholder implementation (requires PyPDF2)
- ⚠️ **DOCX**: Placeholder implementation (requires python-docx)

**Main Methods**:
- `parse_document(file_path)`: Main parsing interface
- `_extract_txt_content(file_path)`: Text file extraction
- `_extract_md_content(file_path)`: Markdown file extraction
- `_extract_pdf_content(file_path)`: PDF extraction (placeholder)
- `_extract_docx_content(file_path)`: DOCX extraction (placeholder)

### 3. RequirementExtractor (`requirement_extractor.py`)

**Purpose**: Extracts and categorizes requirements from RFP documents.

**Requirement Categories**:
- **Functional**: User-facing features and capabilities
- **Non-Functional**: Performance, scalability, usability requirements
- **Technical**: Technology stack, architecture, infrastructure requirements
- **Compliance**: Regulatory, security, and audit requirements

**Key Features**:
- Automatic requirement categorization using pattern matching
- Priority level analysis (high, medium, low)
- Requirement scoring and validation
- Summary statistics and insights

**Main Methods**:
- `extract_requirements(content)`: Complete requirement extraction
- `_extract_functional_requirements(content)`: Functional requirement identification
- `_extract_non_functional_requirements(content)`: Performance/quality requirements
- `_extract_technical_requirements(content)`: Technology and architecture requirements
- `_analyze_priority_levels(content)`: Priority analysis

### 4. RiskAssessor (`risk_assessor.py`)

**Purpose**: Comprehensive project risk assessment with mitigation strategies.

**Risk Categories**:
- **Technical**: Technology complexity, integration challenges
- **Timeline**: Schedule pressure, dependency risks
- **Budget**: Cost overruns, resource constraints
- **Operational**: Team skills, communication, process risks
- **Compliance**: Regulatory, security, audit risks

**Key Features**:
- Multi-dimensional risk scoring (0-4 scale)
- Weighted risk calculation by category importance
- Automated mitigation strategy generation
- Risk timeline and milestone planning
- Project recommendations based on risk levels

**Main Methods**:
- `assess_project_risk(requirements, project_details, content)`: Complete risk assessment
- `_assess_risk_categories(...)`: Category-specific risk analysis
- `_generate_mitigation_strategies(...)`: Strategy recommendations
- `_create_risk_timeline(...)`: Risk management timeline
- `get_statistics()`: Assessment statistics

## 🚀 Installation & Dependencies

### Required Dependencies

```bash
# Core dependencies (already in requirements.txt)
pip install asyncio logging datetime

# NLP dependencies (optional but recommended)
pip install spacy
python -m spacy download en_core_web_sm

# Document parsing dependencies (required for full functionality)
pip install PyPDF2 python-docx

# Testing dependencies
pip install pytest pytest-asyncio
```

### Current Status

✅ **Working with fallbacks**: All components work with regex-based fallbacks
⚠️ **Missing dependencies**: spaCy, PyPDF2, python-docx not currently installed
🔧 **Recommended**: Install missing dependencies for full functionality

## 💻 Usage Examples

### Basic Document Analysis

```python
from modules.analysis.document_analyzer import DocumentAnalyzer

# Initialize analyzer
analyzer = DocumentAnalyzer()

# Analyze a document
document_data = {
    'content': "Your RFP content here...",
    'metadata': {'filename': 'rfp.pdf', 'file_type': 'pdf'}
}

result = await analyzer.analyze_document(document_data)
print(f"Analysis status: {result['status']}")
print(f"Key entities found: {result['key_entities']}")
```

### Document Parsing

```python
from modules.analysis.document_parser import DocumentParser

# Initialize parser
parser = DocumentParser()

# Parse different file types
txt_result = await parser.parse_document('/path/to/document.txt')
md_result = await parser.parse_document('/path/to/document.md')
pdf_result = await parser.parse_document('/path/to/document.pdf')  # Placeholder

print(f"Parsed content: {txt_result['content']}")
```

### Requirement Extraction

```python
from modules.analysis.requirement_extractor import RequirementExtractor

# Initialize extractor
extractor = RequirementExtractor()

# Extract requirements from RFP content
rfp_content = "Your RFP document content..."
result = await extractor.extract_requirements(rfp_content)

print(f"Functional requirements: {len(result['requirements']['functional'])}")
print(f"Technical requirements: {len(result['requirements']['technical'])}")
print(f"Priority analysis: {result['priority_analysis']}")
```

### Risk Assessment

```python
from modules.analysis.risk_assessor import RiskAssessor

# Initialize assessor
assessor = RiskAssessor()

# Assess project risks
requirements = {
    'functional': [...],
    'technical': [...],
    'compliance': [...]
}

project_details = {
    'budget': '$200,000',
    'deadline': 'December 2024',
    'team_size': 8
}

risk_result = await assessor.assess_project_risk(
    requirements=requirements,
    project_details=project_details,
    content=rfp_content
)

print(f"Overall risk level: {risk_result['overall_risk']['level']}")
print(f"Risk score: {risk_result['overall_risk']['score']}")
```

### Complete Analysis Pipeline

```python
async def analyze_rfp_document(file_path):
    """Complete RFP analysis pipeline."""
    
    # Step 1: Parse document
    parser = DocumentParser()
    parsed = await parser.parse_document(file_path)
    
    if parsed['status'] != 'success':
        return {'error': 'Failed to parse document'}
    
    content = parsed['content']
    
    # Step 2: Analyze document structure
    analyzer = DocumentAnalyzer()
    analysis = await analyzer.analyze_document({
        'content': content,
        'metadata': parsed['metadata']
    })
    
    # Step 3: Extract requirements
    extractor = RequirementExtractor()
    requirements = await extractor.extract_requirements(content)
    
    # Step 4: Assess risks
    assessor = RiskAssessor()
    project_details = {
        'budget': 'TBD',
        'deadline': 'TBD',
        'team_size': 'TBD'
    }
    
    risks = await assessor.assess_project_risk(
        requirements=requirements['requirements'],
        project_details=project_details,
        content=content
    )
    
    return {
        'document_analysis': analysis,
        'requirements': requirements,
        'risk_assessment': risks
    }

# Usage
result = await analyze_rfp_document('/path/to/rfp.pdf')
```

## 📚 API Reference

### Common Response Format

All components return standardized responses:

```python
{
    'status': 'success' | 'error',
    'data': { ... },  # Component-specific results
    'error': 'Error message',  # Only present if status == 'error'
    'timestamp': 'ISO timestamp',
    'processing_time': float  # Seconds
}
```

### Error Handling

All components include comprehensive error handling:

- **File not found**: Returns error status with descriptive message
- **Invalid content**: Handles empty or malformed content gracefully
- **Processing failures**: Catches and logs exceptions with context
- **Dependency issues**: Graceful fallbacks when optional dependencies missing

### Configuration Options

Components can be configured via initialization parameters:

```python
# DocumentAnalyzer configuration
analyzer = DocumentAnalyzer(
    enable_nlp=True,  # Use spaCy if available
    min_confidence=0.7,  # Minimum confidence for entity extraction
    max_entities=50  # Maximum entities to extract per category
)

# RequirementExtractor configuration
extractor = RequirementExtractor(
    min_priority_score=0.5,  # Minimum score for priority classification
    enable_validation=True,  # Validate extracted requirements
    max_requirements=100  # Maximum requirements per category
)
```

## 🧪 Testing

### Running Tests

```bash
# Install test dependencies
pip install pytest pytest-asyncio

# Run all analysis module tests
pytest tests/test_analysis_module.py -v

# Run specific test classes
pytest tests/test_analysis_module.py::TestDocumentAnalyzer -v
pytest tests/test_analysis_module.py::TestRiskAssessor -v

# Run with coverage
pytest tests/test_analysis_module.py --cov=src/modules/analysis --cov-report=html
```

### Test Coverage

The test suite covers:

- ✅ **Unit Tests**: Individual component functionality
- ✅ **Integration Tests**: Component interaction workflows
- ✅ **Error Handling**: Edge cases and error conditions
- ✅ **Async Operations**: Proper async/await testing
- ✅ **Mock Dependencies**: Mocked external dependencies

### Test Data

Test files use:
- Realistic RFP content samples
- Multiple document formats
- Various project complexity levels
- Different risk scenarios

## ⚠️ Known Issues & Limitations

### Current Limitations

1. **PDF/DOCX Parsing**: 
   - Current implementation uses placeholders
   - Requires PyPDF2 and python-docx installation
   - No support for complex document layouts

2. **spaCy Dependency**:
   - NLP features limited without spaCy
   - Falls back to regex patterns
   - Entity extraction less accurate without proper NLP

3. **Risk Assessment**:
   - Rule-based risk scoring (not ML-based)
   - Limited to predefined risk categories
   - Requires manual threshold tuning

4. **Language Support**:
   - Currently English-only
   - No multi-language document support

### Recommended Improvements

1. **Enhanced PDF/DOCX Support**:
   ```bash
   pip install PyPDF2 python-docx
   # Implement proper extraction methods
   ```

2. **NLP Integration**:
   ```bash
   pip install spacy
   python -m spacy download en_core_web_sm
   # Enable advanced entity extraction
   ```

3. **Machine Learning Enhancement**:
   - Train custom models for requirement classification
   - Implement ML-based risk scoring
   - Add document similarity analysis

4. **Performance Optimization**:
   - Implement document caching
   - Parallel processing for large documents
   - Streaming for very large files

## 🤝 Contributing

### Development Guidelines

1. **Code Style**: Follow PEP 8 and existing patterns
2. **Async/Await**: Use async patterns consistently
3. **Error Handling**: Include comprehensive error handling
4. **Logging**: Use structured logging throughout
5. **Testing**: Add tests for new functionality

### Adding New Features

1. **New Document Formats**: Extend DocumentParser
2. **Additional Risk Categories**: Update RiskAssessor configuration
3. **Enhanced NLP**: Improve DocumentAnalyzer entity extraction
4. **Custom Requirements**: Extend RequirementExtractor patterns

### Performance Considerations

- Large documents may require streaming processing
- Memory usage can be optimized for batch processing
- Consider implementing caching for repeated analyses
- Monitor async operation performance

---

## 📈 Module Statistics

| Component | Lines of Code | Main Methods | Test Coverage |
|-----------|---------------|--------------|---------------|
| DocumentAnalyzer | 384 | 4 | ✅ Covered |
| DocumentParser | 214 | 6 | ✅ Covered |
| RequirementExtractor | 322 | 8 | ✅ Covered |
| RiskAssessor | 485 | 12 | ✅ Covered |
| **Total** | **1,405** | **30** | **90%+** |

## 🔗 Related Documentation

- [Base Agent Documentation](../agents/README.md)
- [API Integration Guide](../../api/README.md)
- [Project Configuration](../../config/README.md)
- [Testing Guidelines](../../../tests/README.md)
