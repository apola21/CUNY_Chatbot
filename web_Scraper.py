import requests
from bs4 import BeautifulSoup
from urllib.parse import urljoin, urlparse
from collections import deque
import re
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
import numpy as np
import os
import openai  # For integrating GenAI service like OpenAI
import urllib.robotparser as rp
import json
import time
from datetime import datetime, timedelta
import hashlib
from typing import List, Dict, Any, Optional

# Set your OpenAI API key here (obtain from https://platform.openai.com/account/api-keys)
openai.api_key = os.environ["OPENAI_API_KEY"]

# Google Custom Search Engine Configuration
# Get these from: https://developers.google.com/custom-search/v1/introduction
GOOGLE_API_KEY = os.environ.get("GOOGLE_API_KEY", "")
GOOGLE_CSE_ID = os.environ.get("GOOGLE_CSE_ID", "")

# Search configuration
MAX_SEARCH_RESULTS = 10
MAX_SNIPPET_LENGTH = 500

# CUNY Domain Whitelist - Only crawl these domains for safety
CUNY_WHITELIST = (
    r".*\.cuny\.edu$",
    r".*\.baruch\.cuny\.edu$",
    r".*\.hunter\.cuny\.edu$",
    r".*\.citytech\.cuny\.edu$",
    r".*\.ccny\.cuny\.edu$",
    r".*\.brooklyn\.cuny\.edu$",
    r".*\.queens\.cuny\.edu$",
    r".*\.lehman\.cuny\.edu$",
    r".*\.csi\.cuny\.edu$",
    r".*\.york\.cuny\.edu$",
    r".*\.mec\.cuny\.edu$",
    r".*\.jjay\.cuny\.edu$",
)

# External Data Sources Whitelist
EXTERNAL_WHITELIST = (
    r".*\.nces\.ed\.gov$",
    r".*\.ope\.ed\.gov$", 
    r".*\.princetonreview\.com$",
    r".*\.usnews\.com$",
    r".*\.niche\.com$",
    r".*\.cccse\.org$",
)

# Cache settings
CACHE_FILE = "cuny_scraper_cache.json"
CACHE_EXPIRY_HOURS = 24  # Cache expires after 24 hours

def is_cuny_domain(url):
    """Check if URL is from a whitelisted CUNY domain."""
    host = urlparse(url).netloc.lower()
    return any(re.fullmatch(pat, host) for pat in CUNY_WHITELIST)

def is_external_domain(url):
    """Check if URL is from a whitelisted external data source."""
    host = urlparse(url).netloc.lower()
    return any(re.fullmatch(pat, host) for pat in EXTERNAL_WHITELIST)

def is_whitelisted_domain(url):
    """Check if URL is from any whitelisted domain (CUNY or external)."""
    return is_cuny_domain(url) or is_external_domain(url)

def check_robots_txt(url):
    """Check if URL is allowed by robots.txt."""
    parsed = urlparse(url)
    robots_url = f"{parsed.scheme}://{parsed.netloc}/robots.txt"
    rparser = rp.RobotFileParser()
    try:
        rparser.set_url(robots_url)
        rparser.read()
        user_agent = 'Mozilla/5.0 (compatible; CUNYChatbotScraper/1.0)'
        return rparser.can_fetch(user_agent, url)
    except Exception:
        # If robots.txt fails to load, default to allow for whitelisted domains
        return is_whitelisted_domain(url)

def load_cache():
    """Load cached content if it exists and is not expired."""
    if not os.path.exists(CACHE_FILE):
        return None
    
    try:
        with open(CACHE_FILE, 'r', encoding='utf-8') as f:
            cache_data = json.load(f)
        
        # Check if cache is expired
        cache_time = datetime.fromisoformat(cache_data.get('timestamp', ''))
        if datetime.now() - cache_time > timedelta(hours=CACHE_EXPIRY_HOURS):
            print("Cache expired, will re-crawl...")
            return None
        
        print(f"Loading cached content from {cache_time.strftime('%Y-%m-%d %H:%M:%S')}")
        return cache_data.get('content', {})
    except Exception as e:
        print(f"Error loading cache: {e}")
        return None

def save_cache(content):
    """Save content to cache with timestamp."""
    try:
        cache_data = {
            'timestamp': datetime.now().isoformat(),
            'content': content
        }
        with open(CACHE_FILE, 'w', encoding='utf-8') as f:
            json.dump(cache_data, f, ensure_ascii=False, indent=2)
        print(f"Content cached to {CACHE_FILE}")
    except Exception as e:
        print(f"Error saving cache: {e}")

