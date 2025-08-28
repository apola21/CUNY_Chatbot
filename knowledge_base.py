import json
import pandas as pd
from typing import Dict, List, Any
import logging

logger = logging.getLogger(__name__)

class CUNYKnowledgeBase:
    """Knowledge base containing CUNY-specific information"""
    
    def __init__(self):
        self.data = self._load_knowledge_base()
        
    def _load_knowledge_base(self) -> Dict[str, Any]:
        """Load comprehensive CUNY knowledge base"""
        return {
            "admissions": {
                "requirements": {
                    "freshman": {
                        "gpa": "Minimum 2.0 GPA",
                        "sat": "SAT scores recommended but not required for most programs",
                        "transcript": "Official high school transcript required",
                        "essay": "Personal statement required",
                        "recommendations": "Letters of recommendation recommended"
                    },
                    "transfer": {
                        "credits": "Minimum 12 college credits",
                        "gpa": "Minimum 2.0 GPA",
                        "transcript": "Official college transcript required"
                    },
                    "international": {
                        "toefl": "TOEFL score of 80+ or IELTS 6.5+",
                        "transcript": "Official transcript with English translation",
                        "visa": "Valid student visa required"
                    }
                },
                "deadlines": {
                    "fall": "February 1st (priority), April 1st (regular)",
                    "spring": "September 15th",
                    "summer": "March 1st"
                },
                "application_fee": "$65 for most colleges"
            },
            
            "tuition_fees": {
                "undergraduate": {
                    "ny_resident": "$3,465 per semester",
                    "non_ny_resident": "$620 per credit",
                    "international": "$620 per credit"
                },
                "graduate": {
                    "ny_resident": "$5,545 per semester",
                    "non_ny_resident": "$855 per credit",
                    "international": "$855 per credit"
                },
                "additional_fees": {
                    "student_activity": "$15-25 per semester",
                    "technology": "$125 per semester",
                    "health_insurance": "$1,000+ per year (if not covered)"
                }
            },
            
            "scholarships": {
                "cuny_excellence": {
                    "amount": "Up to $6,500 per year",
                    "requirements": "3.5+ GPA, leadership activities",
                    "deadline": "March 1st"
                },
                "presidential_scholarship": {
                    "amount": "Full tuition coverage",
                    "requirements": "4.0 GPA, exceptional achievements",
                    "deadline": "February 1st"
                },
                "transfer_scholarship": {
                    "amount": "Up to $4,000 per year",
                    "requirements": "3.0+ GPA, 30+ transfer credits",
                    "deadline": "April 15th"
                },
                "need_based": {
                    "pell_grant": "Up to $6,895 per year",
                    "tap_grant": "Up to $5,665 per year (NY residents)",
                    "requirements": "FAFSA completion required"
                }
            },
            
            "campus_life": {
                "housing": {
                    "on_campus": "Limited availability, $8,000-12,000 per year",
                    "off_campus": "Various options in NYC, $1,200-2,500 per month",
                    "meal_plans": {
                        "basic": "$1,200 per semester",
                        "premium": "$2,000 per semester",
                        "flex": "Pay-as-you-go options available"
                    }
                },
                "activities": {
                    "clubs": "200+ student organizations",
                    "sports": "NCAA Division III athletics",
                    "cultural": "Diverse cultural events and celebrations",
                    "leadership": "Student government and leadership programs"
                },
                "safety": {
                    "campus_police": "24/7 campus security",
                    "escort_service": "Free campus escort service",
                    "emergency": "Blue light emergency phones throughout campus",
                    "crime_rate": "Low crime rate with active safety programs"
                }
            },
            
            "academics": {
                "majors": [
                    "Business Administration", "Computer Science", "Psychology",
                    "Biology", "English", "Mathematics", "History", "Political Science",
                    "Sociology", "Economics", "Engineering", "Education", "Nursing",
                    "Criminal Justice", "Media Studies", "Art", "Music", "Theater"
                ],
                "class_size": "Average 25 students per class",
                "faculty": "90% hold terminal degrees",
                "research": "Extensive undergraduate research opportunities",
                "internships": "Strong NYC internship connections"
            },
            
            "campus_tours": {
                "in_person": {
                    "schedule": "Monday-Friday, 10 AM and 2 PM",
                    "duration": "90 minutes",
                    "registration": "Required 48 hours in advance",
                    "group_size": "Maximum 15 students per tour"
                },
                "virtual": {
                    "availability": "24/7 online virtual tours",
                    "features": "360-degree campus views, student testimonials",
                    "registration": "Not required for virtual tours"
                }
            },
            
            "student_services": {
                "academic_advising": "Free academic counseling",
                "career_services": "Job placement assistance, resume help",
                "health_services": "On-campus health clinic",
                "counseling": "Free mental health counseling",
                "disability_services": "Comprehensive accommodation support",
                "tutoring": "Free peer and professional tutoring"
            },
            
            "technology": {
                "wifi": "Free campus-wide WiFi",
                "computer_labs": "24/7 computer lab access",
                "software": "Free Microsoft Office and Adobe Creative Suite",
                "online_learning": "Hybrid and online course options"
            },
            
            "transportation": {
                "subway": "Convenient access to NYC subway system",
                "bus": "Multiple bus routes serve all campuses",
                "parking": "Limited on-campus parking available",
                "bike": "Bike racks and storage facilities"
            }
        }
    
    def search(self, query: str) -> List[Dict[str, Any]]:
        """Search knowledge base for relevant information"""
        query_lower = query.lower()
        results = []
        
        # Search through all categories
        for category, data in self.data.items():
            if self._matches_category(query_lower, category):
                results.append({
                    'category': category,
                    'data': data,
                    'relevance': self._calculate_relevance(query_lower, data)
                })
        
        # Sort by relevance
        results.sort(key=lambda x: x['relevance'], reverse=True)
        return results[:5]  # Return top 5 most relevant results
    
    def _matches_category(self, query: str, category: str) -> bool:
        """Check if query matches a category"""
        category_keywords = {
            'admissions': ['admission', 'apply', 'application', 'requirements', 'deadline'],
            'tuition_fees': ['tuition', 'fee', 'cost', 'price', 'payment'],
            'scholarships': ['scholarship', 'financial aid', 'grant', 'money'],
            'campus_life': ['campus', 'life', 'housing', 'meal', 'activity', 'club'],
            'academics': ['major', 'class', 'course', 'academic', 'study'],
            'campus_tours': ['tour', 'visit', 'campus tour', 'virtual'],
            'student_services': ['service', 'help', 'support', 'advising'],
            'technology': ['wifi', 'computer', 'technology', 'software'],
            'transportation': ['transport', 'subway', 'bus', 'parking']
        }
        
        if category in category_keywords:
            return any(keyword in query for keyword in category_keywords[category])
        return False
    
    def _calculate_relevance(self, query: str, data: Any) -> float:
        """Calculate relevance score for search results"""
        if isinstance(data, dict):
            text = ' '.join(str(v) for v in data.values())
        elif isinstance(data, list):
            text = ' '.join(str(item) for item in data)
        else:
            text = str(data)
        
        text_lower = text.lower()
        relevance = 0.0
        
        # Simple keyword matching
        query_words = query.split()
        for word in query_words:
            if word in text_lower:
                relevance += 1.0
        
        return relevance
    
    def get_specific_info(self, category: str, subcategory: str = None) -> Any:
        """Get specific information from knowledge base"""
        if category not in self.data:
            return None
        
        if subcategory:
            return self.data[category].get(subcategory)
        
        return self.data[category]
