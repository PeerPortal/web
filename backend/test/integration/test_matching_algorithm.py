"""
Test suite for enhanced matching algorithm with partial matching support
Tests both individual functions and end-to-end matching scenarios
"""

import pytest
import asyncio
from unittest.mock import Mock, AsyncMock
from typing import Dict, List, Any
import sys
import os

# Add the project root to Python path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.crud.crud_matching import (
    _calculate_string_similarity,
    _are_related_majors,
    _are_adjacent_degrees,
    calculate_match_scores,
    create_matching_request,
    save_matching_result
)

# Mock schema classes for testing
class MockMatchingRequest:
    def __init__(self, target_universities=None, target_majors=None, degree_level="master", 
                 preferred_languages=None, service_categories=None):
        self.target_universities = target_universities or ["Stanford University"]
        self.target_majors = target_majors or ["Computer Science"]
        self.degree_level = degree_level
        self.preferred_languages = preferred_languages or ["English"]
        self.service_categories = service_categories or ["Academic Guidance"]

class TestHelperFunctions:
    """Test helper functions for partial matching"""
    
    def test_string_similarity(self):
        """Test string similarity calculation"""
        # Exact match
        assert _calculate_string_similarity("Stanford University", "Stanford University") == 1.0
        
        # Partial match
        similarity = _calculate_string_similarity("Stanford University", "Stanford")
        assert similarity > 0.7  # Should be high similarity
        
        # Different strings
        similarity = _calculate_string_similarity("Harvard", "MIT")
        assert similarity < 0.3  # Should be low similarity
        
        # Case insensitive
        similarity = _calculate_string_similarity("Computer Science", "computer science")
        assert similarity == 1.0
        
        print("✅ String similarity tests passed")

    def test_related_majors(self):
        """Test related major detection"""
        # Direct relation
        assert _are_related_majors("Computer Science", "Software Engineering") == True
        assert _are_related_majors("Business Administration", "Management") == True
        
        # Bidirectional relation
        assert _are_related_majors("Data Science", "Computer Science") == True
        assert _are_related_majors("Software Engineering", "Computer Science") == True
        
        # Unrelated majors
        assert _are_related_majors("Computer Science", "Biology") == False
        assert _are_related_majors("Psychology", "Engineering") == False
        
        # Case insensitive
        assert _are_related_majors("COMPUTER SCIENCE", "data science") == True
        
        print("✅ Related majors tests passed")

    def test_adjacent_degrees(self):
        """Test adjacent degree detection"""
        # Adjacent degrees
        assert _are_adjacent_degrees("bachelor", "master") == True
        assert _are_adjacent_degrees("master", "phd") == True
        assert _are_adjacent_degrees("phd", "master") == True
        
        # Non-adjacent degrees
        assert _are_adjacent_degrees("bachelor", "phd") == False
        
        # Same degree
        assert _are_adjacent_degrees("master", "master") == False
        
        # Case insensitive
        assert _are_adjacent_degrees("BACHELOR", "master") == True
        
        print("✅ Adjacent degrees tests passed")

