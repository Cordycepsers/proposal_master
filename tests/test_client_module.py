"""
Test suite for Client Module components.
"""

import pytest
import asyncio
from src.modules.client.capability_evaluator import CapabilityEvaluator
from src.modules.client.profile_comparator import ProfileComparator


class TestCapabilityEvaluator:
    """Test cases for CapabilityEvaluator class."""
    
    @pytest.fixture
    def evaluator(self):
        """Create a CapabilityEvaluator instance for testing."""
        return CapabilityEvaluator()
    
    @pytest.fixture
    def sample_client_profile(self):
        """Create a sample client profile for testing."""
        return {
            'id': 'client_001',
            'name': 'Tech Innovators Inc',
            'team_size': 15,
            'years_experience': 8,
            'technology_experience': {
                'languages': ['Python', 'JavaScript', 'Java'],
                'frameworks': ['React', 'Django', 'Spring']
            },
            'budget_track_record': 'good',
            'project_success_rate': 0.85,
            'organizational_maturity': 'defined'
        }
    
    @pytest.fixture
    def sample_project_requirements(self):
        """Create sample project requirements for testing."""
        return {
            'id': 'project_001',
            'technologies': ['Python', 'React', 'PostgreSQL'],
            'estimated_team_size': 10,
            'technical_complexity': 3.5,
            'management_complexity': 3.0,
            'estimated_budget': {'min': 100000, 'max': 200000}
        }
    
    def test_initialization(self, evaluator):
        """Test CapabilityEvaluator initialization."""
        assert evaluator.name == "Capability Evaluator"
        assert "capabilities" in evaluator.description.lower()
        assert len(evaluator.capability_dimensions) == 5
        assert all(dim in evaluator.capability_dimensions for dim in 
                  ['technical', 'operational', 'organizational', 'financial', 'strategic'])
        assert len(evaluator.maturity_levels) == 5
    
    def test_get_statistics(self, evaluator):
        """Test getting evaluation statistics."""
        stats = evaluator.get_statistics()
        assert isinstance(stats, dict)
        assert 'evaluations_completed' in stats
        assert 'avg_capability_score' in stats
        assert 'high_readiness_clients' in stats
    
    @pytest.mark.asyncio
    async def test_process_invalid_input(self, evaluator):
        """Test process method with invalid input."""
        # Test with empty input
        result = await evaluator.process({})
        assert result['status'] == 'error'
        assert 'Client profile is required' in result['error']
        
        # Test with None
        result = await evaluator.process({'client_profile': None})
        assert result['status'] == 'error'
        assert 'Client profile is required' in result['error']
    
    @pytest.mark.asyncio
    async def test_process_valid_input(self, evaluator, sample_client_profile, sample_project_requirements):
        """Test process method with valid input."""
        input_data = {
            'client_profile': sample_client_profile,
            'project_requirements': sample_project_requirements,
            'assessment_scope': ['technical', 'operational']
        }
        
        result = await evaluator.process(input_data)
        
        assert result['status'] == 'success'
        assert result['client_id'] == 'client_001'
        assert 'capability_assessment' in result
        assert 'readiness_score' in result
        assert 'capability_gaps' in result
        assert 'improvement_plan' in result
        assert 'project_fit' in result
        
        # Check capability assessment structure
        assessment = result['capability_assessment']
        assert 'technical' in assessment
        assert 'operational' in assessment
        
        for dimension, data in assessment.items():
            assert 'score' in data
            assert 'maturity_level' in data
            assert 'maturity_name' in data
            assert 'factor_scores' in data
            assert 'weight' in data
            assert 'weighted_score' in data
    
    @pytest.mark.asyncio
    async def test_assess_capabilities(self, evaluator, sample_client_profile, sample_project_requirements):
        """Test capability assessment method."""
        assessment = await evaluator._assess_capabilities(
            sample_client_profile, sample_project_requirements, ['technical', 'operational']
        )
        
        assert isinstance(assessment, dict)
        assert 'technical' in assessment
        assert 'operational' in assessment
        
        # Check technical assessment
        tech_assessment = assessment['technical']
        assert 0 <= tech_assessment['score'] <= 5
        assert 1 <= tech_assessment['maturity_level'] <= 5
        assert tech_assessment['maturity_name'] in ['Initial', 'Developing', 'Defined', 'Managed', 'Optimizing']
    
    @pytest.mark.asyncio
    async def test_assess_factor(self, evaluator, sample_client_profile, sample_project_requirements):
        """Test individual factor assessment."""
        # Test technology stack factor
        score = await evaluator._assess_factor('technology_stack', sample_client_profile, sample_project_requirements)
        assert 1.0 <= score <= 5.0
        
        # Test team size factor
        score = await evaluator._assess_factor('team_size', sample_client_profile, sample_project_requirements)
        assert 1.0 <= score <= 5.0
        
        # Test budget management factor
        score = await evaluator._assess_factor('budget_management', sample_client_profile, sample_project_requirements)
        assert 1.0 <= score <= 5.0
    
    @pytest.mark.asyncio
    async def test_calculate_readiness_score(self, evaluator):
        """Test readiness score calculation."""
        mock_assessment = {
            'technical': {'weighted_score': 1.2, 'weight': 0.3},
            'operational': {'weighted_score': 1.0, 'weight': 0.25}
        }
        
        readiness = await evaluator._calculate_readiness_score(mock_assessment)
        
        assert isinstance(readiness, dict)
        assert 'overall_score' in readiness
        assert 'readiness_level' in readiness
        assert 'description' in readiness
        assert 'percentage' in readiness
        assert readiness['readiness_level'] in ['very_low', 'low', 'medium', 'high', 'very_high']
    
    @pytest.mark.asyncio
    async def test_identify_capability_gaps(self, evaluator):
        """Test capability gap identification."""
        mock_assessment = {
            'technical': {
                'score': 2.5,  # Below 3.0 threshold
                'factor_scores': {'technology_stack': 2.0, 'architecture_experience': 3.0}
            },
            'operational': {
                'score': 4.0,  # Above threshold
                'factor_scores': {'project_management': 4.0, 'team_size': 4.0}
            }
        }
        
        gaps = await evaluator._identify_capability_gaps(mock_assessment, {})
        
        assert isinstance(gaps, list)
        assert len(gaps) == 1  # Only technical should have gaps
        assert gaps[0]['dimension'] == 'technical'
        assert gaps[0]['current_score'] == 2.5
        assert gaps[0]['severity'] in ['high', 'medium']


