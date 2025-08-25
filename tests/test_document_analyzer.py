"""
Test suite for DocumentAnalyzer module.
"""

import pytest
from src.modules.analysis.document_analyzer import DocumentAnalyzer


class TestDocumentAnalyzer:
    """Test cases for DocumentAnalyzer class."""
    
    @pytest.fixture
    def analyzer(self):
        """Create a DocumentAnalyzer instance for testing."""
        return DocumentAnalyzer()
    
    @pytest.fixture
    def sample_content(self):
        """Sample document content for testing."""
        return """
        # Project Requirements Document
        
        ## 1. Executive Summary
        This project must deliver a comprehensive solution that will provide advanced analytics capabilities.
        
        The client needs to have:
        - Real-time data processing
        - User-friendly dashboard  
        - Secure authentication system
        
        ## 2. Technical Specifications
        The system should include the following components:
        - Backend API (Python/FastAPI)
        - Frontend (React)
        - Database (PostgreSQL)
        
        Budget: $150,000
        Timeline: 6 months
        Contact: john.doe@company.com
        Phone: (555) 123-4567
        Website: https://www.example.com
        
        Action item: Complete technical review by March 15, 2024
        
        ## 3. Requirements
        The system must have 99.9% uptime and shall provide comprehensive logging.
        The solution will deliver real-time monitoring capabilities.
        """
    
    def test_initialization(self, analyzer):
        """Test DocumentAnalyzer initialization."""
        assert hasattr(analyzer, 'analysis_cache')
        assert isinstance(analyzer.analysis_cache, dict)
        # spaCy model may or may not be loaded depending on environment
    
    def test_analyze_document_structure_basic(self, analyzer, sample_content):
        """Test basic document structure analysis."""
        structure = analyzer.analyze_document_structure(sample_content)
        
        # Check required fields
        assert 'total_length' in structure
        assert 'word_count' in structure
        assert 'paragraph_count' in structure
        assert 'sections' in structure
        assert 'headings' in structure
        assert 'lists' in structure
        assert 'tables' in structure
        assert 'readability_score' in structure
        
        # Check basic metrics
        assert structure['word_count'] > 0
        assert structure['total_length'] > structure['word_count']
        assert structure['paragraph_count'] > 0
        assert len(structure['headings']) > 0
        assert isinstance(structure['readability_score'], (int, float))
    
    def test_analyze_document_structure_empty_content(self, analyzer):
        """Test structure analysis with empty content."""
        structure = analyzer.analyze_document_structure("")
        
        assert structure['total_length'] == 0
        assert structure['word_count'] == 0
        assert structure['paragraph_count'] == 0
        assert structure['readability_score'] == 0.0
    
    def test_extract_key_entities(self, analyzer, sample_content):
        """Test entity extraction functionality."""
        entities = analyzer.extract_key_entities(sample_content)
        
        # Check entity categories exist
        expected_categories = [
            'dates', 'monetary_amounts', 'percentages', 'organizations',
            'persons', 'locations', 'products', 'events', 'email_addresses',
            'phone_numbers', 'urls'
        ]
        
        for category in expected_categories:
            assert category in entities
            assert isinstance(entities[category], list)
        
        # Check specific extractions
        assert len(entities['email_addresses']) > 0
        assert 'john.doe@company.com' in entities['email_addresses']
        
        assert len(entities['phone_numbers']) > 0
        assert any('555' in phone for phone in entities['phone_numbers'])
        
        assert len(entities['urls']) > 0
        assert any('example.com' in url for url in entities['urls'])
        
        assert len(entities['percentages']) > 0
        assert '99.9%' in entities['percentages']
    
    def test_extract_key_entities_empty_content(self, analyzer):
        """Test entity extraction with empty content."""
        entities = analyzer.extract_key_entities("")
        
        for category in entities:
            assert entities[category] == []
    
    def test_analyze_content_themes(self, analyzer, sample_content):
        """Test content theme analysis."""
        themes = analyzer.analyze_content_themes(sample_content)
        
        # Check required fields
        assert 'top_keywords' in themes
        assert 'technical_terms' in themes
        assert 'business_terms' in themes
        assert 'action_items' in themes
        assert 'requirements_indicators' in themes
        
        # Check data types
        assert isinstance(themes['top_keywords'], list)
        assert isinstance(themes['technical_terms'], list)
        assert isinstance(themes['business_terms'], list)
        assert isinstance(themes['action_items'], list)
        assert isinstance(themes['requirements_indicators'], list)
        
        # Check keyword structure (should be tuples of word, count)
        if themes['top_keywords']:
            assert isinstance(themes['top_keywords'][0], tuple)
            assert len(themes['top_keywords'][0]) == 2
    
    def test_identify_sections(self, analyzer):
        """Test section identification."""
        content = """
        EXECUTIVE SUMMARY
        
        1. Introduction
        This is the introduction section.
        
        2. Technical Details:
        Technical information here.
        
        PROJECT OVERVIEW:
        Overview content.
        """
        
        sections = analyzer._identify_sections(content)
        
        assert len(sections) > 0
        assert all('title' in section for section in sections)
        assert all('line_number' in section for section in sections)
        assert all('type' in section for section in sections)
    
    def test_extract_headings(self, analyzer):
        """Test heading extraction."""
        content = """
        # Main Heading
        
        ## Sub Heading
        
        ### Another Heading
        
        Regular Heading
        ===============
        
        Another Regular Heading
        -----------------------
        """
        
        headings = analyzer._extract_headings(content)
        
        assert len(headings) > 0
        assert 'Main Heading' in headings
        assert 'Sub Heading' in headings
        assert 'Regular Heading' in headings
    
    def test_extract_lists(self, analyzer):
        """Test list extraction."""
        content = """
        • Bullet point 1
        • Bullet point 2
        - Another bullet
        * Yet another bullet
        
        1. Numbered item 1
        2. Numbered item 2
        3. Numbered item 3
        
        a) Lettered item 1
        b) Lettered item 2
        """
        
        lists = analyzer._extract_lists(content)
        
        assert 'bullet_points' in lists
        assert 'numbered_items' in lists
        assert 'lettered_items' in lists
        
        assert lists['bullet_points'] > 0
        assert lists['numbered_items'] > 0
        assert lists['lettered_items'] > 0
    
    def test_calculate_readability(self, analyzer):
        """Test readability calculation."""
        # Simple text
        simple_text = "This is a simple text. It has short words. Easy to read."
        simple_score = analyzer._calculate_readability(simple_text)
        
        # Complex text
        complex_text = """
        The implementation of sophisticated methodologies necessitates comprehensive 
        consideration of multifaceted interdisciplinary approaches that demonstrate 
        substantial technological advancement capabilities.
        """
        complex_score = analyzer._calculate_readability(complex_text)
        
        # Simple text should have higher readability score
        assert simple_score > complex_score
        assert 0 <= simple_score <= 100
        assert 0 <= complex_score <= 100
    
    def test_count_syllables(self, analyzer):
        """Test syllable counting."""
        test_cases = [
            ('hello', 2),
            ('world', 1),
            ('beautiful', 3),
            ('a', 1),
            ('the', 1),
            ('computer', 3),
        ]
        
        for word, expected in test_cases:
            result = analyzer._count_syllables(word)
            assert result >= 1  # Every word has at least one syllable
            # Allow some variation in syllable counting as it's an approximation
            assert abs(result - expected) <= 1
    
    def test_extract_dates(self, analyzer):
        """Test date extraction."""
        content = """
        Meeting on 03/15/2024
        Deadline: March 15, 2024
        Start date: 2024-03-15
        Another date: 12-25-2023
        """
        
        dates = analyzer._extract_dates(content)
        
        assert len(dates) > 0
        assert any('03/15/2024' in str(dates) or '03/15/2024' in dates)
        assert any('March 15, 2024' in str(dates) or 'March 15, 2024' in dates)
    
    def test_extract_monetary_amounts(self, analyzer):
        """Test monetary amount extraction."""
        content = """
        The budget is $50,000.00
        Cost: $1,500
        Price: 2000 USD
        Amount: 750 dollars
        """
        
        amounts = analyzer._extract_monetary_amounts(content)
        
        assert len(amounts) > 0
        assert any('50,000' in amount for amount in amounts)
        assert any('1,500' in amount for amount in amounts)
    
    def test_extract_percentages(self, analyzer):
        """Test percentage extraction."""
        content = "Success rate: 95.5%, efficiency: 80%, completion: 100%"
        
        percentages = analyzer._extract_percentages(content)
        
        assert len(percentages) >= 3
        assert '95.5%' in percentages
        assert '80%' in percentages
        assert '100%' in percentages
    
    def test_extract_emails(self, analyzer):
        """Test email extraction."""
        content = """
        Contact us at info@company.com
        Support: support@example.org
        Admin: admin.user@subdomain.domain.co.uk
        """
        
        emails = analyzer._extract_emails(content)
        
        assert len(emails) >= 3
        assert 'info@company.com' in emails
        assert 'support@example.org' in emails
    
    def test_extract_phone_numbers(self, analyzer):
        """Test phone number extraction."""
        content = """
        Call us at (555) 123-4567
        Phone: 555-987-6543
        Contact: 555.456.7890
        """
        
        phones = analyzer._extract_phone_numbers(content)
        
        assert len(phones) >= 3
        assert '(555) 123-4567' in phones
        assert '555-987-6543' in phones
        assert '555.456.7890' in phones
    
    def test_extract_urls(self, analyzer):
        """Test URL extraction."""
        content = """
        Visit our website: https://www.example.com
        Documentation: http://docs.example.org/api
        Support: https://support.company.com/help
        """
        
        urls = analyzer._extract_urls(content)
        
        assert len(urls) >= 3
        assert 'https://www.example.com' in urls
        assert 'http://docs.example.org/api' in urls
    
    def test_preprocess_text(self, analyzer):
        """Test text preprocessing."""
        content = "The QUICK brown fox jumps over the lazy dog!"
        
        words = analyzer._preprocess_text(content)
        
        # Should remove stop words and punctuation
        assert 'the' not in words  # Stop word
        assert 'quick' in words
        assert 'brown' in words
        assert 'fox' in words
        assert 'jumps' in words
        
        # Should be lowercase
        assert all(word.islower() for word in words)
    
    def test_identify_technical_terms(self, analyzer):
        """Test technical term identification."""
        content = """
        The implementation involves sophisticated algorithms and methodologies.
        We use API, REST, JSON, and XML technologies.
        The multi-threading approach ensures high-performance processing.
        """
        
        technical_terms = analyzer._identify_technical_terms(content)
        
        assert len(technical_terms) > 0
        # Should find terms with technical suffixes
        assert any('tion' in term for term in technical_terms)
        # Should find acronyms
        # Should find hyphenated terms
    
    def test_identify_business_terms(self, analyzer):
        """Test business term identification."""
        content = """
        This contract outlines the project requirements and deliverables.
        The proposal includes budget estimates and timeline milestones.
        Our client expects quality service and timely delivery.
        """
        
        business_terms = analyzer._identify_business_terms(content)
        
        assert len(business_terms) > 0
        assert 'contract' in business_terms
        assert 'proposal' in business_terms
        assert 'budget' in business_terms
        assert 'timeline' in business_terms
        assert 'client' in business_terms
        assert 'service' in business_terms
    
    def test_extract_action_items(self, analyzer):
        """Test action item extraction."""
        content = """
        The team must complete the design phase by next week.
        Action item: Review all technical specifications.
        TODO: Update the project documentation.
        Task: Coordinate with the client for approval.
        The system shall provide real-time monitoring.
        """
        
        action_items = analyzer._extract_action_items(content)
        
        assert len(action_items) > 0
        # Should find various action item patterns
        assert any(len(item) > 10 for item in action_items)  # Meaningful action items
    
    def test_find_requirement_indicators(self, analyzer):
        """Test requirement indicator identification."""
        content = """
        The system must have high availability.
        The application shall provide user authentication.
        Users are required to complete training.
        The service needs to support 1000+ concurrent users.
        The platform should include analytics dashboard.
        """
        
        indicators = analyzer._find_requirement_indicators(content)
        
        assert len(indicators) > 0
        # Should find context around requirement phrases
        assert any('must have' in indicator for indicator in indicators)
        assert any('shall provide' in indicator for indicator in indicators)