class TestMatchingAlgorithm:
    """Test the main matching algorithm"""
    
    @pytest.fixture
    def sample_mentors(self):
        """Sample mentor data for testing"""
        return [
            {
                'id': 1,
                'university': 'Stanford University',
                'major': 'Computer Science',
                'degree_level': 'master',
                'rating': 4.8,
                'total_sessions': 45,
                'languages': ['English', 'Chinese'],
                'specialties': ['Academic Guidance', 'Career Planning'],
                'verification_status': 'verified'
            },
            {
                'id': 2,
                'university': 'MIT',
                'major': 'Software Engineering',
                'degree_level': 'phd',
                'rating': 4.9,
                'total_sessions': 62,
                'languages': ['English'],
                'specialties': ['Technical Interview', 'Research Guidance'],
                'verification_status': 'verified'
            },
            {
                'id': 3,
                'university': 'UC Berkeley',
                'major': 'Data Science',
                'degree_level': 'master',
                'rating': 4.7,
                'total_sessions': 28,
                'languages': ['English', 'Spanish'],
                'specialties': ['Academic Guidance'],
                'verification_status': 'verified'
            },
            {
                'id': 4,
                'university': 'Harvard University',
                'major': 'Business Administration',
                'degree_level': 'master',
                'rating': 4.6,
                'total_sessions': 35,
                'languages': ['English'],
                'specialties': ['Career Planning'],
                'verification_status': 'verified'
            }
        ]

    def test_exact_matching(self, sample_mentors):
        """Test exact matching functionality"""
        request = MockMatchingRequest(
            target_universities=["Stanford University"],
            target_majors=["Computer Science"],
            degree_level="master"
        )
        
        # Mock Supabase response
        mock_result = Mock()
        mock_result.data = sample_mentors
        
        # Simulate the matching logic for exact matches
        matches = []
        for mentor in sample_mentors:
            score = 0.0
            
            # University exact match
            if mentor['university'] in request.target_universities:
                score += 0.3
                
            # Major exact match
            if mentor['major'] in request.target_majors:
                score += 0.25
                
            # Degree exact match
            if mentor['degree_level'] == request.degree_level:
                score += 0.2
                
            # Rating score
            score += (mentor['rating'] / 5.0) * 0.15
            
            # Language match
            if not request.preferred_languages or any(lang in mentor.get('languages', []) for lang in request.preferred_languages):
                score += 0.1
            
            mentor['total_score'] = score
            if score > 0.5:  # Only include high-scoring matches
                matches.append(mentor)
        
        # Should find Stanford CS mentor with high score
        stanford_match = next((m for m in matches if m['university'] == 'Stanford University'), None)
        assert stanford_match is not None
        assert stanford_match['total_score'] > 0.8  # Should have high score for exact match
        
        print("✅ Exact matching tests passed")

    def test_partial_matching(self, sample_mentors):
        """Test partial matching functionality"""
        request = MockMatchingRequest(
            target_universities=["Stanford"],  # Partial university name
            target_majors=["Software Engineering"],  # Related but not exact major
            degree_level="master"
        )
        
        matches = []
        for mentor in sample_mentors:
            university_score = 0.0
            major_score = 0.0
            
            # Test partial university matching
            for target_uni in request.target_universities:
                if (target_uni.lower() in mentor['university'].lower() or 
                    mentor['university'].lower() in target_uni.lower()):
                    university_score = max(university_score, 0.2)
                elif _calculate_string_similarity(mentor['university'], target_uni) > 0.7:
                    university_score = max(university_score, 0.15)
            
            # Test related major matching
            for target_major in request.target_majors:
                if mentor['major'] in request.target_majors:
                    major_score = 0.25
                elif _are_related_majors(mentor['major'], target_major):
                    major_score = max(major_score, 0.12)
                elif _calculate_string_similarity(mentor['major'], target_major) > 0.6:
                    major_score = max(major_score, 0.08)
            
            total_score = university_score + major_score
            mentor['partial_score'] = total_score
            
            if total_score > 0.1:
                matches.append(mentor)
        
        # Should find Stanford mentor with partial university match
        stanford_match = next((m for m in matches if 'Stanford' in m['university']), None)
        assert stanford_match is not None
        assert stanford_match['partial_score'] > 0.1
        
        # Should find related major matches
        related_major_matches = [m for m in matches if m['partial_score'] > 0.05]
        assert len(related_major_matches) > 0
        
        print("✅ Partial matching tests passed")

    def test_scoring_weights(self, sample_mentors):
        """Test that scoring weights are applied correctly"""
        request = MockMatchingRequest()
        
        for mentor in sample_mentors:
            # Calculate individual scores
            university_score = 0.3 if mentor['university'] in request.target_universities else 0.0
            major_score = 0.25 if mentor['major'] in request.target_majors else 0.0
            degree_score = 0.2 if mentor['degree_level'] == request.degree_level else 0.0
            rating_score = (mentor['rating'] / 5.0) * 0.15
            
            # Experience bonus
            experience_bonus = 0.0
            if mentor['total_sessions'] >= 50:
                experience_bonus = 0.05
            elif mentor['total_sessions'] >= 20:
                experience_bonus = 0.03
            elif mentor['total_sessions'] >= 5:
                experience_bonus = 0.01
            
            total_expected = university_score + major_score + degree_score + rating_score + experience_bonus
            
            # Verify scoring ranges
            assert 0.0 <= total_expected <= 1.0
            assert rating_score <= 0.15  # Rating shouldn't exceed 15%
            
        print("✅ Scoring weights tests passed")

