# CUNY AI Assistant - Enrollment Chatbot

An AI-powered chatbot designed to provide instant, personalized guidance to prospective students about City University of New York (CUNY) colleges. This chatbot addresses the need for 24/7 enrollment support and helps reduce lead drop-offs by providing immediate, accurate information.

## 🎯 Problem Solved

- **Gen Z Expectations**: Modern students expect instant, personalized answers
- **Traditional Admissions**: Slow response times lead to student drop-offs
- **Lead Conversion**: Universities struggle to convert inquiries into applications
- **Information Access**: Students need quick access to comprehensive campus information

## ✨ Features

### 🤖 AI-Powered Responses
- **OpenAI Integration**: Uses GPT-3.5-turbo for intelligent, contextual responses
- **Knowledge Base**: Comprehensive CUNY-specific information database
- **Conversation Memory**: Maintains context across conversation turns
- **Fallback Responses**: Graceful handling when AI is unavailable

### 📚 Comprehensive Information Coverage
- **Admissions**: Requirements, deadlines, application process
- **Tuition & Fees**: Cost breakdown by residency status
- **Scholarships**: Merit-based and need-based financial aid
- **Campus Life**: Housing, meal plans, activities, safety
- **Academics**: Majors, class sizes, faculty information
- **Student Services**: Advising, career services, health services
- **Technology**: WiFi, computer labs, software access
- **Transportation**: Subway, bus, parking information

### 🎨 Modern User Interface
- **Responsive Design**: Works on desktop, tablet, and mobile
- **Real-time Chat**: Instant message exchange
- **Quick Questions**: Pre-built common questions for easy access
- **Loading Indicators**: Visual feedback during AI processing
- **Professional Design**: Clean, modern interface with CUNY branding

### 🔧 Technical Features
- **Flask Backend**: Python web framework for API endpoints
- **RESTful API**: Clean API design for easy integration
- **Error Handling**: Robust error handling and fallback mechanisms
- **Scalable Architecture**: Easy to extend and customize

## 🚀 Quick Start

### Prerequisites
- Python 3.8 or higher
- OpenAI API key
- Modern web browser

### Installation

1. **Clone the repository**
   ```bash
   git clone <repository-url>
   cd CUNY_Chatbot
   ```

2. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

3. **Set up environment variables**
   ```bash
   cp .env.example .env
   ```
   
   Edit `.env` file and add your OpenAI API key:
   ```
   OPENAI_API_KEY=your_openai_api_key_here
   ```

4. **Run the application**
   ```bash
   python app.py
   ```

5. **Access the chatbot**
   Open your browser and go to `http://localhost:5000`

## 📁 Project Structure

```
CUNY_Chatbot/
├── app.py                 # Main Flask application
├── chatbot.py            # AI chatbot logic
├── knowledge_base.py     # CUNY information database
├── requirements.txt      # Python dependencies
├── .env                  # Environment variables
├── README.md            # Project documentation
├── templates/
│   └── index.html       # Main chat interface
└── static/
    ├── css/
    │   └── style.css    # Styling and responsive design
    └── js/
        └── chat.js      # Frontend chat functionality
```

## 🎯 Usage Examples

### Sample Questions the Chatbot Can Answer:

**Admissions:**
- "What are the admission requirements for transfer students?"
- "When is the application deadline for fall semester?"
- "Do I need SAT scores for admission?"

**Financial Aid:**
- "What scholarships are available for international students?"
- "How much is tuition for NY residents?"
- "What financial aid options do I have?"

**Campus Life:**
- "What housing options are available?"
- "How safe is the campus?"
- "What student activities and clubs are there?"

**Academics:**
- "What majors are offered?"
- "How large are the class sizes?"
- "Do you offer online courses?"

## 🔧 Configuration

### Environment Variables

Create a `.env` file with the following variables:

```env
OPENAI_API_KEY=your_openai_api_key_here
FLASK_ENV=development
PORT=5000
```

### Customizing Knowledge Base

Edit `knowledge_base.py` to add or modify information:

```python
# Add new category
"new_category": {
    "subcategory": {
        "key": "value"
    }
}
```

### Styling Customization

Modify `static/css/style.css` to change the appearance:

```css
/* Change primary colors */
:root {
    --primary-color: #667eea;
    --secondary-color: #764ba2;
}
```

## 🚀 Deployment

### Local Development
```bash
python app.py
```

### Production Deployment
```bash
gunicorn -w 4 -b 0.0.0.0:5000 app:app
```

### Docker Deployment
```bash
docker build -t cuny-chatbot .
docker run -p 5000:5000 cuny-chatbot
```

## 🔌 API Endpoints

### Chat Endpoint
- **POST** `/api/chat`
- **Body**: `{"message": "user question", "history": []}`
- **Response**: `{"response": "ai response", "timestamp": "..."}`

### Quick Questions
- **GET** `/api/quick-questions`
- **Response**: `{"questions": ["question1", "question2", ...]}`

### Campus Information
- **GET** `/api/campus-info`
- **Response**: `{"name": "CUNY", "campuses": [...], ...}`

### Health Check
- **GET** `/health`
- **Response**: `{"status": "healthy", "timestamp": "..."}`

## 🎨 Customization

### Adding New Universities

1. **Update Knowledge Base**: Modify `knowledge_base.py` with new university data
2. **Update Branding**: Change colors, logos, and text in HTML/CSS
3. **Modify System Prompt**: Update the AI assistant's role in `chatbot.py`

### Extending Features

- **Database Integration**: Add persistent storage for conversations
- **Analytics**: Track user interactions and popular questions
- **Multi-language Support**: Add internationalization
- **Voice Integration**: Add speech-to-text capabilities
- **CRM Integration**: Connect with existing admission systems

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## 📄 License

This project is licensed under the MIT License - see the LICENSE file for details.

## 🙏 Acknowledgments

- OpenAI for providing the GPT API
- CUNY for the comprehensive information used in the knowledge base
- Flask community for the excellent web framework
- Font Awesome for the beautiful icons

## 📞 Support

For support and questions:
- Create an issue in the repository
- Contact the development team
- Check the documentation

---

**Built with ❤️ for better student experiences**
