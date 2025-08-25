# DocumentAnalyzer Module

The DocumentAnalyzer module provides advanced document analysis capabilities for the Proposal Master system, offering comprehensive content analysis, entity extraction, and theme identification.

## Overview

The DocumentAnalyzer is designed to extract meaningful insights from textual content through multiple analysis techniques including structural analysis, named entity recognition, and thematic analysis. It leverages both rule-based patterns and NLP models for robust content understanding.

## Features

### Document Structure Analysis
- **Content Metrics**: Word count, paragraph count, total length analysis
- **Section Detection**: Automatic identification of document sections and hierarchies
- **Heading Extraction**: Markdown and traditional heading pattern recognition
- **List Analysis**: Detection and counting of bullet points, numbered lists, and lettered lists
- **Table Detection**: Identification of table structures in various formats
- **Readability Assessment**: Flesch Reading Ease score calculation

### Entity Extraction
- **Temporal Entities**: Dates in multiple formats (MM/DD/YYYY, Month DD YYYY, etc.)
- **Financial Information**: Monetary amounts, budgets, costs in various formats
- **Quantitative Data**: Percentages, numerical values with context
- **Contact Information**: Email addresses, phone numbers, URLs
- **Named Entities**: Organizations, persons, locations, products, events (via spaCy)
- **Pattern-Based Extraction**: Regex-based fallback for robust entity detection

### Content Theme Analysis
- **Keyword Analysis**: Top keywords with frequency analysis
- **Technical Term Identification**: Recognition of technical jargon and acronyms
- **Business Term Detection**: Identification of business and commercial terminology
- **Action Item Extraction**: Automatic detection of tasks and action items
- **Requirement Indicators**: Identification of requirement-related phrases and contexts

## Dependencies

### Required
- Python 3.7+
- Standard library: `re`, `collections`, `pathlib`, `logging`

### Optional
- **spaCy**: Enhanced named entity recognition (`python -m spacy download en_core_web_sm`)
- When spaCy is unavailable, falls back to regex-based extraction

## Usage

### Basic Usage

```python
from src.modules.analysis.document_analyzer import DocumentAnalyzer

# Initialize analyzer
analyzer = DocumentAnalyzer()

# Analyze document structure
content = "Your document content here..."
structure = analyzer.analyze_document_structure(content)

# Extract entities
entities = analyzer.extract_key_entities(content)

# Analyze themes
themes = analyzer.analyze_content_themes(content)
```

### Structure Analysis Example

```python
structure = analyzer.analyze_document_structure(document_content)

print(f"Word count: {structure['word_count']}")
print(f"Readability score: {structure['readability_score']:.1f}")
print(f"Sections found: {len(structure['sections'])}")
print(f"Headings: {structure['headings']}")
print(f"Lists: {structure['lists']}")
```

**Output:**
```python
{
    'total_length': 2450,
    'word_count': 425,
    'paragraph_count': 12,
    'sections': [
        {'title': 'Executive Summary', 'line_number': 3, 'type': 'header'},
        {'title': 'Technical Requirements', 'line_number': 15, 'type': 'header'}
    ],
    'headings': ['Project Overview', 'Requirements', 'Timeline'],
    'lists': {'bullet_points': 8, 'numbered_items': 5, 'lettered_items': 0},
    'tables': 2,
    'readability_score': 45.3
}
```

### Entity Extraction Example

```python
entities = analyzer.extract_key_entities(document_content)

for entity_type, values in entities.items():
    if values:
        print(f"{entity_type}: {values}")
```

**Output:**
```python
{
    'dates': ['March 15, 2024', 'Q2 2024', '6 months'],
    'monetary_amounts': ['$150,000', '$50,000'],
    'percentages': ['99.9%', '85%'],
    'organizations': ['Microsoft Corporation', 'API Gateway Inc'],
    'persons': ['John Smith', 'Sarah Johnson'],
    'locations': ['New York', 'California'],
    'email_addresses': ['contact@company.com'],
    'phone_numbers': ['(555) 123-4567'],
    'urls': ['https://www.example.com']
}
```

### Theme Analysis Example

```python
themes = analyzer.analyze_content_themes(document_content)

print(f"Top keywords: {themes['top_keywords'][:5]}")
print(f"Business terms: {themes['business_terms']}")
print(f"Action items: {themes['action_items']}")
```

**Output:**
```python
{
    'top_keywords': [('system', 12), ('requirements', 8), ('project', 6)],
    'technical_terms': ['api', 'authentication', 'database', 'integration'],
    'business_terms': ['contract', 'budget', 'timeline', 'deliverable'],
    'action_items': ['Complete design review by March 1st', 'Finalize budget approval'],
    'requirements_indicators': ['must provide secure authentication', 'shall include logging']
}
```

## Advanced Features

### Custom Analysis Patterns

The DocumentAnalyzer uses sophisticated regex patterns for robust extraction:

#### Date Patterns
- `MM/DD/YYYY` and `MM-DD-YYYY` formats
- `Month DD, YYYY` natural language dates
- `YYYY-MM-DD` ISO format dates
- Relative dates like "6 months", "Q2 2024"

#### Financial Patterns
- Currency amounts: `$1,000.00`, `€500`, `£750`
- Written amounts: `1000 USD`, `500 dollars`
- Range handling: `$10K-$50K`

#### Contact Patterns
- Email validation with domain checking
- Phone formats: `(555) 123-4567`, `555-123-4567`, `555.123.4567`
- URL extraction with protocol detection

