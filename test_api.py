#!/usr/bin/env python3
"""
Test script to verify OpenAI API key is working
"""

import os
import openai

def test_openai_api():
    """Test if OpenAI API key is working"""
    print("🔑 Testing OpenAI API Key...")
    
    # Get API key
    api_key = os.getenv('OPENAI_API_KEY')
    
    if not api_key:
        print("❌ No API key found in environment variables")
        print("   Please set: export OPENAI_API_KEY='your-key-here'")
        return False
    
    if api_key == 'your_openai_api_key_here':
        print("❌ API key is still the placeholder value")
        print("   Please set your actual API key")
        return False
    
    print(f"✅ API key found: {api_key[:10]}...")
    
    try:
        # Initialize client
        client = openai.OpenAI(api_key=api_key)
        
        # Test with a simple request
        response = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[{"role": "user", "content": "Say 'Hello from OpenAI!'"}],
            max_tokens=10
        )
        
        result = response.choices[0].message.content
        print(f"✅ API test successful! Response: {result}")
        return True
        
    except Exception as e:
        print(f"❌ API test failed: {str(e)}")
        return False

def test_chatbot_initialization():
    """Test if chatbot can initialize with API key"""
    print("\n🤖 Testing Chatbot Initialization...")
    
    try:
        from knowledge_base import CUNYKnowledgeBase
        from chatbot import CUNYChatbot
        
        kb = CUNYKnowledgeBase()
        chatbot = CUNYChatbot(kb)
        
        if chatbot.has_openai:
            print("✅ Chatbot initialized with OpenAI support")
            return True
        else:
            print("❌ Chatbot initialized without OpenAI support")
            return False
            
    except Exception as e:
        print(f"❌ Chatbot initialization failed: {str(e)}")
        return False

def test_chatbot_response():
    """Test if chatbot gives AI response vs fallback"""
    print("\n💬 Testing Chatbot Response...")
    
    try:
        from knowledge_base import CUNYKnowledgeBase
        from chatbot import CUNYChatbot
        
        kb = CUNYKnowledgeBase()
        chatbot = CUNYChatbot(kb)
        
        # Test with a specific question
        test_question = "What's the difference between Baruch and Hunter College for business majors?"
        
        response = chatbot.get_response(test_question)
        
        print(f"Question: {test_question}")
        print(f"Response: {response[:200]}...")
        
        # Check if it's a fallback response
        fallback_indicators = [
            "I'd be happy to help you learn more about CUNY",
            "What specific information are you looking for",
            "Could you please rephrase your question"
        ]
        
        is_fallback = any(indicator in response for indicator in fallback_indicators)
        
        if is_fallback:
            print("❌ Chatbot is using fallback response (no AI)")
        else:
            print("✅ Chatbot is using AI response")
            
        return not is_fallback
        
    except Exception as e:
        print(f"❌ Chatbot response test failed: {str(e)}")
        return False

if __name__ == "__main__":
    print("🚀 OpenAI API and Chatbot Test Suite")
    print("=" * 50)
    
    # Test API key
    api_works = test_openai_api()
    
    if api_works:
        # Test chatbot initialization
        chatbot_works = test_chatbot_initialization()
        
        if chatbot_works:
            # Test actual response
            ai_response = test_chatbot_response()
            
            if ai_response:
                print("\n🎉 All tests passed! Your chatbot should work with AI.")
            else:
                print("\n⚠️  API works but chatbot still using fallback responses.")
                print("   This might be a code issue.")
        else:
            print("\n❌ Chatbot initialization failed.")
    else:
        print("\n❌ API key issue. Please fix before testing chatbot.")
