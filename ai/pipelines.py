"""
TaskWeave AI - AI processing pipelines
"""
from typing import Dict, Any, List, Optional
import structlog

from .providers import AIProvider
from .prompts import (
    TASK_EXTRACTION_PROMPT,
    PRIORITY_SCORING_PROMPT, 
    DAILY_DIGEST_PROMPT,
    WEEKLY_REPORT_PROMPT
)

logger = structlog.get_logger()

class TaskExtractor:
    """Extract tasks from various event types"""
    
    def __init__(self, ai_provider: Optional[AIProvider] = None):
        self.ai_provider = ai_provider or AIProvider()
    
    async def extract_tasks(self, event_data: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Extract actionable tasks from event data"""
        try:
            # Format event data for AI processing
            event_context = self._format_event_context(event_data)
            
            prompt = TASK_EXTRACTION_PROMPT.format(
                event_type=event_data.get("type", "unknown"),
                event_content=event_context
            )
            
            schema = {
                "tasks": [
                    {
                        "title": "string",
                        "description": "string",
                        "priority": "number (1-5)",
                        "estimated_effort": "string",
                        "category": "string",
                        "actionable": "boolean",
                        "confidence": "number (0-1)"
                    }
                ]
            }
            
            result = await self.ai_provider.extract_structured_data(prompt, schema)
            
            # Filter high-confidence tasks
            tasks = result.get("tasks", [])
            filtered_tasks = [
                task for task in tasks 
                if task.get("actionable", False) and task.get("confidence", 0) > 0.7
            ]
            
            logger.info("Tasks extracted", 
                       total_extracted=len(tasks), 
                       high_confidence=len(filtered_tasks),
                       event_type=event_data.get("type"))
            
            return filtered_tasks
            
        except Exception as e:
            logger.error("Task extraction failed", error=str(e))
            return []
    
    def _format_event_context(self, event_data: Dict[str, Any]) -> str:
        """Format event data for AI processing"""
        event_type = event_data.get("type", "")
        
        if event_type == "email":
            return f"""
Subject: {event_data.get('subject', '')}
From: {event_data.get('from', '')}
Body: {event_data.get('body', '')[:1000]}
"""
        elif event_type == "issue":
            return f"""
Title: {event_data.get('title', '')}
Repository: {event_data.get('repo', '')}
State: {event_data.get('state', '')}
Body: {event_data.get('body', '')[:1000]}
Labels: {', '.join(event_data.get('labels', []))}
"""
        elif event_type == "message":
            return f"""
Channel: {event_data.get('channel', '')}
User: {event_data.get('user', '')}
Message: {event_data.get('text', '')}
"""
        elif event_type == "card":
            return f"""
Board: {event_data.get('board', '')}
Card Name: {event_data.get('name', '')}
Description: {event_data.get('description', '')}
Due Date: {event_data.get('due_date', '')}
Labels: {', '.join(event_data.get('labels', []))}
"""
        else:
            # Generic formatting
            return str(event_data.get("raw", event_data))[:1000]

class PriorityScorer:
    """Score task priorities using AI"""
    
    def __init__(self, ai_provider: Optional[AIProvider] = None):
        self.ai_provider = ai_provider or AIProvider()
    
    async def score_priority(self, task_data: Dict[str, Any], context: Dict[str, Any] = None) -> int:
        """Score task priority from 1-5"""
        try:
            context_str = ""
            if context:
                context_str = f"""
Organization Context:
- Team size: {context.get('team_size', 'unknown')}
- Current workload: {context.get('current_workload', 'unknown')}
- Recent priorities: {context.get('recent_priorities', [])}
"""
            
            prompt = PRIORITY_SCORING_PROMPT.format(
                title=task_data.get("title", ""),
                description=task_data.get("description", ""),
                source=task_data.get("source", ""),
                context=context_str
            )
            
            schema = {
                "priority": "number (1-5)",
                "reasoning": "string",
                "urgency_factors": ["string"],
                "confidence": "number (0-1)"
            }
            
            result = await self.ai_provider.extract_structured_data(prompt, schema)
            
            priority = result.get("priority", 3)
            # Ensure priority is within valid range
            priority = max(1, min(5, int(priority)))
            
            logger.info("Priority scored", 
                       task_title=task_data.get("title", "")[:50],
                       priority=priority,
                       confidence=result.get("confidence", 0))
            
            return priority
            
        except Exception as e:
            logger.error("Priority scoring failed", error=str(e))
            return 3  # Default medium priority

class ReportGenerator:
    """Generate AI-powered reports"""
    
    def __init__(self, ai_provider: Optional[AIProvider] = None):
        self.ai_provider = ai_provider or AIProvider()
    
    async def generate_report(self, report_data: Dict[str, Any]) -> Dict[str, Any]:
        """Generate comprehensive report"""
        try:
            report_type = report_data.get("period", "daily")
            
            if report_type == "daily":
                prompt = DAILY_DIGEST_PROMPT.format(
                    date=report_data.get("end_date", ""),
                    task_data=self._format_task_summary(report_data.get("tasks", {})),
                    event_data=self._format_event_summary(report_data.get("events", {}))
                )
            else:
                prompt = WEEKLY_REPORT_PROMPT.format(
                    start_date=report_data.get("start_date", ""),
                    end_date=report_data.get("end_date", ""),
                    task_data=self._format_task_summary(report_data.get("tasks", {})),
                    event_data=self._format_event_summary(report_data.get("events", {}))
                )
            
            schema = {
                "executive_summary": "string",
                "key_accomplishments": ["string"],
                "challenges_identified": ["string"],
                "upcoming_priorities": ["string"],
                "metrics": {
                    "productivity_score": "number (1-10)",
                    "task_completion_rate": "number (0-1)",
                    "team_velocity": "string"
                },
                "recommendations": ["string"]
            }
            
            result = await self.ai_provider.extract_structured_data(prompt, schema)
            
            logger.info("Report generated", 
                       type=report_type,
                       summary_length=len(result.get("executive_summary", "")))
            
            return result
            
        except Exception as e:
            logger.error("Report generation failed", error=str(e))
            return {
                "executive_summary": "Report generation failed due to technical issues.",
                "key_accomplishments": [],
                "challenges_identified": ["Technical issues with AI report generation"],
                "upcoming_priorities": [],
                "metrics": {"productivity_score": 5, "task_completion_rate": 0, "team_velocity": "unknown"},
                "recommendations": ["Review AI service configuration"]
            }
    
    def _format_task_summary(self, task_data: Dict[str, Any]) -> str:
        """Format task data for AI processing"""
        return f"""
Task Summary:
- Total tasks: {task_data.get('total', 0)}
- Completed: {task_data.get('completed', 0)}
- In progress: {task_data.get('in_progress', 0)}
- Todo: {task_data.get('todo', 0)}
- Blocked: {task_data.get('blocked', 0)}

Priority Distribution:
- High priority: {task_data.get('by_priority', {}).get('high', 0)}
- Medium priority: {task_data.get('by_priority', {}).get('medium', 0)}
- Low priority: {task_data.get('by_priority', {}).get('low', 0)}
"""
    
    def _format_event_summary(self, event_data: Dict[str, Any]) -> str:
        """Format event data for AI processing"""
        by_provider = event_data.get("by_provider", {})
        provider_summary = "\n".join([f"- {provider}: {count}" for provider, count in by_provider.items()])
        
        return f"""
Event Summary:
- Total events: {event_data.get('total', 0)}

By Provider:
{provider_summary}
"""

class DailyDigester:
    """Generate daily digest summaries"""
    
    def __init__(self, ai_provider: Optional[AIProvider] = None):
        self.ai_provider = ai_provider or AIProvider()
    
    async def generate_digest(self, events: List[Dict[str, Any]]) -> str:
        """Generate daily digest from events"""
        try:
            # Group events by type and source
            event_summary = self._summarize_events(events)
            
            prompt = f"""
Create a brief daily digest from these events:

{event_summary}

Focus on:
1. Key updates and changes
2. New tasks or issues that need attention
3. Important communications
4. Progress on ongoing work

Keep it concise but informative, suitable for a team lead's morning briefing.
"""
            
            digest = await self.ai_provider.generate_completion(
                prompt=prompt,
                temperature=0.5,
                max_tokens=500
            )
            
            logger.info("Daily digest generated", event_count=len(events))
            
            return digest
            
        except Exception as e:
            logger.error("Daily digest generation failed", error=str(e))
            return "Unable to generate daily digest due to technical issues."
    
    def _summarize_events(self, events: List[Dict[str, Any]]) -> str:
        """Summarize events for digest generation"""
        if not events:
            return "No events to summarize."
        
        summary_parts = []
        
        # Group by type
        by_type = {}
        for event in events:
            event_type = event.get("type", "unknown")
            if event_type not in by_type:
                by_type[event_type] = []
            by_type[event_type].append(event)
        
        for event_type, type_events in by_type.items():
            summary_parts.append(f"\n{event_type.title()} Events ({len(type_events)}):")
            
            for event in type_events[:5]:  # Limit to 5 per type
                if event_type == "email":
                    summary_parts.append(f"- {event.get('subject', 'No subject')}")
                elif event_type == "issue":
                    summary_parts.append(f"- {event.get('title', 'No title')} ({event.get('state', 'unknown')})")
                elif event_type == "message":
                    summary_parts.append(f"- {event.get('channel', '')}: {event.get('text', '')[:100]}")
                else:
                    summary_parts.append(f"- {str(event)[:100]}")
        
        return "\n".join(summary_parts)