class TestDocumentAnalyzerEdgeCases:
    """Test edge cases and error conditions."""
    
    @pytest.fixture
    def analyzer(self):
        return DocumentAnalyzer()
    
    def test_analyze_very_short_content(self, analyzer):
        """Test analysis with very short content."""
        short_content = "Hi."
        
        structure = analyzer.analyze_document_structure(short_content)
        entities = analyzer.extract_key_entities(short_content)
        themes = analyzer.analyze_content_themes(short_content)
        
        # Should handle gracefully without errors
        assert structure['word_count'] == 1
        assert all(isinstance(entity_list, list) for entity_list in entities.values())
        assert all(isinstance(theme_data, list) for theme_data in themes.values() if isinstance(theme_data, list))
    
    def test_analyze_special_characters(self, analyzer):
        """Test analysis with special characters and unicode."""
        special_content = """
        Special chars: ñáéíóú çâêîô
        Symbols: ©®™ §¶• ←→↑↓
        Unicode: 你好 مرحبا Здравствуйте
        """
        
        # Should handle without errors
        structure = analyzer.analyze_document_structure(special_content)
        entities = analyzer.extract_key_entities(special_content)
        themes = analyzer.analyze_content_themes(special_content)
        
        assert structure['word_count'] > 0
        assert isinstance(entities, dict)
        assert isinstance(themes, dict)
    
    def test_analyze_very_long_content(self, analyzer):
        """Test analysis with very long content."""
        # Create a long document
        long_content = "This is a test sentence. " * 1000
        
        structure = analyzer.analyze_document_structure(long_content)
        
        assert structure['word_count'] == 5000  # 5 words * 1000 repetitions
        assert structure['total_length'] > 20000  # Should be quite long
        assert isinstance(structure['readability_score'], (int, float))


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