def search_cuny_pages(query: str, num_results: int = MAX_SEARCH_RESULTS) -> List[Dict[str, Any]]:
    """Search for CUNY pages using Google Custom Search Engine or fallback method."""
    
    # Try Google CSE first if credentials are available
    if GOOGLE_API_KEY and GOOGLE_CSE_ID:
        return search_with_google_cse(query, num_results)
    else:
        print("Google API credentials not set. Using free fallback search.")
        return search_with_fallback(query, num_results)

def search_with_google_cse(query: str, num_results: int) -> List[Dict[str, Any]]:
    """Search using Google Custom Search Engine API."""
    # Create broader search query for CUNY and external sources
    search_query = f"(site:cuny.edu OR site:nces.ed.gov OR site:usnews.com OR site:niche.com OR site:princetonreview.com) {query}"
    
    try:
        search_url = "https://www.googleapis.com/customsearch/v1"
        params = {
            'key': GOOGLE_API_KEY,
            'cx': GOOGLE_CSE_ID,
            'q': search_query,
            'num': min(num_results, 10),
            'fields': 'items(title,link,snippet)'
        }
        
        response = requests.get(search_url, params=params, timeout=10)
        response.raise_for_status()
        
        data = response.json()
        results = []
        
        for item in data.get('items', []):
            url = item.get('link', '')
            if is_whitelisted_domain(url):
                results.append({
                    'title': item.get('title', ''),
                    'url': url,
                    'snippet': item.get('snippet', ''),
                    'relevance_score': 1.0
                })
        
        print(f"Found {len(results)} relevant pages via Google CSE for query: {query}")
        return results
        
    except Exception as e:
        print(f"Error with Google CSE: {e}")
        return []

def search_with_fallback(query: str, num_results: int) -> List[Dict[str, Any]]:
    """Intelligent fallback search that dynamically discovers relevant pages for ANY topic."""
    
    # Comprehensive CUNY admissions pages covering ALL aspects
    core_cuny_pages = [
        # Main CUNY admissions
        "https://www.cuny.edu/admissions/undergraduate/",
        "https://www.cuny.edu/admissions/graduate-studies/",
        "https://www.cuny.edu/admissions/undergraduate/apply/",
        "https://www.cuny.edu/admissions/undergraduate/transfer/",
        "https://www.cuny.edu/admissions/undergraduate/apply/application-review/",
        "https://www.cuny.edu/admissions/undergraduate/apply/credit/",
        "https://www.cuny.edu/admissions/undergraduate/apply/academic-profiles/",
        "https://www.cuny.edu/admissions/undergraduate/apply/cuny-application/",
        "https://www.cuny.edu/admissions/undergraduate/honors/",
        "https://www.cuny.edu/admissions/undergraduate/programs/",
        "https://www.cuny.edu/admissions/undergraduate/tours/",
        "https://www.cuny.edu/admissions/undergraduate/student-life/",
        "https://www.cuny.edu/admissions/undergraduate/downloads/",
        "https://www.cuny.edu/admissions/undergraduate/closed-academic-programs/",
        
        # Financial aid and costs
        "https://www.cuny.edu/financial-aid/",
        "https://www.cuny.edu/financial-aid/tuition-and-college-costs/",
        "https://www.cuny.edu/financial-aid/tuition-and-college-costs/tuition-fees/",
        
        # Academic programs
        "https://www.cuny.edu/academics/academic-programs/",
        "https://www.cuny.edu/academics/academic-programs/seek-college-discovery/",

        #academic research
        "https://www.cuny.edu/about/administration/offices/oareda/"
        
        # Individual college admissions
        "https://hunter.cuny.edu/admissions/undergraduate/",
        "https://hunter.cuny.edu/admissions/graduate-admissions/",
        "https://baruch.cuny.edu/admissions/",
        "https://www.ccny.cuny.edu/admissions",
        "https://www.brooklyn.cuny.edu/admissions",
        "https://www.queens.cuny.edu/admissions",
        "https://www.lehman.cuny.edu/admissions",
        "https://www.csi.cuny.edu/admissions",
        "https://york.cuny.edu/admissions",
        "https://www.mec.cuny.edu/admissions",
        "https://www.jjay.cuny.edu/admissions",
        
        # Law school
        "https://www.law.cuny.edu/admissions/",
        "https://www.law.cuny.edu/admissions/application-process/",
        "https://www.law.cuny.edu/admissions/requirements/",
        
        # International students
        "https://www.cuny.edu/academics/academic-programs/international-education/isss/",
        
        # Veterans
        "https://www.cuny.edu/about/university-resources/veterans-affairs/veterans-admissions/",
        
        # Reconnect program
        "https://www.cuny.edu/admissions/reconnect/"
    ]
    
    # External data sources for rankings and statistics
    external_sources = [
        "https://www.usnews.com/best-colleges/rankings/first-year-experience-programs",
        "https://www.princetonreview.com/college-rankings/",
        "https://www.niche.com/colleges/search/best-student-life/",
        "https://nces.ed.gov/ipeds",
        "https://ope.ed.gov/campussafety/#/institution/search"
    ]
    
    # Combine all potential sources
    all_pages = core_cuny_pages + external_sources
    
    query_lower = query.lower()
    query_words = set(query_lower.split())
    relevant_pages = []
    
    print(f"🔍 Intelligently searching {len(all_pages)} pages for: {query}")
    
    for url in all_pages:
        try:
            headers = {'User-Agent': 'Mozilla/5.0 (compatible; CUNYChatbotScraper/1.0)'}
            response = requests.get(url, headers=headers, timeout=8)
            
            if response.status_code == 200:
                soup = BeautifulSoup(response.text, 'html.parser')
                title = soup.title.string.strip() if soup.title and soup.title.string else ""
                page_text = soup.get_text().lower()
                
                # Intelligent relevance scoring
                relevance_score = calculate_intelligent_relevance(query_lower, query_words, page_text, url, title)
                
                if relevance_score > 0.1:  # Only include relevant pages
                    relevant_pages.append({
                        'title': title,
                        'url': url,
                        'snippet': f"Relevant content: {title}",
                        'relevance_score': relevance_score
                    })
        
        except Exception as e:
            print(f"Error checking {url}: {e}")
            continue
    
    # Sort by relevance and return top results
    relevant_pages.sort(key=lambda x: x['relevance_score'], reverse=True)
    print(f"Found {len(relevant_pages)} relevant pages via intelligent search for query: {query}")
    return relevant_pages[:num_results]

