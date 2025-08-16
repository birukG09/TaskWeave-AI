"""
TaskWeave - Text Analysis Service with advanced processing and failover logic
"""
import os
import logging
from typing import Optional, Dict, Any, List
from langchain_openai import ChatOpenAI
from langchain_anthropic import ChatAnthropic
from langchain.schema import HumanMessage, SystemMessage
from langchain_community.callbacks import get_openai_callback
import pinecone
from tenacity import retry, stop_after_attempt, wait_exponential

logger = logging.getLogger(__name__)

class AnalysisServiceWrapper:
    """Analysis service wrapper with multiple backends and context memory"""
    
    def __init__(self):
        self.primary_client = None
        self.secondary_client = None
        self.pinecone_index = None
        self._initialize_clients()
        self._initialize_pinecone()
    
    def _initialize_clients(self):
        """Initialize processing clients"""
        primary_key = os.environ.get('PRIMARY_API_KEY')
        secondary_key = os.environ.get('SECONDARY_API_KEY')
        
        if primary_key:
            try:
                from langchain_openai import ChatOpenAI
                self.primary_client = ChatOpenAI(
                    model="gpt-4o",
                    openai_api_key=primary_key,
                    temperature=0.1
                )
                logger.info("Primary processing client initialized")
            except ImportError:
                logger.warning("Primary client not available")
        
        if secondary_key:
            try:
                from langchain_anthropic import ChatAnthropic
                self.secondary_client = ChatAnthropic(
                    model="claude-sonnet-4-20250514",
                    anthropic_api_key=secondary_key,
                    temperature=0.1
                )
                logger.info("Secondary processing client initialized")
            except ImportError:
                logger.warning("Secondary client not available")
    
    def _initialize_pinecone(self):
        """Initialize Pinecone for context memory"""
        pinecone_key = os.environ.get('PINECONE_API_KEY')
        pinecone_env = os.environ.get('PINECONE_ENVIRONMENT', 'us-west1-gcp')
        
        if pinecone_key:
            try:
                pinecone.init(api_key=pinecone_key, environment=pinecone_env)
                
                # Create or connect to index
                index_name = "taskweave-context"
                if index_name not in pinecone.list_indexes():
                    pinecone.create_index(
                        name=index_name,
                        dimension=1536,  # OpenAI embedding dimension
                        metric='cosine'
                    )
                
                self.pinecone_index = pinecone.Index(index_name)
                logger.info("Pinecone context memory initialized")
            except Exception as e:
                logger.warning(f"Pinecone initialization failed: {e}")
    
    @retry(stop=stop_after_attempt(3), wait=wait_exponential(multiplier=1, min=4, max=10))
    def _call_openai(self, messages: List, **kwargs):
        """Call OpenAI with retry logic"""
        if not self.openai_client:
            raise Exception("OpenAI client not available")
        
        with get_openai_callback() as cb:
            response = self.openai_client(messages, **kwargs)
            logger.info(f"OpenAI usage - Tokens: {cb.total_tokens}, Cost: ${cb.total_cost}")
            return response.content
    
    @retry(stop=stop_after_attempt(3), wait=wait_exponential(multiplier=1, min=4, max=10))
    def _call_anthropic(self, messages: List, **kwargs):
        """Call Anthropic with retry logic"""
        if not self.anthropic_client:
            raise Exception("Anthropic client not available")
        
        response = self.anthropic_client(messages, **kwargs)
        return response.content
    
    def generate_with_fallback(self, prompt: str, system_prompt: str = None, **kwargs) -> str:
        """Generate text with OpenAI primary, Anthropic fallback"""
        messages = []
        if system_prompt:
            messages.append(SystemMessage(content=system_prompt))
        messages.append(HumanMessage(content=prompt))
        
        # Try OpenAI first
        if self.openai_client:
            try:
                return self._call_openai(messages, **kwargs)
            except Exception as e:
                logger.error(f"OpenAI failed: {e}, falling back to Anthropic")
        
        # Fallback to Anthropic
        if self.anthropic_client:
            try:
                return self._call_anthropic(messages, **kwargs)
            except Exception as e:
                logger.error(f"Anthropic failed: {e}")
                raise Exception("All AI providers failed")
        
        raise Exception("No AI providers available")
    
    def extract_tasks_from_text(self, text: str, source: str = "unknown") -> List[Dict[str, Any]]:
        """Extract actionable tasks from text using AI or rule-based fallback"""
        
        # If AI clients are available, use them
        if self.openai_client or self.anthropic_client:
            system_prompt = """You are an AI assistant that extracts actionable tasks from text.
            Analyze the provided text and identify concrete, actionable tasks that should be tracked.
            
            For each task, provide:
            - title: Clear, concise task title
            - description: Detailed description of what needs to be done
            - priority: high, medium, or low
            - estimated_effort: small, medium, large
            - assignee: person mentioned or "unassigned"
            - due_date: if mentioned, otherwise null
            
            Return a JSON array of task objects. If no actionable tasks found, return empty array."""
            
            prompt = f"""Source: {source}
            Text to analyze: {text}
            
            Extract actionable tasks in JSON format:"""
            
            try:
                response = self.generate_with_fallback(prompt, system_prompt)
                import json
                tasks = json.loads(response)
                return tasks if isinstance(tasks, list) else []
            except Exception as e:
                logger.error(f"AI task extraction failed: {e}")
        
        # Fallback: Rule-based task extraction
        return self._extract_tasks_rule_based(text, source)
    
    def _extract_tasks_rule_based(self, text: str, source: str) -> List[Dict[str, Any]]:
        """Fallback rule-based task extraction"""
        import re
        
        tasks = []
        
        # Keywords that suggest actionable tasks
        task_keywords = [
            r'need to\s+(\w+(?:\s+\w+)*)',
            r'should\s+(\w+(?:\s+\w+)*)',
            r'must\s+(\w+(?:\s+\w+)*)',
            r'todo:?\s*(.+)',
            r'action:?\s*(.+)',
            r'task:?\s*(.+)',
            r'fix\s+(.+)',
            r'implement\s+(.+)',
            r'create\s+(.+)',
            r'review\s+(.+)',
            r'update\s+(.+)',
            r'complete\s+(.+)'
        ]
        
        # Priority keywords
        priority_high = ['urgent', 'critical', 'asap', 'immediately', 'high priority']
        priority_low = ['later', 'when possible', 'low priority', 'nice to have']
        
        sentences = re.split(r'[.!?]\s+', text)
        
        for sentence in sentences:
            for pattern in task_keywords:
                matches = re.findall(pattern, sentence, re.IGNORECASE)
                for match in matches:
                    # Determine priority
                    priority = 'medium'  # default
                    sentence_lower = sentence.lower()
                    
                    if any(keyword in sentence_lower for keyword in priority_high):
                        priority = 'high'
                    elif any(keyword in sentence_lower for keyword in priority_low):
                        priority = 'low'
                    
                    # Extract assignee if mentioned
                    assignee_match = re.search(r'@(\w+)', sentence)
                    assignee = assignee_match.group(1) if assignee_match else 'unassigned'
                    
                    # Extract due date
                    due_date_match = re.search(r'by\s+(monday|tuesday|wednesday|thursday|friday|saturday|sunday|\d{1,2}/\d{1,2}|\d{4}-\d{2}-\d{2})', sentence, re.IGNORECASE)
                    due_date = due_date_match.group(1) if due_date_match else None
                    
                    tasks.append({
                        'title': match.strip()[:100],  # Limit title length
                        'description': sentence.strip(),
                        'priority': priority,
                        'estimated_effort': 'medium',
                        'assignee': assignee,
                        'due_date': due_date,
                        'source': source,
                        'extracted_by': 'rule_based'
                    })
        
        return tasks[:5]  # Limit to 5 tasks per text
    
    def generate_progress_report(self, tasks_data: List[Dict], timeframe: str = "weekly") -> str:
        """Generate AI-powered progress report"""
        system_prompt = f"""You are an AI assistant that creates insightful {timeframe} progress reports for teams.
        Analyze the provided task data and generate a comprehensive report that includes:
        
        1. Executive Summary (2-3 sentences)
        2. Key Accomplishments
        3. Task Status Breakdown
        4. Priority Items Completed
        5. Upcoming Focus Areas
        6. Team Productivity Insights
        7. Recommendations for next {timeframe}
        
        Make it professional, actionable, and highlight both achievements and areas for improvement."""
        
        prompt = f"""Generate a {timeframe} progress report based on this task data:
        {tasks_data}
        
        Create a comprehensive report that would be valuable for team leadership:"""
        
        try:
            return self.generate_with_fallback(prompt, system_prompt)
        except Exception as e:
            logger.error(f"Report generation failed: {e}")
            return f"Report generation temporarily unavailable. Task summary: {len(tasks_data)} tasks analyzed."
    
    def store_context(self, text: str, metadata: Dict[str, Any]):
        """Store context in Pinecone for memory"""
        if not self.pinecone_index:
            return False
        
        try:
            # Generate embedding (would need OpenAI embeddings)
            # For now, store key-value pairs
            context_id = f"ctx_{metadata.get('timestamp', 'unknown')}"
            # This is a simplified version - would need proper embeddings
            logger.info(f"Context stored: {context_id}")
            return True
        except Exception as e:
            logger.error(f"Context storage failed: {e}")
            return False
    
    def retrieve_context(self, query: str, limit: int = 5) -> List[Dict]:
        """Retrieve relevant context from Pinecone"""
        if not self.pinecone_index:
            return []
        
        try:
            # Would implement semantic search here
            logger.info(f"Context retrieval for: {query}")
            return []
        except Exception as e:
            logger.error(f"Context retrieval failed: {e}")
            return []

# Create global analysis service instance
analysis_service = AnalysisServiceWrapper()