import os
import json
import logging
from datetime import datetime
from typing import Dict, Any, Optional, List
from sqlalchemy import create_engine, Column, String, Text, DateTime, Integer, Float, JSON
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
import uuid

logger = logging.getLogger(__name__)

Base = declarative_base()

class Conversation(Base):
    """Conversation table matching the spreadsheet structure"""
    __tablename__ = 'conversations'
    
    # Primary key
    conversation_id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    
    # User information
    user_audience = Column(String(50))  # prospect, applicant, current_student
    user_intent = Column(String(100))   # application_status, financial_aid, etc.
    user_sub_intent = Column(String(100))  # deadlines, document_submission, etc.
    
    # Query details
    actual_query = Column(Text, nullable=False)
    bot_response = Column(Text, nullable=False)
    
    # Data source information
    data_sources_used = Column(JSON)  # List of URLs/sources
    response_method = Column(String(50))  # live_search, static_kb, fallback
    
    # Quality metrics
    response_quality_score = Column(Float, default=0.0)  # 0-1 scale
    user_satisfaction = Column(Integer)  # 1-5 scale if collected
    
    # Metadata
    timestamp = Column(DateTime, default=datetime.utcnow)
    session_id = Column(String(100))  # To group related conversations
    
    # Additional analytics
    response_time_ms = Column(Integer)  # Response generation time
    sources_count = Column(Integer, default=0)  # Number of sources used
    response_length = Column(Integer)  # Character count of response

class QueryAnalytics(Base):
    """Query pattern analytics table"""
    __tablename__ = 'query_analytics'
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    query_type = Column(String(100), nullable=False)
    frequency_count = Column(Integer, default=1)
    success_rate = Column(Float, default=0.0)
    avg_response_time = Column(Float, default=0.0)
    common_failure_patterns = Column(JSON)
    last_updated = Column(DateTime, default=datetime.utcnow)

