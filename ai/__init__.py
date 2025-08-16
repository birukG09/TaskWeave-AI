"""
TaskWeave AI - AI module
"""
from .providers import OpenAIProvider, AnthropicProvider
from .pipelines import TaskExtractor, PriorityScorer, ReportGenerator, DailyDigester
from .prompts import TASK_EXTRACTION_PROMPT, PRIORITY_SCORING_PROMPT, DAILY_DIGEST_PROMPT, WEEKLY_REPORT_PROMPT

__all__ = [
    "OpenAIProvider",
    "AnthropicProvider",
    "TaskExtractor",
    "PriorityScorer", 
    "ReportGenerator",
    "DailyDigester",
    "TASK_EXTRACTION_PROMPT",
    "PRIORITY_SCORING_PROMPT",
    "DAILY_DIGEST_PROMPT",
    "WEEKLY_REPORT_PROMPT"
]