### Text Preprocessing

Advanced text preprocessing for theme analysis:
- **Stop Word Removal**: Comprehensive English stop word list
- **Noise Filtering**: Punctuation and special character handling
- **Case Normalization**: Consistent lowercase processing
- **Length Filtering**: Minimum word length requirements

### Readability Assessment

Implements a simplified Flesch Reading Ease formula:
- **Score Range**: 0-100 (higher = more readable)
- **Factors**: Average sentence length, syllable complexity
- **Interpretation**: 
  - 90-100: Very Easy
  - 80-90: Easy
  - 70-80: Fairly Easy
  - 60-70: Standard
  - 50-60: Fairly Difficult
  - 30-50: Difficult
  - 0-30: Very Difficult

## Performance Considerations

### Optimization Features
- **Analysis Caching**: Results cached to avoid reprocessing
- **Lazy Loading**: spaCy model loaded only when available
- **Regex Compilation**: Patterns compiled once for efficiency
- **Memory Management**: Efficient string processing for large documents

### Processing Limits
- **Recommended Maximum**: 10MB text files
- **Performance Sweet Spot**: 1-5MB documents
- **Large Document Handling**: Automatic chunking for very large files

## Error Handling

### Graceful Degradation
- **Missing spaCy**: Falls back to regex-based entity extraction
- **Invalid Input**: Returns empty structures rather than crashing
- **Encoding Issues**: Handles various text encodings automatically
- **Memory Constraints**: Processes large documents in chunks

### Validation
- **Input Validation**: Checks for valid string input
- **Content Sanitization**: Handles special characters and unicode
- **Result Verification**: Ensures consistent output structure

## Integration Points

### With Other Modules
- **DocumentParser**: Provides structured content for analysis
- **RequirementExtractor**: Supplies entity and theme data for requirement identification
- **RiskAssessor**: Offers content insights for risk evaluation
- **ProposalGenerator**: Provides content themes for proposal writing

### Data Flow
```
Raw Document → DocumentParser → DocumentAnalyzer → RequirementExtractor
                                        ↓
                               RiskAssessor ← Content Themes & Entities
```

## Testing

### Comprehensive Test Suite
The module includes extensive tests covering:

```bash
# Run all tests
python -m pytest tests/test_document_analyzer.py -v

# Test specific functionality
python -c "
from src.modules.analysis.document_analyzer import DocumentAnalyzer
analyzer = DocumentAnalyzer()
result = analyzer.analyze_document_structure('Test content...')
print(result)
"
```

### Test Categories
- **Unit Tests**: Individual method testing
- **Integration Tests**: Cross-module functionality
- **Edge Cases**: Empty content, special characters, very large documents
- **Performance Tests**: Speed and memory usage validation

## Configuration

### Default Settings
```python
# Built-in configurations
STOP_WORDS = {'the', 'a', 'an', 'and', 'or', 'but', ...}
MAX_KEYWORDS = 20
MAX_ACTION_ITEMS = 10
MAX_REQUIREMENT_INDICATORS = 15
```

### Customization Options
```python
# Extend business terms
analyzer.business_keywords.extend(['your', 'custom', 'terms'])

# Modify extraction patterns
analyzer.date_patterns.append(r'your_custom_date_pattern')
```

## Implementation Status

✅ **Completed Features:**
- Document structure analysis with comprehensive metrics
- Multi-pattern entity extraction (dates, money, contacts, etc.)
- Advanced theme analysis with keyword frequency
- Business and technical term identification
- Action item and requirement detection
- Readability assessment with Flesch formula
- Robust error handling and graceful degradation
- Comprehensive test coverage

✅ **Production Ready:** Yes, with fallback mechanisms for all dependencies

## Example Use Cases

### 1. RFP Analysis
```python
# Analyze an RFP document
rfp_content = load_rfp_document()
analyzer = DocumentAnalyzer()

# Extract key information
structure = analyzer.analyze_document_structure(rfp_content)
entities = analyzer.extract_key_entities(rfp_content)
themes = analyzer.analyze_content_themes(rfp_content)

# Identify critical elements
budget = entities['monetary_amounts']
deadlines = entities['dates']
requirements = themes['requirements_indicators']
business_focus = themes['business_terms']
```

### 2. Proposal Quality Assessment
```python
# Assess proposal readability and completeness
proposal = load_proposal_document()

structure = analyzer.analyze_document_structure(proposal)
readability = structure['readability_score']

if readability < 30:
    print("Warning: Proposal may be too complex")
elif readability > 80:
    print("Info: Proposal is very readable")
```

### 3. Contract Review
```python
# Extract contract essentials
contract = load_contract_document()
entities = analyzer.extract_key_entities(contract)

key_dates = entities['dates']
amounts = entities['monetary_amounts'] 
contacts = entities['email_addresses'] + entities['phone_numbers']
organizations = entities['organizations']

print(f"Contract involves: {organizations}")
print(f"Key dates: {key_dates}")
print(f"Financial terms: {amounts}")
```

## Future Enhancements

### Planned Features
- **Multi-language Support**: Extended language models
- **Custom Entity Types**: User-defined entity categories
- **Advanced Metrics**: Sentiment analysis, complexity scoring
- **Visual Analysis**: Chart and diagram detection
- **Semantic Similarity**: Content comparison capabilities

### Performance Improvements
- **Parallel Processing**: Multi-threaded analysis for large documents
- **Incremental Analysis**: Update analysis for document changes
- **Memory Optimization**: Streaming processing for very large files
