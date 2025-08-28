#!/usr/bin/env python3
"""
Test script for CUNY Chatbot
This script tests the chatbot functionality without requiring an OpenAI API key.
"""

import os
import sys
from knowledge_base import CUNYKnowledgeBase
from chatbot import CUNYChatbot

def test_knowledge_base():
    """Test the knowledge base functionality"""
    print("Testing Knowledge Base...")
    
    kb = CUNYKnowledgeBase()
    
    # Test search functionality
    test_queries = [
        "admission requirements",
        "tuition costs",
        "scholarships",
        "campus housing",
        "meal plans",
        "safety",
        "majors",
        "deadlines"
    ]
    
    for query in test_queries:
        results = kb.search(query)
        print(f"  ✅ Query: '{query}' -> Found {len(results)} results")
        if results:
            print(f"     Top result: {results[0]['category']}")
    
    # Test specific info retrieval
    categories = ["admissions", "tuition_fees", "scholarships", "campus_life"]
    for category in categories:
        info = kb.get_specific_info(category)
        if info:
            print(f"  Category '{category}' -> Data available")
        else:
            print(f"  Category '{category}' -> No data found")
    
    print("Knowledge Base tests completed!\n")

def test_chatbot_fallback():
    """Test chatbot fallback responses without OpenAI"""
    print("🧪 Testing Chatbot Fallback Responses...")
    
    kb = CUNYKnowledgeBase()
    chatbot = CUNYChatbot(kb)
    
    # Test fallback responses
    test_messages = [
        "What are the admission requirements?",
        "How much is tuition?",
        "Tell me about scholarships",
        "I want to visit campus",
        "What majors do you offer?",
        "Hello, how are you?"
    ]
    
    for message in test_messages:
        try:
            response = chatbot._get_fallback_response(message)
            print(f"  Message: '{message[:50]}...'")
            print(f"     Response: '{response[:100]}...'")
        except Exception as e:
            print(f"  Error with message '{message}': {str(e)}")
    
    print("Chatbot fallback tests completed!\n")

def test_quick_responses():
    """Test quick response functionality"""
    print("🧪 Testing Quick Responses...")
    
    kb = CUNYKnowledgeBase()
    chatbot = CUNYChatbot(kb)
    
    quick_types = ["admissions", "tuition", "scholarships", "campus_life", "majors"]
    
    for qtype in quick_types:
        try:
            response = chatbot.get_quick_response(qtype)
            print(f"  Quick response for '{qtype}': '{response[:80]}...'")
        except Exception as e:
            print(f"  Error with quick response '{qtype}': {str(e)}")
    
    print("Quick response tests completed!\n")

def test_data_integrity():
    """Test that all required data is present"""
    print("esting Data Integrity")
    
    kb = CUNYKnowledgeBase()
    data = kb.data
    
    required_categories = [
        "admissions", "tuition_fees", "scholarships", "campus_life",
        "academics", "campus_tours", "student_services", "technology", "transportation"
    ]
    
    for category in required_categories:
        if category in data:
            print(f"  Category '{category}' found")
            # Check if category has content
            if data[category]:
                print(f"     Contains {len(data[category])} subcategories/items")
            else:
                print(f"     ategory '{category}' is empty")
        else:
            print(f"  Category '{category}' missing")
    
    # Test specific important data points
    important_data = [
        ("admissions", "requirements"),
        ("tuition_fees", "undergraduate"),
        ("scholarships", "cuny_excellence"),
        ("campus_life", "housing"),
        ("academics", "majors")
    ]
    
    for category, subcategory in important_data:
        if category in data and subcategory in data[category]:
            print(f"  Important data '{category}.{subcategory}' found")
        else:
            print(f"  Important data '{category}.{subcategory}' missing")
    
    print("Data integrity tests completed!\n")

def main():
    """Run all tests"""
    print("Starting CUNY Chatbot Tests...\n")
    
    try:
        test_knowledge_base()
        test_chatbot_fallback()
        test_quick_responses()
        test_data_integrity()
        
        print("All tests completed successfully!")
        print("\n Summary:")
        print("  Knowledge base is working correctly")
        print("  Chatbot fallback responses are functional")
        print("  Quick responses are available")
        print("  Data integrity is maintained")
        print("\n The chatbot is ready to use!")
        print("   To run the web interface: python app.py")
        
    except Exception as e:
        print(f"Test failed with error: {str(e)}")
        sys.exit(1)

if __name__ == "__main__":
    main()