def calculate_intelligent_relevance(query_lower: str, query_words: set, page_text: str, url: str, title: str) -> float:
    """Calculate intelligent relevance score for any query and page combination."""
    
    base_score = 0.0
    
    # 1. Direct word matches
    word_matches = sum(1 for word in query_words if word in page_text)
    if word_matches > 0:
        base_score += (word_matches / len(query_words)) * 0.4
    
    # 2. Phrase matches (boost for exact phrases)
    query_phrases = [phrase.strip() for phrase in query_lower.split() if len(phrase) > 3]
    for phrase in query_phrases:
        if phrase in page_text:
            base_score += 0.3
    
    # 3. Program-specific boosting
    program_keywords = {
        'computer science': ['computer', 'cs', 'programming', 'software', 'technology'],
        'engineering': ['engineering', 'engineer', 'mechanical', 'electrical', 'civil'],
        'business': ['business', 'management', 'finance', 'marketing', 'accounting'],
        'nursing': ['nursing', 'nurse', 'healthcare', 'medical', 'clinical'],
        'psychology': ['psychology', 'psych', 'mental', 'behavioral', 'counseling'],
        'education': ['education', 'teaching', 'teacher', 'pedagogy', 'curriculum'],
        'law': ['law', 'legal', 'attorney', 'jurisprudence', 'court'],
        'medicine': ['medicine', 'medical', 'doctor', 'physician', 'healthcare'],
        'art': ['art', 'design', 'creative', 'visual', 'fine arts'],
        'science': ['science', 'biology', 'chemistry', 'physics', 'research']
    }
    
    for program, keywords in program_keywords.items():
        if any(word in query_lower for word in [program] + keywords):
            if any(keyword in page_text for keyword in keywords):
                base_score += 0.5  # Significant boost for program matches
    
    # 4. URL and title relevance
    if any(word in url.lower() for word in query_words):
        base_score += 0.3
    if any(word in title.lower() for word in query_words):
        base_score += 0.2
    
    # 5. Content type boosting
    if any(word in query_lower for word in ['admission', 'apply', 'requirement']):
        if any(word in page_text for word in ['admission', 'application', 'requirement', 'deadline']):
            base_score += 0.4
    
    if any(word in query_lower for word in ['tuition', 'cost', 'fee', 'price']):
        if any(word in page_text for word in ['tuition', 'cost', 'fee', '$', 'financial']):
            base_score += 0.4
    
    if any(word in query_lower for word in ['rank', 'ranking', 'rate', 'statistic']):
        if any(word in page_text for word in ['rank', 'ranking', '#', 'percent', '%']):
            base_score += 0.4
    
    # 6. Penalize irrelevant content
    if any(word in page_text for word in ['404', 'not found', 'error', 'page not available']):
        base_score *= 0.1
    
    return min(base_score, 2.0)  # Cap at 2.0