class ConversationLogger:
    """Real-time conversation logging system for Bot 1"""
    
    def __init__(self, database_url: str = None):
        """Initialize the conversation logger with database connection"""
        if database_url is None:
            # Default to local PostgreSQL for development
            database_url = os.getenv('DATABASE_URL', 'postgresql://localhost/cuny_chatbot')
        
        try:
            self.engine = create_engine(database_url)
            self.SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=self.engine)
            
            # Create tables if they don't exist
            Base.metadata.create_all(bind=self.engine)
            
            logger.info("Conversation logger initialized successfully")
            
        except Exception as e:
            logger.error(f"Failed to initialize conversation logger: {e}")
            self.engine = None
            self.SessionLocal = None
    
    def log_conversation(self, 
                        user_query: str,
                        bot_response: str,
                        data_sources: List[str] = None,
                        response_method: str = "unknown",
                        user_audience: str = "unknown",
                        user_intent: str = "unknown",
                        user_sub_intent: str = "unknown",
                        response_time_ms: int = 0,
                        session_id: str = None,
                        user_satisfaction: int = None) -> str:
        """Log a conversation with all metadata"""
        
        if not self.engine:
            logger.warning("Database not available, skipping conversation log")
            return None
        
        try:
            # Generate conversation ID
            conversation_id = str(uuid.uuid4())
            
            # Calculate response quality score (simple heuristic)
            quality_score = self._calculate_quality_score(
                user_query, bot_response, data_sources, response_method
            )
            
            # Create conversation record
            conversation = Conversation(
                conversation_id=conversation_id,
                user_audience=user_audience,
                user_intent=user_intent,
                user_sub_intent=user_sub_intent,
                actual_query=user_query,
                bot_response=bot_response,
                data_sources_used=data_sources or [],
                response_method=response_method,
                response_quality_score=quality_score,
                user_satisfaction=user_satisfaction,
                response_time_ms=response_time_ms,
                session_id=session_id or str(uuid.uuid4()),
                sources_count=len(data_sources) if data_sources else 0,
                response_length=len(bot_response)
            )
            
            # Save to database
            session = self.SessionLocal()
            session.add(conversation)
            session.commit()
            session.close()
            
            # Update analytics
            self._update_query_analytics(user_intent, response_method, response_time_ms)
            
            logger.info(f"Conversation logged: {conversation_id}")
            return conversation_id
            
        except Exception as e:
            logger.error(f"Failed to log conversation: {e}")
            return None
    
    def _calculate_quality_score(self, 
                                user_query: str, 
                                bot_response: str, 
                                data_sources: List[str], 
                                response_method: str) -> float:
        """Calculate response quality score (0-1 scale)"""
        score = 0.0
        
        # Base score for having a response
        if bot_response and len(bot_response.strip()) > 0:
            score += 0.3
        
        # Bonus for live search (more current data)
        if response_method == "live_search":
            score += 0.3
        elif response_method == "static_kb":
            score += 0.2
        
        # Bonus for having data sources
        if data_sources and len(data_sources) > 0:
            score += 0.2
        
        # Bonus for detailed response (not too short, not too long)
        response_length = len(bot_response)
        if 50 <= response_length <= 1000:
            score += 0.2
        elif response_length > 1000:
            score += 0.1  # Slightly penalize very long responses
        
        # Penalty for generic responses
        generic_phrases = [
            "I don't have specific information",
            "Please check the website",
            "Contact the office",
            "I'm not sure about that"
        ]
        
        if any(phrase.lower() in bot_response.lower() for phrase in generic_phrases):
            score -= 0.2
        
        return max(0.0, min(1.0, score))  # Clamp between 0 and 1
    
    def _update_query_analytics(self, query_type: str, response_method: str, response_time_ms: int):
        """Update query analytics for pattern analysis"""
        if not self.engine:
            return
        
        try:
            session = self.SessionLocal()
            
            # Find existing analytics record
            analytics = session.query(QueryAnalytics).filter(
                QueryAnalytics.query_type == query_type
            ).first()
            
            if analytics:
                # Update existing record
                analytics.frequency_count += 1
                analytics.avg_response_time = (
                    (analytics.avg_response_time * (analytics.frequency_count - 1) + response_time_ms) 
                    / analytics.frequency_count
                )
                analytics.last_updated = datetime.utcnow()
            else:
                # Create new record
                analytics = QueryAnalytics(
                    query_type=query_type,
                    frequency_count=1,
                    avg_response_time=response_time_ms,
                    success_rate=1.0 if response_method != "fallback" else 0.0
                )
                session.add(analytics)
            
            session.commit()
            session.close()
            
        except Exception as e:
            logger.error(f"Failed to update query analytics: {e}")
    
    def get_conversation_stats(self, hours: int = 24) -> Dict[str, Any]:
        """Get conversation statistics for the last N hours"""
        if not self.engine:
            return {}
        
        try:
            session = self.SessionLocal()
            
            # Calculate time threshold
            time_threshold = datetime.utcnow() - timedelta(hours=hours)
            
            # Get basic stats
            total_conversations = session.query(Conversation).filter(
                Conversation.timestamp >= time_threshold
            ).count()
            
            avg_quality = session.query(Conversation).filter(
                Conversation.timestamp >= time_threshold
            ).with_entities(Conversation.response_quality_score).all()
            
            avg_quality_score = sum([q[0] for q in avg_quality]) / len(avg_quality) if avg_quality else 0
            
            # Get top intents
            top_intents = session.query(
                Conversation.user_intent,
                session.query(Conversation).filter(
                    Conversation.user_intent == Conversation.user_intent,
                    Conversation.timestamp >= time_threshold
                ).count().label('count')
            ).filter(
                Conversation.timestamp >= time_threshold
            ).group_by(Conversation.user_intent).order_by('count DESC').limit(5).all()
            
            session.close()
            
            return {
                'total_conversations': total_conversations,
                'avg_quality_score': round(avg_quality_score, 2),
                'top_intents': [{'intent': intent, 'count': count} for intent, count in top_intents],
                'time_period_hours': hours
            }
            
        except Exception as e:
            logger.error(f"Failed to get conversation stats: {e}")
            return {}
    
    def get_analytics_dashboard_data(self) -> Dict[str, Any]:
        """Get comprehensive analytics data for OAREDA dashboard"""
        if not self.engine:
            return {}
        
        try:
            session = self.SessionLocal()
            
            # Get all analytics
            analytics = session.query(QueryAnalytics).all()
            
            # Get recent conversations (last 7 days)
            week_ago = datetime.utcnow() - timedelta(days=7)
            recent_conversations = session.query(Conversation).filter(
                Conversation.timestamp >= week_ago
            ).all()
            
            # Process data for dashboard
            dashboard_data = {
                'query_patterns': [
                    {
                        'query_type': a.query_type,
                        'frequency': a.frequency_count,
                        'success_rate': a.success_rate,
                        'avg_response_time': a.avg_response_time
                    } for a in analytics
                ],
                'recent_activity': {
                    'total_conversations': len(recent_conversations),
                    'avg_quality_score': sum([c.response_quality_score for c in recent_conversations]) / len(recent_conversations) if recent_conversations else 0,
                    'response_methods': {}
                },
                'knowledge_gaps': self._identify_knowledge_gaps(recent_conversations)
            }
            
            # Count response methods
            for conv in recent_conversations:
                method = conv.response_method
                if method in dashboard_data['recent_activity']['response_methods']:
                    dashboard_data['recent_activity']['response_methods'][method] += 1
                else:
                    dashboard_data['recent_activity']['response_methods'][method] = 1
            
            session.close()
            return dashboard_data
            
        except Exception as e:
            logger.error(f"Failed to get analytics dashboard data: {e}")
            return {}
    
    def _identify_knowledge_gaps(self, conversations: List[Conversation]) -> List[Dict[str, Any]]:
        """Identify potential knowledge gaps based on conversation patterns"""
        gaps = []
        
        # Find queries with low quality scores
        low_quality = [c for c in conversations if c.response_quality_score < 0.3]
        
        if low_quality:
            gaps.append({
                'type': 'low_quality_responses',
                'count': len(low_quality),
                'description': f'{len(low_quality)} conversations had low quality scores',
                'sample_queries': [c.actual_query for c in low_quality[:3]]
            })
        
        # Find fallback responses (indicates missing knowledge)
        fallback_responses = [c for c in conversations if c.response_method == 'fallback']
        
        if fallback_responses:
            gaps.append({
                'type': 'fallback_responses',
                'count': len(fallback_responses),
                'description': f'{len(fallback_responses)} conversations used fallback responses',
                'sample_queries': [c.actual_query for c in fallback_responses[:3]]
            })
        
        return gaps

# Global logger instance
conversation_logger = ConversationLogger()