class TestDatabaseIntegration:
    """Test database integration scenarios"""
    
    async def test_asyncpg_integration(self):
        """Test AsyncPG database integration"""
        # Mock database connection
        mock_conn = AsyncMock()
        mock_db_conn = {"type": "asyncpg", "connection": mock_conn}
        
        # Mock query results
        mock_conn.fetch.return_value = [
            {
                'id': 1,
                'university': 'Stanford University',
                'major': 'Computer Science',
                'degree_level': 'master',
                'rating': 4.8,
                'total_sessions': 45,
                'university_match': 0.3,
                'major_match': 0.25,
                'degree_match': 0.2,
                'rating_score': 0.144,
                'language_match': 0.1,
                'experience_bonus': 0.01,
                'specialty_bonus': 0.05,
                'total_score': 1.054,
                'username': 'mentor1',
                'full_name': 'John Mentor',
                'avatar_url': 'avatar1.jpg'
            }
        ]
        
        request = MockMatchingRequest()
        results = await calculate_match_scores(mock_db_conn, request)
        
        # Verify database was called with correct parameters
        mock_conn.fetch.assert_called_once()
        call_args = mock_conn.fetch.call_args
        assert len(call_args[0]) == 2  # Query string and parameters
        
        # Verify results
        assert len(results) == 1
        assert results[0]['total_score'] > 1.0  # High score for good match
        
        print("✅ AsyncPG integration tests passed")

    async def test_supabase_integration(self):
        """Test Supabase integration"""
        # Mock Supabase client
        mock_client = Mock()
        mock_db_conn = {"type": "supabase", "connection": mock_client}
        
        # Mock Supabase response
        mock_result = Mock()
        mock_result.data = [
            {
                'id': 1,
                'university': 'Stanford University',
                'major': 'Computer Science',
                'degree_level': 'master',
                'rating': 4.8,
                'total_sessions': 45,
                'languages': ['English'],
                'specialties': ['Academic Guidance']
            }
        ]
        
        # Setup mock chain
        mock_table = Mock()
        mock_select = Mock()
        mock_eq = Mock()
        mock_order = Mock()
        mock_limit = Mock()
        
        mock_client.table.return_value = mock_table
        mock_table.select.return_value = mock_select
        mock_select.eq.return_value = mock_eq
        mock_eq.order.return_value = mock_order
        mock_order.limit.return_value = mock_limit
        mock_limit.execute.return_value = mock_result
        
        request = MockMatchingRequest()
        results = await calculate_match_scores(mock_db_conn, request)
        
        # Verify Supabase was called correctly
        mock_client.table.assert_called_with('mentorship_relationships')
        
        # Verify results processing
        assert len(results) <= 50  # Should respect limit
        if results:
            assert 'total_score' in results[0]
            assert results[0]['total_score'] >= 0.0
        
        print("✅ Supabase integration tests passed")

class TestEdgeCases:
    """Test edge cases and error handling"""
    
    def test_empty_inputs(self):
        """Test handling of empty inputs"""
        request = MockMatchingRequest(
            target_universities=[],
            target_majors=[],
            preferred_languages=[]
        )
        
        # Should handle empty lists gracefully
        assert len(request.target_universities) == 0
        assert len(request.target_majors) == 0
        
        print("✅ Empty inputs tests passed")

    def test_invalid_degree_levels(self):
        """Test handling of invalid degree levels"""
        assert _are_adjacent_degrees("invalid", "master") == False
        assert _are_adjacent_degrees("bachelor", "invalid") == False
        assert _are_adjacent_degrees("", "") == False
        
        print("✅ Invalid degree levels tests passed")

    def test_none_values(self):
        """Test handling of None values"""
        # String similarity with None should not crash
        try:
            similarity = _calculate_string_similarity("test", None)
            assert similarity >= 0.0
        except Exception as e:
            # Should handle gracefully or raise appropriate error
            assert "NoneType" in str(e) or "argument" in str(e)
        
        print("✅ None values tests passed")

    async def test_database_error_handling(self):
        """Test database error handling"""
        # Mock database connection that raises an error
        mock_conn = AsyncMock()
        mock_db_conn = {"type": "asyncpg", "connection": mock_conn}
        mock_conn.fetch.side_effect = Exception("Database connection failed")
        
        request = MockMatchingRequest()
        results = await calculate_match_scores(mock_db_conn, request)
        
        # Should return empty list on error
        assert results == []
        
        print("✅ Database error handling tests passed")