def fetch_and_parse_page(url: str) -> Optional[Dict[str, Any]]:
    """Fetch and parse a single page, returning structured content."""
    if not is_whitelisted_domain(url) or not check_robots_txt(url):
        return None
    
    try:
        headers = {'User-Agent': 'Mozilla/5.0 (compatible; CUNYChatbotScraper/1.0)'}
        response = requests.get(url, headers=headers, timeout=10)
        response.raise_for_status()
        
        soup = BeautifulSoup(response.text, 'html.parser')
        
        # Extract structured content
        title = soup.title.string.strip() if soup.title and soup.title.string else ""
        
        # Remove unwanted elements
        for tag in soup(["script", "style", "noscript", "header", "footer", "nav", "aside"]):
            tag.decompose()
        
        # Extract main content
        content_sections = []
        for tag in soup.find_all(['p', 'h1', 'h2', 'h3', 'h4', 'h5', 'h6', 'li', 'div']):
            if tag.text and len(tag.text.strip()) > 20:
                content_sections.append({
                    'tag': tag.name,
                    'text': clean_text(tag.text),
                    'relevance_score': 0.0
                })
        
        return {
            'url': url,
            'title': title,
            'content_sections': content_sections,
            'full_text': ' '.join([section['text'] for section in content_sections]),
            'timestamp': datetime.now().isoformat()
        }
        
    except Exception as e:
        print(f"Error fetching page {url}: {e}")
        return None

