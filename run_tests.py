# run_tests.py
import pytest
import sys
import os

def run_all_tests():
    """Run all tests with coverage reporting"""
    
    # Add current directory to Python path
    sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
    
    # Run pytest with coverage
    print("Running Smart Proposal System tests...")
    
    # Test specific modules
    test_modules = [
        'tests.test_document_processing',
        'tests.test_ai_content_generation', 
        'tests.test_research_module',
        'tests.test_anti_scraping',
        'tests.test_proposal_workflow',
        'tests.test_collaboration',
        'tests.test_export_functionality'
    ]
    
    # Run tests for each module
    for module in test_modules:
        print(f"Running tests for {module}")
        result = pytest.main([f'{module}', '-v'])
        if result != 0:
            print(f"Tests failed for {module}")
            return False
    
    print("All tests completed successfully!")
    return True

if __name__ == "__main__":
    run_all_tests()
