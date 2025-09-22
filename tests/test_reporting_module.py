"""
Test script for Reporting Module - FeedbackAnalyzer

This script tests the FeedbackAnalyzer functionality including:
- Feedback analysis with various rating distributions
- Keyword extraction from comments
- Statistical calculations
- Edge case handling (empty feedback, missing comments)
"""

import sys
import os
from datetime import datetime

# Add the project root to the path
sys.path.append('/Users/lemaja/proposal_master')

from src.modules.reporting.feedback_analyzer import FeedbackAnalyzer
from src.models.core import Feedback


def create_sample_feedback():
    """Create sample feedback objects for testing."""
    
    # Sample feedback data with varying ratings and comments
    feedback_data = [
        (5, "Excellent proposal! Very detailed and addresses all our requirements. The technical approach is solid and the timeline looks realistic."),
        (4, "Good overall proposal. Technical solution is sound but pricing could be more competitive. Team qualifications look strong."),
        (5, "Outstanding work! The executive summary clearly explains the value proposition. Implementation plan is comprehensive."),
        (3, "Average proposal. Some sections lack detail. Risk management section needs improvement. Budget seems reasonable."),
        (4, "Well-structured document. Technical approach is innovative. Would like to see more client references and case studies."),
        (2, "Proposal lacks detail in several key areas. Timeline seems unrealistic. Pricing is too high for the scope of work."),
        (5, "Fantastic proposal! Demonstrates deep understanding of our requirements. Clear deliverables and milestones."),
        (3, "Decent proposal but missing some technical details. Quality assurance section could be stronger."),
        (4, "Good technical solution. Team has relevant experience. Implementation methodology is well-defined."),
        (1, "Poor proposal. Doesn't address key requirements. Timeline is completely unrealistic. Would not recommend."),
        (5, "Excellent comprehensive proposal. All sections are well-written. Technical approach is innovative and practical."),
        (4, "Strong proposal overall. Minor issues with budget breakdown. Team qualifications are impressive."),
        (3, "Mediocre proposal. Some good points but lacks depth in technical implementation details."),
        (5, "Perfect proposal! Exactly what we were looking for. Clear, detailed, and professionally presented."),
        (2, "Weak proposal. Missing critical information. Budget seems inflated. Timeline is not achievable.")
    ]
    
    # Create Feedback objects
    feedback_objects = []
    for i, (rating, comment) in enumerate(feedback_data):
        feedback = Feedback()
        feedback.id = i + 1
        feedback.proposal_id = (i % 3) + 1  # Distribute across 3 proposals
        feedback.rating = rating
        feedback.comment = comment
        feedback.created_at = datetime.now()
        feedback_objects.append(feedback)
    
    return feedback_objects


