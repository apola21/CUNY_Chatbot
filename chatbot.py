import openai
import os
import json
import logging
from typing import List, Dict, Any
from knowledge_base import CUNYKnowledgeBase

logger = logging.getLogger(__name__)

class CUNYChatbot:
    """AI-powered chatbot for CUNY enrollment and information"""
    
    def __init__(self, knowledge_base: CUNYKnowledgeBase):
        self.knowledge_base = knowledge_base
        # Initialize OpenAI client only if API key is available
        api_key = os.getenv('OPENAI_API_KEY')
        if api_key and api_key != 'your_openai_api_key_here':
            try:
                self.openai_client = openai.OpenAI(api_key=api_key)
                self.has_openai = True
            except Exception as e:
                logger.warning(f"Failed to initialize OpenAI client: {e}")
                self.has_openai = False
        else:
            self.has_openai = False
            self.openai_client = None
        
        # System prompt that defines the chatbot's role and capabilities
        self.system_prompt = """You are CUNY (City University of New York) AI Assistant, a helpful and knowledgeable enrollment advisor. Your role is to provide accurate, helpful, and personalized information to prospective students about CUNY colleges.

Key responsibilities:
- Answer questions about admissions, tuition, scholarships, campus life, academics, and student services
- Provide specific, accurate information from the CUNY knowledge base
- Be friendly, professional, and encouraging
- Help students understand the application process and requirements
- Offer guidance on financial aid and scholarship opportunities
- Share information about campus facilities, activities, and student life
- Direct students to appropriate resources when needed

Important guidelines:
- Always provide accurate information based on the knowledge base
- Be encouraging and supportive of students' educational goals
- If you don't have specific information, suggest contacting the admissions office
- Keep responses concise but informative
- Use a warm, welcoming tone
- Encourage students to visit campus or take virtual tours
- Mention relevant deadlines and important dates when appropriate

Remember: You're helping students make one of the most important decisions of their lives - be supportive and informative!"""

    def get_response(self, user_message: str, conversation_history: List[Dict[str, str]] = None) -> str:
        """Generate a response to user message using OpenAI and knowledge base"""
        try:
            # Search knowledge base for relevant information
            kb_results = self.knowledge_base.search(user_message)
            
            # If OpenAI is available, try to use it
            if self.has_openai and self.openai_client:
                # Prepare context from knowledge base
                context = self._prepare_context(kb_results)
                
                # Prepare conversation history
                messages = self._prepare_messages(user_message, conversation_history, context)
                
                # Generate response using OpenAI
                response = self._generate_openai_response(messages)
                return response
            else:
                # Use fallback response if OpenAI is not available
                return self._get_fallback_response(user_message)
            
        except Exception as e:
            logger.error(f"Error generating response: {str(e)}")
            return self._get_fallback_response(user_message)
    
    def _prepare_context(self, kb_results: List[Dict[str, Any]]) -> str:
        """Prepare context from knowledge base search results"""
        if not kb_results:
            return "No specific information found in knowledge base."
        
        context_parts = []
        for result in kb_results:
            category = result['category']
            data = result['data']
            
            # Format the data for context
            if isinstance(data, dict):
                formatted_data = self._format_dict_for_context(data)
            elif isinstance(data, list):
                formatted_data = ", ".join(str(item) for item in data)
            else:
                formatted_data = str(data)
            
            context_parts.append(f"{category.replace('_', ' ').title()}: {formatted_data}")
        
        return "\n\n".join(context_parts)
    
    def _format_dict_for_context(self, data: Dict[str, Any], indent: int = 0) -> str:
        """Format dictionary data for context"""
        parts = []
        for key, value in data.items():
            if isinstance(value, dict):
                formatted_value = self._format_dict_for_context(value, indent + 1)
                parts.append(f"{key.replace('_', ' ').title()}: {formatted_value}")
            elif isinstance(value, list):
                formatted_value = ", ".join(str(item) for item in value)
                parts.append(f"{key.replace('_', ' ').title()}: {formatted_value}")
            else:
                parts.append(f"{key.replace('_', ' ').title()}: {value}")
        
        return "; ".join(parts)
    
    def _prepare_messages(self, user_message: str, conversation_history: List[Dict[str, str]], context: str) -> List[Dict[str, str]]:
        """Prepare messages for OpenAI API"""
        messages = [
            {"role": "system", "content": self.system_prompt + f"\n\nRelevant information from CUNY knowledge base:\n{context}"}
        ]
        
        # Add conversation history
        if conversation_history:
            for msg in conversation_history[-6:]:  # Keep last 6 messages for context
                if msg.get('role') == 'user':
                    messages.append({"role": "user", "content": msg.get('content', '')})
                elif msg.get('role') == 'assistant':
                    messages.append({"role": "assistant", "content": msg.get('content', '')})
        
        # Add current user message
        messages.append({"role": "user", "content": user_message})
        
        return messages
    
    def _generate_openai_response(self, messages: List[Dict[str, str]]) -> str:
        """Generate response using OpenAI API"""
        try:
            response = self.openai_client.chat.completions.create(
                model="gpt-4o-mini",  # Latest and most capable model
                messages=messages,
                max_tokens=1000,      # Increased for more detailed responses
                temperature=0.7,
                top_p=0.9
            )
            
            return response.choices[0].message.content.strip()
            
        except Exception as e:
            logger.error(f"OpenAI API error: {str(e)}")
            raise e
    
    def _get_fallback_response(self, user_message: str) -> str:
        """Provide fallback response when AI generation fails"""
        fallback_responses = [
            "I'm here to help you with CUNY information! Could you please rephrase your question?",
            "I'd be happy to help you learn more about CUNY. What specific information are you looking for?",
            "Let me help you find the information you need about CUNY. Could you tell me more about what you're interested in?",
            "I'm your CUNY assistant! I can help with admissions, tuition, campus life, and more. What would you like to know?",
            "Welcome to CUNY! I'm here to answer your questions about our colleges and programs. What can I help you with today?"
        ]
        
        # Simple keyword-based fallback
        user_lower = user_message.lower()
        
        if any(word in user_lower for word in ['admission', 'apply', 'application']):
            return "I can help you with CUNY admissions! For the most current application requirements and deadlines, I recommend visiting the specific college's website or contacting their admissions office directly. Would you like to know about general admission requirements?"
        
        elif any(word in user_lower for word in ['tuition', 'cost', 'fee', 'price']):
            return "CUNY offers affordable education! Tuition varies by residency status and program level. NY residents typically pay around $3,465 per semester for undergraduate programs. Would you like more specific information about tuition and fees?"
        
        elif any(word in user_lower for word in ['scholarship', 'financial aid', 'money']):
            return "CUNY offers many scholarship and financial aid opportunities! We have merit-based scholarships, need-based grants, and work-study programs. Have you completed the FAFSA? That's the first step for most financial aid."
        
        elif any(word in user_lower for word in ['campus', 'tour', 'visit']):
            return "I'd love to help you plan a campus visit! Most CUNY colleges offer both in-person and virtual tours. Would you like information about scheduling a tour or taking a virtual campus tour?"
        
        else:
            return fallback_responses[hash(user_message) % len(fallback_responses)]
    
    def get_quick_response(self, question_type: str) -> str:
        """Get quick response for common question types"""
        quick_responses = {
            "admissions": "CUNY has rolling admissions with priority deadlines. You'll need transcripts, personal statement, and letters of recommendation. Application fee is $65. Would you like specific requirements for your program?",
            "tuition": "CUNY tuition is very affordable! NY residents pay about $3,465 per semester for undergraduate programs. Non-residents pay $620 per credit. Plus there are many scholarship opportunities!",
            "scholarships": "CUNY offers excellent scholarships! We have merit-based awards up to $6,500/year, Presidential Scholarships for full tuition, and need-based grants. Have you completed your FAFSA?",
            "campus_life": "CUNY campuses offer vibrant student life! We have 200+ clubs, NCAA sports, cultural events, and leadership programs. Housing options include on-campus and off-campus arrangements. What interests you most?",
            "majors": "CUNY offers 100+ majors across all campuses! Popular programs include Business, Computer Science, Psychology, Engineering, and Education. What field interests you? I can help you find the right program!"
        }
        
        return quick_responses.get(question_type, "I'm here to help! What would you like to know about CUNY?")
