from flask import Flask, request, jsonify, render_template
from flask_cors import CORS
import os
import json
import openai
from datetime import datetime
import logging
from knowledge_base import CUNYKnowledgeBase
from chatbot import CUNYChatbot

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = Flask(__name__)
CORS(app)

# Initialize OpenAI client
openai.api_key = os.getenv('OPENAI_API_KEY')

# Initialize knowledge base and chatbot
knowledge_base = CUNYKnowledgeBase()
chatbot = CUNYChatbot(knowledge_base)

@app.route('/')
def index():
    """Serve the main chat interface"""
    return render_template('index.html')

@app.route('/api/chat', methods=['POST'])
def chat():
    """Handle chat messages"""
    try:
        data = request.get_json()
        user_message = data.get('message', '')
        conversation_history = data.get('history', [])
        
        if not user_message.strip():
            return jsonify({'error': 'Message cannot be empty'}), 400
        
        # Get response from chatbot
        response = chatbot.get_response(user_message, conversation_history)
        
        return jsonify({
            'response': response,
            'timestamp': datetime.now().isoformat()
        })
        
    except Exception as e:
        logger.error(f"Error in chat endpoint: {str(e)}")
        return jsonify({'error': 'Internal server error'}), 500

@app.route('/api/quick-questions', methods=['GET'])
def get_quick_questions():
    """Get common questions for quick access"""
    quick_questions = [
        "What are the admission requirements?",
        "How much is tuition?",
        "What scholarships are available?",
        "When are the application deadlines?",
        "What majors are offered?",
        "How do I schedule a campus tour?",
        "What housing options are available?",
        "What meal plans are offered?",
        "How safe is the campus?",
        "What student activities are available?"
    ]
    return jsonify({'questions': quick_questions})

@app.route('/api/campus-info', methods=['GET'])
def get_campus_info():
    """Get basic campus information"""
    campus_info = {
        'name': 'City University of New York (CUNY)',
        'campuses': [
            'Baruch College',
            'Brooklyn College', 
            'City College',
            'Hunter College',
            'Queens College',
            'Lehman College',
            'College of Staten Island',
            'York College',
            'Medgar Evers College',
            'John Jay College of Criminal Justice'
        ],
        'total_students': '275,000+',
        'founded': '1847',
        'type': 'Public University System'
    }
    return jsonify(campus_info)

@app.route('/health', methods=['GET'])
def health_check():
    """Health check endpoint"""
    return jsonify({'status': 'healthy', 'timestamp': datetime.now().isoformat()})



if __name__ == '__main__':
    port = int(os.environ.get('PORT', 8080))
    app.run(host='0.0.0.0', port=port, debug=True)