class TestProfileComparator:
    """Test cases for ProfileComparator class."""
    
    @pytest.fixture
    def comparator(self):
        """Create a ProfileComparator instance for testing."""
        return ProfileComparator()
    
    @pytest.fixture
    def sample_client_profile(self):
        """Create a sample client profile for testing."""
        return {
            'id': 'client_002',
            'name': 'Digital Solutions Ltd',
            'technology_experience': {
                'languages': ['Python', 'JavaScript', 'TypeScript'],
                'frameworks': ['React', 'Vue.js', 'Django']
            },
            'budget_range': {'min': 50000, 'max': 150000},
            'preferred_timeline': {'max_duration_months': 8},
            'industry_experience': ['finance', 'e-commerce'],
            'available_team_size': 12,
            'risk_tolerance': 'medium'
        }
    
    @pytest.fixture
    def sample_project_requirements(self):
        """Create sample project requirements for testing."""
        return {
            'id': 'project_002',
            'technologies': ['Python', 'React', 'Node.js'],
            'estimated_budget': {'min': 80000, 'max': 120000},
            'timeline': {'duration_months': 6},
            'industry': 'finance',
            'estimated_team_size': 8,
            'risk_level': 'medium'
        }
    
    def test_initialization(self, comparator):
        """Test ProfileComparator initialization."""
        assert comparator.name == "Profile Comparator"
        assert "compares" in comparator.description.lower()
        assert len(comparator.comparison_categories) == 5
        assert len(comparator.compatibility_levels) == 5
    
    @pytest.mark.asyncio
    async def test_process_invalid_input(self, comparator):
        """Test process method with invalid input."""
        # Test with missing client profile
        result = await comparator.process({'project_requirements': {}})
        assert result['status'] == 'error'
        assert 'Both client profile and project requirements are required' in result['error']
        
        # Test with missing project requirements
        result = await comparator.process({'client_profile': {}})
        assert result['status'] == 'error'
        assert 'Both client profile and project requirements are required' in result['error']
    
    @pytest.mark.asyncio
    async def test_process_valid_input(self, comparator, sample_client_profile, sample_project_requirements):
        """Test process method with valid input."""
        input_data = {
            'client_profile': sample_client_profile,
            'project_requirements': sample_project_requirements,
            'comparison_scope': ['technical_alignment', 'business_alignment']
        }
        
        result = await comparator.process(input_data)
        
        assert result['status'] == 'success'
        assert result['client_id'] == 'client_002'
        assert result['project_id'] == 'project_002'
        assert 'category_comparisons' in result
        assert 'compatibility_score' in result
        assert 'alignment_analysis' in result
        assert 'recommendations' in result
        assert 'risk_assessment' in result
        
        # Check compatibility score structure
        score = result['compatibility_score']
        assert 'overall_score' in score
        assert 'compatibility_level' in score
        assert 'recommendation' in score
        assert 0 <= score['overall_score'] <= 1
    
    @pytest.mark.asyncio
    async def test_compare_categories(self, comparator, sample_client_profile, sample_project_requirements):
        """Test category comparison method."""
        comparisons = await comparator._compare_categories(
            sample_client_profile, 
            sample_project_requirements, 
            ['technical_alignment', 'business_alignment'],
            {'technical_alignment': 0.3, 'business_alignment': 0.2}
        )
        
        assert isinstance(comparisons, dict)
        assert 'technical_alignment' in comparisons
        assert 'business_alignment' in comparisons
        
        for category, data in comparisons.items():
            assert 'score' in data
            assert 'weight' in data
            assert 'weighted_score' in data
            assert 'factor_comparisons' in data
            assert 'alignment_level' in data
    
    @pytest.mark.asyncio
    async def test_compare_factor_technology_stack(self, comparator, sample_client_profile, sample_project_requirements):
        """Test technology stack factor comparison."""
        score, details = await comparator._compare_factor(
            'technology_stack', sample_client_profile, sample_project_requirements
        )
        
        assert 0 <= score <= 1
        assert isinstance(details, dict)
        assert 'client_value' in details
        assert 'required_value' in details
        assert 'match_quality' in details
        
        # Should find matches for Python and React
        assert details['matches'] >= 2
        assert details['match_quality'] in ['excellent', 'good', 'partial', 'poor']
    
    @pytest.mark.asyncio
    async def test_compare_factor_budget_range(self, comparator, sample_client_profile, sample_project_requirements):
        """Test budget range factor comparison."""
        score, details = await comparator._compare_factor(
            'budget_range', sample_client_profile, sample_project_requirements
        )
        
        assert 0 <= score <= 1
        assert isinstance(details, dict)
        assert 'match_quality' in details
        
        # Client max (150k) covers project max (120k), should be excellent
        assert score >= 0.7
        assert details['match_quality'] in ['excellent', 'good', 'adequate', 'insufficient']
    
    @pytest.mark.asyncio
    async def test_compare_factor_industry_experience(self, comparator, sample_client_profile, sample_project_requirements):
        """Test industry experience factor comparison."""
        score, details = await comparator._compare_factor(
            'industry_experience', sample_client_profile, sample_project_requirements
        )
        
        assert 0 <= score <= 1
        assert isinstance(details, dict)
        
        # Client has finance experience, project is finance - should be perfect match
        assert score == 1.0
        assert details['match_quality'] == 'direct_match'
    
    @pytest.mark.asyncio
    async def test_calculate_industry_similarity(self, comparator):
        """Test industry similarity calculation."""
        # Test direct relationship
        similarity = await comparator._calculate_industry_similarity(['banking'], 'finance')
        assert similarity >= 0.6
        
        # Test unrelated industries
        similarity = await comparator._calculate_industry_similarity(['manufacturing'], 'healthcare')
        assert similarity <= 0.5
    
    @pytest.mark.asyncio
    async def test_calculate_compatibility_score(self, comparator):
        """Test compatibility score calculation."""
        mock_comparisons = {
            'technical_alignment': {'weighted_score': 0.2, 'weight': 0.25},
            'business_alignment': {'weighted_score': 0.18, 'weight': 0.2}
        }
        
        score = await comparator._calculate_compatibility_score(mock_comparisons)
        
        assert isinstance(score, dict)
        assert 'overall_score' in score
        assert 'compatibility_level' in score
        assert 'recommendation' in score
        assert 'color_indicator' in score
        assert score['compatibility_level'] in ['excellent', 'good', 'fair', 'poor', 'very_poor']