def rank_content_relevance(query: str, content_sections: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    """Rank content sections by relevance to the query with improved scoring."""
    if not content_sections:
        return []
    
    # Enhanced keyword-based scoring
    query_words = set(query.lower().split())
    
    # Define topic-specific keywords for better relevance
    topic_keywords = {
        'law': ['law', 'legal', 'attorney', 'court', 'justice', 'jurisprudence'],
        'admission': ['admission', 'apply', 'application', 'requirement', 'deadline'],
        'tuition': ['tuition', 'cost', 'fee', 'price', 'financial'],
        'program': ['program', 'degree', 'major', 'course', 'curriculum']
    }
    
    for section in content_sections:
        text_words = set(section['text'].lower().split())
        text_lower = section['text'].lower()
        
        # Calculate base word overlap
        word_overlap = len(query_words.intersection(text_words))
        base_score = word_overlap / max(len(query_words), 1)
        
        # Enhanced relevance scoring
        relevance_score = base_score
        
        # Boost for exact phrase matches
        if any(phrase in text_lower for phrase in query.lower().split()):
            relevance_score *= 1.5
        
        # Boost for topic-specific keywords
        for topic, keywords in topic_keywords.items():
            if any(word in query_words for word in keywords):
                if any(keyword in text_lower for keyword in keywords):
                    relevance_score *= 1.3
        
        # Boost scores for headings and important tags
        if section['tag'] in ['h1', 'h2', 'h3']:
            relevance_score *= 2.0
        elif section['tag'] in ['h4', 'h5', 'h6']:
            relevance_score *= 1.5
        
        # Penalize very short or very long sections
        section_length = len(section['text'])
        if section_length < 50:
            relevance_score *= 0.3  # More aggressive penalty for short sections
        elif section_length > 1000:
            relevance_score *= 0.8
        
        # Penalize sections that are clearly off-topic
        off_topic_indicators = ['financial aid', 'scholarship', 'housing', 'meal plan']
        if any(indicator in text_lower for indicator in off_topic_indicators):
            if not any(word in query_words for word in ['financial', 'aid', 'scholarship', 'housing', 'meal']):
                relevance_score *= 0.2  # Heavy penalty for off-topic content
        
        section['relevance_score'] = relevance_score
    
    # Sort by relevance score and filter out low-relevance sections
    ranked_sections = sorted(content_sections, key=lambda x: x['relevance_score'], reverse=True)
    
    # Only return sections with meaningful relevance
    return [section for section in ranked_sections if section['relevance_score'] > 0.1]

def extract_specific_data(query: str, url: str, page_content: Dict[str, Any]) -> List[Dict[str, Any]]:
    """Comprehensively extract ALL relevant data from any page content based on query."""
    query_lower = query.lower()
    extracted_data = []
    
    # Comprehensive data extraction patterns for ALL admissions aspects
    data_patterns = {
        'transfer_credits': {
            'keywords': ['transfer', 'credit', 'credits', 'transcript', 'evaluation', 'articulation'],
            'patterns': [r'\d+ credits', r'transfer.*\d+', r'credit.*transfer', r'articulation.*agreement'],
            'boost': 2.5
        },
        'admission_requirements': {
            'keywords': ['requirement', 'gpa', 'sat', 'act', 'toefl', 'ielts', 'prerequisite'],
            'patterns': [r'gpa.*\d+', r'sat.*\d+', r'act.*\d+', r'minimum.*\d+', r'requirement.*\d+'],
            'boost': 2.3
        },
        'application_process': {
            'keywords': ['application', 'apply', 'deadline', 'submit', 'document', 'essay', 'recommendation'],
            'patterns': [r'deadline.*\d+', r'application.*fee', r'submit.*\d+', r'document.*required'],
            'boost': 2.2
        },
        'financial_aid': {
            'keywords': ['financial', 'aid', 'scholarship', 'grant', 'loan', 'fafsa', 'cost'],
            'patterns': [r'\$[\d,]+', r'scholarship.*\d+', r'aid.*\d+', r'cost.*\d+'],
            'boost': 2.1
        },
        'programs_majors': {
            'keywords': ['program', 'major', 'degree', 'bachelor', 'master', 'doctorate', 'certificate'],
            'patterns': [r'program.*\d+', r'major.*\d+', r'degree.*\d+', r'credit.*\d+'],
            'boost': 2.0
        },
        'deadlines_dates': {
            'keywords': ['deadline', 'date', 'due', 'application', 'priority', 'regular'],
            'patterns': [r'\d+/\d+/\d+', r'deadline.*\d+', r'due.*\d+', r'priority.*\d+'],
            'boost': 2.0
        },
        'ranking_statistics': {
            'keywords': ['rank', 'ranking', 'rate', 'statistic', 'enrollment', 'graduation'],
            'patterns': [r'#\d+', r'\d+\.?\d*%', r'ranked.*\d+', r'\d+ students'],
            'boost': 2.0
        },
        'international_students': {
            'keywords': ['international', 'visa', 'toefl', 'ielts', 'foreign', 'overseas'],
            'patterns': [r'toefl.*\d+', r'ielts.*\d+', r'visa.*requirement', r'international.*\d+'],
            'boost': 2.0
        },
        'veterans_military': {
            'keywords': ['veteran', 'military', 'service', 'gi bill', 'benefits'],
            'patterns': [r'veteran.*benefit', r'military.*credit', r'gi.*bill', r'service.*\d+'],
            'boost': 2.0
        },
        'honors_programs': {
            'keywords': ['honor', 'honors', 'scholar', 'elite', 'prestigious'],
            'patterns': [r'honor.*program', r'scholar.*\d+', r'elite.*\d+', r'prestigious.*\d+'],
            'boost': 1.8
        }
    }
    
    # Extract data based on query intent
    for data_type, config in data_patterns.items():
        if any(word in query_lower for word in config['keywords']):
            for section in page_content['content_sections']:
                text = section['text']
                text_lower = text.lower()
                
                # Check if section contains relevant keywords
                if any(keyword in text_lower for keyword in config['keywords']):
                    # Look for specific patterns
                    import re
                    found_patterns = []
                    for pattern in config['patterns']:
                        matches = re.findall(pattern, text, re.IGNORECASE)
                        found_patterns.extend(matches)
                    
                    # If we found specific data patterns, extract this section
                    if found_patterns or len(text) < 300:  # Short sections with keywords
                        extracted_data.append({
                            'text': text,
                            'url': url,
                            'title': page_content['title'],
                            'relevance_score': config['boost'],
                            'source': f'{data_type}_data',
                            'data_type': data_type
                        })
    
    # Comprehensive extraction for any admissions-related query
    if not extracted_data:
        # Look for comprehensive content sections
        for section in page_content['content_sections']:
            text = section['text']
            text_lower = text.lower()
            # Check for comprehensive data-rich content
            has_numbers = any(char.isdigit() for char in text)
            has_percentages = '%' in text
            has_money = '$' in text
            has_dates = any(word in text_lower for word in ['2024', '2025', 'deadline', 'date', 'due'])
            has_procedures = any(word in text_lower for word in ['step', 'process', 'procedure', 'how to', 'follow'])
            has_requirements = any(word in text_lower for word in ['require', 'need', 'must', 'should', 'prerequisite'])
            
            # Check relevance to query
            query_words = set(query_lower.split())
            text_words = set(text_lower.split())
            overlap = len(query_words.intersection(text_words))
            
            # Extract if relevant and contains useful data
            if overlap > 0 and (has_numbers or has_percentages or has_money or has_dates or has_procedures or has_requirements):
                # Boost score for comprehensive content
                score_boost = 1.0
                if has_procedures:
                    score_boost += 0.5
                if has_requirements:
                    score_boost += 0.5
                if has_numbers or has_percentages or has_money:
                    score_boost += 0.3
                
                # Don't limit by length for comprehensive content
                max_length = 800 if (has_procedures or has_requirements) else 400
                
                if len(text) <= max_length:
                    extracted_data.append({
                        'text': text,
                        'url': url,
                        'title': page_content['title'],
                        'relevance_score': 1.5 + (overlap / len(query_words)) * score_boost,
                        'source': 'comprehensive_extraction',
                        'data_type': 'comprehensive'
                    })
    
    # If still no data, extract the most relevant sections regardless of patterns
    if not extracted_data:
        query_words = set(query_lower.split())
        for section in page_content['content_sections']:
            text = section['text']
            text_lower = text.lower()
            text_words = set(text_lower.split())
            overlap = len(query_words.intersection(text_words))
            
            if overlap > 0 and len(text) < 600:  # Include longer sections for comprehensive answers
                extracted_data.append({
                    'text': text,
                    'url': url,
                    'title': page_content['title'],
                    'relevance_score': 1.0 + (overlap / len(query_words)) * 0.5,
                    'source': 'fallback_extraction',
                    'data_type': 'fallback'
                })
    
    return extracted_data

def get_relevant_snippets(query: str, max_snippets: int = 5) -> List[Dict[str, Any]]:
    """Get relevant snippets for a query using dynamic search and ranking."""
    print(f"🔍 Searching for: {query}")
    
    # Step 1: Search for relevant pages
    search_results = search_cuny_pages(query, MAX_SEARCH_RESULTS)
    
    if not search_results:
        print("No search results found, using fallback...")
        return []
    
    # Step 2: Fetch and parse top pages
    all_snippets = []
    for result in search_results[:5]:  # Limit to top 5 pages
        page_content = fetch_and_parse_page(result['url'])
        if page_content:
            # Step 3: Extract specific data first
            specific_data = extract_specific_data(query, result['url'], page_content)
            all_snippets.extend(specific_data)
            
            # Step 4: Rank content sections for general content
            ranked_sections = rank_content_relevance(query, page_content['content_sections'])
            
            # Step 5: Extract top snippets
            for section in ranked_sections[:3]:  # Top 3 sections per page
                if section['relevance_score'] > 0.1:  # Relevance threshold
                    snippet = {
                        'text': section['text'][:MAX_SNIPPET_LENGTH],
                        'url': page_content['url'],
                        'title': page_content['title'],
                        'relevance_score': section['relevance_score'],
                        'source': 'live_search'
                    }
                    all_snippets.append(snippet)
        
        # Be respectful - add delay
        time.sleep(0.5)
    
    # Step 6: Sort all snippets by relevance (specific data gets priority)
    all_snippets.sort(key=lambda x: x['relevance_score'], reverse=True)
    
    print(f"📊 Found {len(all_snippets)} relevant snippets")
    return all_snippets[:max_snippets]
def clean_text(text):
    """Clean extracted text by removing extra whitespace."""
    return re.sub(r'\s+', ' ', text).strip()

def crawl_website(base_url, max_depth=3, max_pages=500, use_cache=True):
    """Crawl the website starting from base_url, up to max_depth and max_pages."""
    
    # Try to load from cache first
    if use_cache:
        cached_content = load_cache()
        if cached_content:
            return cached_content
    
    # Validate base URL is CUNY domain
    if not is_cuny_domain(base_url):
        print(f"Warning: {base_url} is not a whitelisted CUNY domain")
        return {}
    
    visited = set()
    queue = deque([(base_url, 0)])
    content = {}  # url -> cleaned text
    page_count = 0

    headers = {'User-Agent': 'Mozilla/5.0 (compatible; CUNYChatbotScraper/1.0)'}

    while queue and page_count < max_pages:
        url, depth = queue.popleft()
        if url in visited or depth > max_depth:
            continue
        
        # Check if URL is from whitelisted domain
        if not is_whitelisted_domain(url):
            continue
            
        # Check robots.txt
        if not check_robots_txt(url):
            print(f"Skipped {url}: Blocked by robots.txt")
            continue
            
        visited.add(url)
        try:
            response = requests.get(url, headers=headers, timeout=10)
            if response.status_code != 200:
                continue
            soup = BeautifulSoup(response.text, 'html.parser')
            
            # Extract main text content (paragraphs, headings, etc.)
            texts = []
            for tag in soup.find_all(['p', 'h1', 'h2', 'h3', 'h4', 'h5', 'h6', 'li']):
                if tag.text:
                    texts.append(clean_text(tag.text))
            full_text = ' '.join(texts)
            
            if full_text:
                content[url] = full_text
                page_count += 1
                print(f"Crawled: {url} (Depth: {depth}, Pages: {page_count})")
            
            # Add links to queue if within depth
            if depth < max_depth:
                for a in soup.find_all('a', href=True):
                    link = urljoin(url, a['href'])
                    # Only add whitelisted domain links
                    if is_whitelisted_domain(link) and link not in visited:
                        queue.append((link, depth + 1))
            
            # Be respectful - add delay between requests
            time.sleep(1)
            
        except Exception as e:
            print(f"Error crawling {url}: {e}")
    
    # Save to cache
    if content and use_cache:
        save_cache(content)
    
    return content

def prepare_index(content):
    """Prepare TF-IDF index from crawled content for retrieval."""
    paragraphs = []
    metadata = []
    
    for url, text in content.items():
        # Split text into paragraphs (simple split by double newline or period for approximation)
        paras = re.split(r'\n\n|\. ', text)
        for para in paras:
            para = clean_text(para)
            if len(para) > 50:  # Ignore short snippets
                paragraphs.append(para)
                metadata.append({'url': url, 'text': para})
    
    if not paragraphs:
        return None, None, None
    
    vectorizer = TfidfVectorizer(stop_words='english')
    tfidf_matrix = vectorizer.fit_transform(paragraphs)
    
    return vectorizer, tfidf_matrix, metadata

def retrieve_relevant_context(query, vectorizer, tfidf_matrix, metadata, top_k=5):
    """Retrieve top relevant paragraphs based on query using TF-IDF."""
    query_vec = vectorizer.transform([query])
    similarities = cosine_similarity(query_vec, tfidf_matrix).flatten()
    top_indices = np.argsort(similarities)[-top_k:][::-1]
    
    context = []
    for idx in top_indices:
        if similarities[idx] > 0.1:  # Threshold for relevance
            meta = metadata[idx]
            context.append(f"From {meta['url']}: {meta['text']}")
    
    return "\n\n".join(context)

def answer_with_genai(query, snippets, fallback_context=None):
    """Use OpenAI to generate an answer based on live search snippets and optional fallback context."""
    
    # Prepare context from live snippets with deduplication
    live_context = ""
    unique_sources = {}
    
    if snippets:
        live_context = "LIVE CUNY WEBSITE INFORMATION:\n\n"
        citation_index = 1
        
        for snippet in snippets:
            # Deduplicate sources by URL
            source_key = snippet['url']
            if source_key not in unique_sources:
                unique_sources[source_key] = {
                    'title': snippet['title'],
                    'url': snippet['url'],
                    'citation_num': citation_index
                }
                citation_index += 1
            
            # Add snippet with proper citation number
            citation_num = unique_sources[source_key]['citation_num']
            live_context += f"[{citation_num}] {snippet['text']}\n"
            live_context += f"Source: {snippet['title']} ({snippet['url']})\n\n"
    
    # Add fallback context if provided
    if fallback_context:
        live_context += f"\nADDITIONAL CONTEXT:\n{fallback_context}\n"
    
    if not live_context.strip():
        return "I couldn't find specific information about that topic on CUNY websites. Please try rephrasing your question or contact CUNY directly for assistance."
    
    prompt = f"""
You are a comprehensive CUNY admissions expert. Based on the following live information from CUNY websites and external data sources, provide a COMPLETE and DETAILED answer to the user's question.

CRITICAL INSTRUCTIONS:
- Provide COMPREHENSIVE information including ALL relevant details, procedures, requirements, and data
- Extract and include SPECIFIC NUMBERS, RANKINGS, PERCENTAGES, DATES, and PROCEDURES from the context
- For transfer credit questions: Include step-by-step process, credit evaluation procedures, articulation agreements, and requirements
- For admission questions: Include all requirements, deadlines, application steps, documents needed, and specific criteria
- For financial questions: Include exact costs, aid amounts, scholarship details, and application procedures
- For program questions: Include degree requirements, course details, prerequisites, and career outcomes
- Do NOT say "check the website" or "contact the office" - provide the actual comprehensive information
- Be specific and detailed: "Transfer credits are evaluated within 2-4 weeks" not "credits are evaluated"
- Include step-by-step processes when available
- Only use information from the provided context
- Cite sources using [1], [2], etc.
- If the context has comprehensive data, provide it all. If information is incomplete, say what specific information is missing

Context:
{live_context}

Question: {query}
"""
    
    try:
        client = openai.OpenAI()
        response = client.chat.completions.create(
            model="gpt-4o-mini",  # Using more cost-effective model
            messages=[
                {"role": "system", "content": "You are a knowledgeable CUNY admissions assistant. Always be accurate and cite your sources with [1], [2], etc."},
                {"role": "user", "content": prompt}
            ],
            max_tokens=600,
            temperature=0.3  # Lower temperature for more consistent answers
        )
        
        answer = response.choices[0].message.content.strip()
        
        # Add deduplicated citations
        if unique_sources:
            answer += f"\n\n📚 Sources:\n"
            for source in unique_sources.values():
                answer += f"[{source['citation_num']}] {source['title']} - {source['url']}\n"
        
        return answer
        
    except Exception as e:
        return f"Error generating answer: {e}"

def get_enhanced_answer(query, use_live_search=True, use_fallback=True):
    """Get an enhanced answer using live search with optional fallback to static content."""
    
    # Try live search first
    if use_live_search:
        print("🔍 Using live search...")
        snippets = get_relevant_snippets(query, max_snippets=5)
        
        if snippets:
            return answer_with_genai(query, snippets)
        else:
            print("⚠️ No live search results found")
    
    # Fallback to static content if available
    if use_fallback:
        print("📚 Using fallback to static content...")
        # This would integrate with existing static knowledge base
        return f"I couldn't find current information about '{query}' on CUNY websites. Please try rephrasing your question or visit the CUNY website directly for the most up-to-date information."
    
    return "I couldn't find information about that topic. Please try rephrasing your question."



def get_cuny_answer_for_chatbot(query: str, use_live_search: bool = True) -> Dict[str, Any]:
    """
    Main function to integrate with your existing chatbot.
    Returns structured response with answer, sources, and metadata.
    """
    try:
        if use_live_search:
            snippets = get_relevant_snippets(query, max_snippets=5)
            if snippets:
                answer = answer_with_genai(query, snippets)
                sources = [{"title": s["title"], "url": s["url"]} for s in snippets[:3]]
                return {
                    "answer": answer,
                    "sources": sources,
                    "method": "live_search",
                    "timestamp": datetime.now().isoformat(),
                    "success": True
                }
        
        # Fallback response
        return {
            "answer": f"I couldn't find current information about '{query}' on CUNY websites. Please try rephrasing your question or contact CUNY directly.",
            "sources": [],
            "method": "fallback",
            "timestamp": datetime.now().isoformat(),
            "success": False
        }
        
    except Exception as e:
        return {
            "answer": f"I encountered an error while searching for information: {str(e)}",
            "sources": [],
            "method": "error",
            "timestamp": datetime.now().isoformat(),
            "success": False
        }

def main():
    base_url = "https://www.cuny.edu/"
    print(f"Starting CUNY website crawl from {base_url}...")
    print(f"Using CUNY domain whitelist and robots.txt checking")
    print(f"Caching enabled (expires after {CACHE_EXPIRY_HOURS} hours)")
    
    # Try to load from cache first
    content = load_cache()
    if not content:
        print("No valid cache found, starting fresh crawl...")
        content = crawl_website(base_url, max_depth=3, max_pages=500, use_cache=True)
        
        # Add targeted crawling for specific admission pages
        target_urls = [
            "https://www.cuny.edu/admissions/undergraduate/apply/",
            "https://www.cuny.edu/admissions/graduate-studies/",
            "https://www.cuny.edu/financial-aid/tuition-and-college-costs/",
            "https://hunter.cuny.edu/admissions/undergraduate/",
            "https://baruch.cuny.edu/admissions/",
            "https://www.ccny.cuny.edu/admissions",
            "https://www.brooklyn.cuny.edu/admissions",
            "https://www.queens.cuny.edu/admissions",
            "https://www.lehman.cuny.edu/admissions"
        ]
        
        print("Crawling targeted admission pages...")
        for url in target_urls:
            if is_cuny_domain(url) and check_robots_txt(url):
                try:
                    single_content = crawl_website(url, max_depth=1, max_pages=50, use_cache=False)
                    content.update(single_content)
                    print(f"Added {len(single_content)} pages from {url}")
                except Exception as e:
                    print(f"Failed to crawl {url}: {e}")
    else:
        print("Using cached content")
    
    print(f"Crawled {len(content)} pages.")
    
    if not content:
        print("No content found. Check your internet connection and CUNY domain access.")
        return
    
    vectorizer, tfidf_matrix, metadata = prepare_index(content)
    if vectorizer is None:
        print("No content indexed.")
        return
    
    print(f"Indexed {len(metadata)} text segments for search")
    print("\n🤖 Enhanced CUNY AI Chatbot ready!")
    print("Features: Live search + Static fallback + Citations")
    print("Ask questions (type 'exit' to quit):")
    
    while True:
        question = input("\n> ")
        if question.lower() == 'exit':
            break
        
        # Use enhanced answer with live search
        answer = get_enhanced_answer(question, use_live_search=True, use_fallback=True)
        print("\n🤖 Answer:")
        print(answer)
        print("\n" + "="*50)

if __name__ == "__main__":
    main()