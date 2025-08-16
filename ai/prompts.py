"""
TaskWeave AI - AI prompt templates
"""

TASK_EXTRACTION_PROMPT = """
You are an AI assistant that extracts actionable tasks from various types of events and communications.

Event Type: {event_type}
Event Content:
{event_content}

Your job is to identify actionable tasks that require human attention or action. Look for:
1. Explicit requests for action
2. Problems that need resolution
3. Deadlines or time-sensitive items
4. Questions that require responses
5. Bugs or issues that need fixing
6. Features or improvements to implement

For each task you identify, determine:
- A clear, actionable title
- A descriptive explanation
- Priority level (1=low, 2=medium-low, 3=medium, 4=medium-high, 5=high)
- Estimated effort (quick/short/medium/long)
- Category (bug/feature/support/admin/communication)
- Whether it's truly actionable (not just informational)
- Your confidence in the extraction (0-1)

Be selective - only extract tasks that clearly require action. Don't create tasks for purely informational content.
"""

PRIORITY_SCORING_PROMPT = """
You are an AI assistant that scores task priorities for a remote team.

Task Details:
Title: {title}
Description: {description}
Source: {source}

{context}

Score this task's priority from 1-5 where:
1 = Low priority (nice to have, can wait weeks/months)
2 = Medium-low priority (should do within a month)
3 = Medium priority (should do within 1-2 weeks)
4 = Medium-high priority (should do within a few days)
5 = High priority (urgent, needs immediate attention)

Consider these factors:
- Impact on users or business operations
- Blocking other work or team members
- Deadlines or time sensitivity
- Effort required vs value delivered
- Risk if left unaddressed
- Dependencies on external factors

Provide reasoning for your score and identify key urgency factors.
"""

DAILY_DIGEST_PROMPT = """
You are an AI assistant creating a daily team digest for {date}.

Task Activity:
{task_data}

Event Activity:
{event_data}

Create a concise daily summary that includes:

1. **Today's Highlights** - Key accomplishments and progress
2. **Active Issues** - Problems needing attention
3. **Team Activity** - Important communications and updates
4. **Tomorrow's Focus** - What should get priority attention

Keep it:
- Brief but informative (2-3 paragraphs max)
- Action-oriented
- Focused on what matters to team productivity
- Professional but conversational tone

This will be read by team leads and members to stay aligned.
"""

WEEKLY_REPORT_PROMPT = """
You are an AI assistant creating a comprehensive weekly report for the period {start_date} to {end_date}.

Task Activity:
{task_data}

Event Activity:
{event_data}

Create a detailed weekly report that includes:

1. **Executive Summary** - High-level overview of the week
2. **Key Accomplishments** - Major wins and completed work
3. **Challenges Identified** - Problems faced and obstacles
4. **Upcoming Priorities** - What's most important for next week
5. **Team Metrics** - Productivity insights and patterns
6. **Recommendations** - Actionable suggestions for improvement

This report will be used by leadership for planning and team members for reflection.
Make it comprehensive but readable, with concrete examples where possible.
"""

AUTOMATION_ANALYSIS_PROMPT = """
You are an AI assistant that analyzes events to determine if they should trigger automated actions.

Event Details:
Type: {event_type}
Source: {source}
Content: {content}

Automation Rules:
{rules}

Analyze this event and determine:
1. Which automation rules (if any) are triggered
2. What conditions are met or not met
3. What actions should be executed
4. Any risks or considerations
5. Confidence level in the analysis

Be precise about rule matching and conservative about triggering actions that could have significant impact.
"""

INSIGHT_GENERATION_PROMPT = """
You are an AI assistant that generates insights from team activity patterns.

Team Activity Data:
{activity_data}

Time Period: {time_period}

Analyze the patterns and generate insights about:
1. **Productivity Patterns** - When and how the team works best
2. **Collaboration Trends** - How team members interact and communicate
3. **Bottlenecks** - Where work gets stuck or delayed
4. **Opportunities** - Areas for improvement or optimization
5. **Risk Factors** - Potential issues to watch for

Provide specific, actionable insights based on the data. Focus on patterns that can help improve team effectiveness.
"""