class TestClientModuleIntegration:
    """Integration tests for client module components."""
    
    @pytest.mark.asyncio
    async def test_capability_evaluator_with_profile_comparator(self):
        """Test integration between CapabilityEvaluator and ProfileComparator."""
        evaluator = CapabilityEvaluator()
        comparator = ProfileComparator()
        
        client_profile = {
            'id': 'integration_test_client',
            'name': 'Test Client Corp',
            'team_size': 20,
            'years_experience': 5,
            'technology_experience': {
                'languages': ['Python', 'JavaScript'],
                'frameworks': ['React', 'Flask']
            },
            'budget_track_record': 'excellent',
            'project_success_rate': 0.9,
            'organizational_maturity': 'managed',
            'budget_range': {'min': 100000, 'max': 300000},
            'industry_experience': ['technology', 'finance'],
            'available_team_size': 15,
            'risk_tolerance': 'medium'
        }
        
        project_requirements = {
            'id': 'integration_test_project',
            'technologies': ['Python', 'React', 'PostgreSQL'],
            'estimated_team_size': 12,
            'technical_complexity': 4.0,
            'management_complexity': 3.5,
            'estimated_budget': {'min': 150000, 'max': 250000},
            'timeline': {'duration_months': 8},
            'industry': 'technology',
            'risk_level': 'medium'
        }
        
        # Run capability evaluation
        capability_result = await evaluator.process({
            'client_profile': client_profile,
            'project_requirements': project_requirements
        })
        
        assert capability_result['status'] == 'success'
        capability_score = capability_result['readiness_score']['overall_score']
        
        # Run profile comparison
        comparison_result = await comparator.process({
            'client_profile': client_profile,
            'project_requirements': project_requirements
        })
        
        assert comparison_result['status'] == 'success'
        compatibility_score = comparison_result['compatibility_score']['overall_score']
        
        # Both should indicate good fit for this well-matched scenario
        assert capability_score >= 3.5  # Good capability score (out of 5)
        assert compatibility_score >= 0.7  # Good compatibility score (out of 1)
        
        print(f"Integration Test Results:")
        print(f"Capability Score: {capability_score}/5.0 ({capability_result['readiness_score']['readiness_level']})")
        print(f"Compatibility Score: {compatibility_score}/1.0 ({comparison_result['compatibility_score']['compatibility_level']})")


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
