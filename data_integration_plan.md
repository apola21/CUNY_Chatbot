# Agentic AI Development Plan for CUNY Chatbot

## Current State → Agentic AI Roadmap

### Phase 1: Data Source Integration (Weeks 1-2)

#### 1.1 Web Scraping Infrastructure
```python
# Tools needed:
- BeautifulSoup4 (already installed)
- Selenium (for dynamic content)
- Scrapy (for large-scale scraping)
- Requests (for API calls)
```

#### 1.2 Document Processing
```python
# Tools needed:
- PyPDF2 / pdfplumber (PDF processing)
- python-docx (Word documents)
- openpyxl (Excel files)
- unstructured (general document parsing)
```

#### 1.3 Social Media Integration
```python
# APIs needed:
- Twitter API (X)
- Instagram Basic Display API
- Facebook Graph API
- LinkedIn API
```

### Phase 2: Agentic Framework (Weeks 3-4)

#### 2.1 Tool Registry
```python
class AgenticTools:
    def __init__(self):
        self.tools = {
            "web_search": self.search_website,
            "read_pdf": self.extract_pdf_content,
            "get_social_media": self.fetch_social_posts,
            "check_database": self.query_database,
            "send_email": self.send_notification
        }
```

#### 2.2 Action Planning
```python
class ActionPlanner:
    def plan_actions(self, user_query):
        # Analyze query and determine required actions
        # Example: "What's the latest scholarship deadline?"
        # Actions: [search_website, check_database, format_response]
```

#### 2.3 Memory System
```python
class AgentMemory:
    def __init__(self):
        self.action_history = []
        self.data_cache = {}
        self.user_context = {}
```

### Phase 3: Real Data Sources (Weeks 5-6)

#### 3.1 University Website Integration
```python
# Target websites:
- cuny.edu (main website)
- Individual college websites (baruch.cuny.edu, hunter.cuny.edu)
- Admissions pages
- Financial aid pages
- Course catalogs
```

#### 3.2 Document Repository
```python
# Document types:
- Course catalogs (PDF)
- Student handbooks (PDF)
- Financial aid guides (PDF)
- Application forms (PDF)
- Policy documents (PDF)
```

#### 3.3 Social Media Monitoring
```python
# Social platforms:
- CUNY official accounts
- Individual college accounts
- Student life accounts
- Event announcements
- Deadline reminders
```

### Phase 4: Agentic Capabilities (Weeks 7-8)

#### 4.1 Autonomous Actions
```python
class AgenticChatbot:
    def handle_query(self, user_query):
        # 1. Analyze query intent
        intent = self.analyze_intent(user_query)
        
        # 2. Plan required actions
        actions = self.plan_actions(intent)
        
        # 3. Execute actions
        results = []
        for action in actions:
            result = self.execute_action(action)
            results.append(result)
        
        # 4. Synthesize response
        response = self.synthesize_response(results)
        
        # 5. Update memory
        self.update_memory(user_query, actions, results)
        
        return response
```

#### 4.2 Tool Usage Examples
```python
# Example 1: Scholarship Deadline Query
def handle_scholarship_deadline(self, query):
    actions = [
        "search_website('cuny.edu/scholarships')",
        "read_pdf('scholarship_guide_2024.pdf')",
        "check_social_media('@CUNY')",
        "format_deadline_info()"
    ]
    return self.execute_actions(actions)

# Example 2: Course Information Query
def handle_course_info(self, query):
    actions = [
        "search_website('catalog.cuny.edu')",
        "read_pdf('course_catalog_2024.pdf')",
        "check_prerequisites()",
        "format_course_info()"
    ]
    return self.execute_actions(actions)
```

### Phase 5: Advanced Features (Weeks 9-10)

#### 5.1 Proactive Monitoring
```python
class ProactiveAgent:
    def monitor_changes(self):
        # Monitor website changes
        # Check for new documents
        # Track social media updates
        # Alert users about relevant changes
```

#### 5.2 Predictive Actions
```python
class PredictiveAgent:
    def predict_user_needs(self, user_profile):
        # Based on user history, predict what they might need
        # Proactively gather information
        # Suggest relevant actions
```

#### 5.3 Multi-Step Reasoning
```python
class ReasoningAgent:
    def complex_query_handler(self, query):
        # Break complex queries into steps
        # Execute each step
        # Combine results
        # Provide comprehensive answer
```

## Implementation Timeline

### Week 1-2: Foundation
- [ ] Set up web scraping infrastructure
- [ ] Implement document processing
- [ ] Create basic tool registry

### Week 3-4: Agentic Framework
- [ ] Build action planning system
- [ ] Implement memory management
- [ ] Create tool execution engine

### Week 5-6: Data Integration
- [ ] Integrate CUNY websites
- [ ] Process course catalogs and documents
- [ ] Set up social media monitoring

### Week 7-8: Agentic Capabilities
- [ ] Implement autonomous actions
- [ ] Add tool usage examples
- [ ] Test with real queries

### Week 9-10: Advanced Features
- [ ] Add proactive monitoring
- [ ] Implement predictive actions
- [ ] Enhance reasoning capabilities

## Technical Requirements

### New Dependencies
```python
# Add to requirements.txt
selenium==4.15.0
scrapy==2.11.0
PyPDF2==3.0.1
python-docx==1.1.0
openpyxl==3.1.2
unstructured==0.10.30
tweepy==4.14.0
facebook-sdk==3.1.0
linkedin-api==2.0.0
```

### Infrastructure Needs
- **Database**: PostgreSQL for storing scraped data
- **Caching**: Redis for fast data access
- **Scheduling**: Celery for background tasks
- **Monitoring**: Sentry for error tracking

## Success Metrics

### Technical Metrics
- **Response Accuracy**: 95%+ accurate information
- **Response Time**: < 5 seconds for complex queries
- **Data Freshness**: < 24 hours for critical information
- **Tool Success Rate**: 90%+ successful tool executions

### Business Metrics
- **User Satisfaction**: Improved response quality
- **Query Resolution**: Higher first-contact resolution
- **Information Accuracy**: Reduced outdated information
- **User Engagement**: More complex queries handled

## Risk Mitigation

### Technical Risks
- **Website Changes**: Implement robust scraping with fallbacks
- **API Rate Limits**: Implement rate limiting and caching
- **Data Quality**: Add validation and verification steps
- **Performance**: Optimize tool execution and caching

### Legal/Compliance Risks
- **Terms of Service**: Respect website terms and robots.txt
- **Data Privacy**: Implement proper data handling
- **Copyright**: Ensure proper attribution and usage rights
- **Accessibility**: Maintain accessibility standards