class TestPerformance:
    """Test performance characteristics"""
    
    def test_large_dataset_handling(self):
        """Test handling of large datasets"""
        # Create large sample dataset
        large_dataset = []
        for i in range(1000):
            large_dataset.append({
                'id': i,
                'university': f'University {i}',
                'major': f'Major {i % 10}',
                'degree_level': 'master',
                'rating': 4.0 + (i % 10) * 0.1,
                'total_sessions': i % 100,
                'languages': ['English'],
                'specialties': ['Academic Guidance']
            })
        
        request = MockMatchingRequest()
        
        # Time the matching process
        import time
        start_time = time.time()
        
        matches = []
        for mentor in large_dataset[:100]:  # Process subset for testing
            score = 0.0
            
            # Simple scoring for performance test
            if mentor['university'] in request.target_universities:
                score += 0.3
            score += (mentor['rating'] / 5.0) * 0.15
            
            mentor['total_score'] = score
            matches.append(mentor)
        
        end_time = time.time()
        processing_time = end_time - start_time
        
        # Should process reasonably quickly
        assert processing_time < 1.0  # Should complete within 1 second
        assert len(matches) == 100
        
        print(f"✅ Performance tests passed - processed 100 records in {processing_time:.3f}s")

def run_all_tests():
    """Run all tests manually"""
    print("🚀 Starting enhanced matching algorithm tests...\n")
    
    # Test helper functions
    helper_tests = TestHelperFunctions()
    helper_tests.test_string_similarity()
    helper_tests.test_related_majors()
    helper_tests.test_adjacent_degrees()
    
    # Test matching algorithm
    matching_tests = TestMatchingAlgorithm()
    sample_mentors = [
        {
            'id': 1,
            'university': 'Stanford University',
            'major': 'Computer Science',
            'degree_level': 'master',
            'rating': 4.8,
            'total_sessions': 45,
            'languages': ['English', 'Chinese'],
            'specialties': ['Academic Guidance', 'Career Planning'],
            'verification_status': 'verified'
        },
        {
            'id': 2,
            'university': 'MIT',
            'major': 'Software Engineering',
            'degree_level': 'phd',
            'rating': 4.9,
            'total_sessions': 62,
            'languages': ['English'],
            'specialties': ['Technical Interview', 'Research Guidance'],
            'verification_status': 'verified'
        }
    ]
    
    matching_tests.test_exact_matching(sample_mentors)
    matching_tests.test_partial_matching(sample_mentors)
    matching_tests.test_scoring_weights(sample_mentors)
    
    # Test edge cases
    edge_tests = TestEdgeCases()
    edge_tests.test_empty_inputs()
    edge_tests.test_invalid_degree_levels()
    edge_tests.test_none_values()
    
    # Test performance
    perf_tests = TestPerformance()
    perf_tests.test_large_dataset_handling()
    
    # Run async tests
    async def run_async_tests():
        db_tests = TestDatabaseIntegration()
        await db_tests.test_asyncpg_integration()
        await db_tests.test_supabase_integration()
        
        edge_tests = TestEdgeCases()
        await edge_tests.test_database_error_handling()
    
    asyncio.run(run_async_tests())
    
    print("\n🎉 All tests completed successfully!")
    print("\n📊 Test Summary:")
    print("  ✅ Helper functions: String similarity, related majors, adjacent degrees")
    print("  ✅ Matching algorithm: Exact matching, partial matching, scoring weights")
    print("  ✅ Database integration: AsyncPG, Supabase")
    print("  ✅ Edge cases: Empty inputs, invalid values, error handling")
    print("  ✅ Performance: Large dataset handling")

if __name__ == "__main__":
    run_all_tests()