def test_feedback_analyzer():
    """Test the FeedbackAnalyzer functionality."""
    
    print("=" * 60)
    print("TESTING REPORTING MODULE - FEEDBACK ANALYZER")
    print("=" * 60)
    
    # Initialize the feedback analyzer
    print("\n1. Initializing FeedbackAnalyzer...")
    analyzer = FeedbackAnalyzer()
    print("   ✓ FeedbackAnalyzer initialized successfully")
    
    # Create sample feedback data
    print("\n2. Creating Sample Feedback Data...")
    feedback_list = create_sample_feedback()
    print(f"   ✓ Created {len(feedback_list)} sample feedback entries")
    
    # Display sample feedback summary
    print(f"\n3. Sample Feedback Overview:")
    rating_counts = {}
    for feedback in feedback_list:
        rating_counts[feedback.rating] = rating_counts.get(feedback.rating, 0) + 1
    
    for rating in sorted(rating_counts.keys()):
        count = rating_counts[rating]
        print(f"   Rating {rating}: {count} entries ({count/len(feedback_list)*100:.1f}%)")
    
    # Test the analyze_feedback method
    print("\n4. Testing Feedback Analysis...")
    analysis_result = analyzer.analyze_feedback(feedback_list)
    
    print(f"   Analysis Results:")
    print(f"   ✓ Total Feedback: {analysis_result['total_feedback']}")
    print(f"   ✓ Average Rating: {analysis_result['average_rating']}")
    
    print(f"\n5. Rating Distribution Analysis:")
    rating_distribution = analysis_result['rating_distribution']
    for rating in sorted(rating_distribution.keys()):
        count = rating_distribution[rating]
        percentage = (count / analysis_result['total_feedback']) * 100
        stars = "★" * rating + "☆" * (5 - rating)
        print(f"   {stars} ({rating}/5): {count} responses ({percentage:.1f}%)")
    
    print(f"\n6. Common Keywords Analysis:")
    common_keywords = analysis_result['common_keywords']
    print(f"   Found {len(common_keywords)} common keywords:")
    for i, keyword in enumerate(common_keywords, 1):
        print(f"   {i:2d}. {keyword}")
    
    # Test with filtered feedback (high ratings only)
    print("\n" + "=" * 60)
    print("TESTING WITH FILTERED FEEDBACK (HIGH RATINGS)")
    print("=" * 60)
    
    high_rating_feedback = [f for f in feedback_list if f.rating >= 4]
    print(f"\n7. Analyzing High Rating Feedback (4-5 stars)...")
    print(f"   Filtered to {len(high_rating_feedback)} entries")
    
    high_rating_analysis = analyzer.analyze_feedback(high_rating_feedback)
    print(f"   ✓ Average Rating: {high_rating_analysis['average_rating']}")
    print(f"   ✓ Rating Distribution: {high_rating_analysis['rating_distribution']}")
    print(f"   ✓ Top Keywords: {high_rating_analysis['common_keywords'][:5]}")
    
    # Test with filtered feedback (low ratings only)
    print("\n8. Analyzing Low Rating Feedback (1-2 stars)...")
    low_rating_feedback = [f for f in feedback_list if f.rating <= 2]
    print(f"   Filtered to {len(low_rating_feedback)} entries")
    
    low_rating_analysis = analyzer.analyze_feedback(low_rating_feedback)
    print(f"   ✓ Average Rating: {low_rating_analysis['average_rating']}")
    print(f"   ✓ Rating Distribution: {low_rating_analysis['rating_distribution']}")
    print(f"   ✓ Top Keywords: {low_rating_analysis['common_keywords'][:5]}")
    
    # Test edge cases
    print("\n" + "=" * 60)
    print("TESTING EDGE CASES")
    print("=" * 60)
    
    # Test with empty feedback list
    print("\n9. Testing with Empty Feedback List...")
    empty_analysis = analyzer.analyze_feedback([])
    print(f"   ✓ Total Feedback: {empty_analysis['total_feedback']}")
    print(f"   ✓ Average Rating: {empty_analysis['average_rating']}")
    print(f"   ✓ Rating Distribution: {empty_analysis['rating_distribution']}")
    print(f"   ✓ Common Keywords: {empty_analysis['common_keywords']}")
    
    # Test with feedback having no comments
    print("\n10. Testing with Feedback Without Comments...")
    no_comment_feedback = []
    for i in range(5):
        feedback = Feedback()
        feedback.id = i + 100
        feedback.proposal_id = 1
        feedback.rating = i + 1  # Ratings 1-5
        feedback.comment = None  # No comment
        feedback.created_at = datetime.now()
        no_comment_feedback.append(feedback)
    
    no_comment_analysis = analyzer.analyze_feedback(no_comment_feedback)
    print(f"   ✓ Total Feedback: {no_comment_analysis['total_feedback']}")
    print(f"   ✓ Average Rating: {no_comment_analysis['average_rating']}")
    print(f"   ✓ Rating Distribution: {no_comment_analysis['rating_distribution']}")
    print(f"   ✓ Common Keywords: {no_comment_analysis['common_keywords']} (expected empty)")
    
    # Test with mixed feedback (some with comments, some without)
    print("\n11. Testing with Mixed Feedback...")
    mixed_feedback = feedback_list[:5] + no_comment_feedback
    mixed_analysis = analyzer.analyze_feedback(mixed_feedback)
    print(f"   ✓ Total Feedback: {mixed_analysis['total_feedback']}")
    print(f"   ✓ Average Rating: {mixed_analysis['average_rating']}")
    print(f"   ✓ Keywords Found: {len(mixed_analysis['common_keywords'])}")
    
    # Comparative Analysis
    print("\n" + "=" * 60)
    print("COMPARATIVE ANALYSIS")
    print("=" * 60)
    
    print(f"\n12. Summary Comparison:")
    print(f"   All Feedback:")
    print(f"     - Count: {analysis_result['total_feedback']}")
    print(f"     - Avg Rating: {analysis_result['average_rating']}")
    print(f"     - Keywords: {len(analysis_result['common_keywords'])}")
    
    print(f"   High Ratings (4-5):")
    print(f"     - Count: {high_rating_analysis['total_feedback']}")
    print(f"     - Avg Rating: {high_rating_analysis['average_rating']}")
    print(f"     - Keywords: {len(high_rating_analysis['common_keywords'])}")
    
    print(f"   Low Ratings (1-2):")
    print(f"     - Count: {low_rating_analysis['total_feedback']}")
    print(f"     - Avg Rating: {low_rating_analysis['average_rating']}")
    print(f"     - Keywords: {len(low_rating_analysis['common_keywords'])}")
    
    # Keyword comparison
    print(f"\n13. Keyword Analysis Comparison:")
    all_keywords = set(analysis_result['common_keywords'])
    high_keywords = set(high_rating_analysis['common_keywords'])
    low_keywords = set(low_rating_analysis['common_keywords'])
    
    positive_words = high_keywords - low_keywords
    negative_words = low_keywords - high_keywords
    common_words = high_keywords & low_keywords
    
    print(f"   Positive Keywords (high ratings only): {list(positive_words)[:5]}")
    print(f"   Negative Keywords (low ratings only): {list(negative_words)[:5]}")
    print(f"   Common Keywords (both high/low): {list(common_words)[:5]}")
    
    print("\n" + "=" * 60)
    print("REPORTING MODULE TESTING COMPLETE")
    print("=" * 60)
    
    return analysis_result


if __name__ == "__main__":
    test_feedback_analyzer()
