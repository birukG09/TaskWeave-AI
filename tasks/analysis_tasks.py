"""
TaskWeave AI - Celery tasks for AI processing
"""
import logging
from celery import current_app as celery_app
from ai_service import ai_service
from simple_app import app, db, User

logger = logging.getLogger(__name__)

@celery_app.task
def process_slack_message_for_tasks(message_data):
    """Process Slack message to extract tasks using AI"""
    try:
        with app.app_context():
            text = message_data.get('text', '')
            channel = message_data.get('channel', 'unknown')
            user = message_data.get('user', 'unknown')
            
            # Extract tasks using AI
            tasks = ai_service.extract_tasks_from_text(
                text=text, 
                source=f"slack:{channel}"
            )
            
            # Store tasks in database (would implement proper Task model)
            created_tasks = []
            for task_data in tasks:
                # Mock task creation - would use proper database models
                task_id = f"task_{len(created_tasks) + 1}"
                created_tasks.append({
                    'id': task_id,
                    'title': task_data.get('title'),
                    'description': task_data.get('description'),
                    'source': 'slack',
                    'channel': channel,
                    'created_by_ai': True
                })
            
            logger.info(f"Created {len(created_tasks)} tasks from Slack message")
            return {
                'status': 'success',
                'tasks_created': len(created_tasks),
                'tasks': created_tasks
            }
            
    except Exception as e:
        logger.error(f"Slack message processing failed: {e}")
        return {'status': 'error', 'message': str(e)}

@celery_app.task
def process_github_events_for_tasks(github_data):
    """Process GitHub events to extract tasks using AI"""
    try:
        with app.app_context():
            event_type = github_data.get('action', 'unknown')
            repo = github_data.get('repository', {}).get('name', 'unknown')
            
            # Extract relevant text based on event type
            if event_type == 'opened' and 'pull_request' in github_data:
                text = f"PR: {github_data['pull_request']['title']}\n{github_data['pull_request']['body']}"
            elif event_type == 'opened' and 'issue' in github_data:
                text = f"Issue: {github_data['issue']['title']}\n{github_data['issue']['body']}"
            else:
                text = f"GitHub {event_type} event in {repo}"
            
            tasks = ai_service.extract_tasks_from_text(
                text=text,
                source=f"github:{repo}"
            )
            
            created_tasks = []
            for task_data in tasks:
                # Mock task creation
                created_tasks.append({
                    'id': f"gh_task_{len(created_tasks) + 1}",
                    'title': task_data.get('title'),
                    'description': task_data.get('description'),
                    'source': 'github',
                    'repository': repo,
                    'event_type': event_type,
                    'created_by_ai': True
                })
            
            logger.info(f"Created {len(created_tasks)} tasks from GitHub event")
            return {
                'status': 'success',
                'tasks_created': len(created_tasks),
                'tasks': created_tasks
            }
            
    except Exception as e:
        logger.error(f"GitHub event processing failed: {e}")
        return {'status': 'error', 'message': str(e)}

@celery_app.task
def generate_weekly_report(org_id, project_id=None):
    """Generate AI-powered weekly progress report"""
    try:
        with app.app_context():
            # Mock task data - would fetch from database
            tasks_data = [
                {
                    'id': '1',
                    'title': 'Complete API integration',
                    'status': 'completed',
                    'priority': 'high',
                    'completed_at': '2024-01-01T10:00:00Z'
                },
                {
                    'id': '2', 
                    'title': 'Review security audit',
                    'status': 'in_progress',
                    'priority': 'medium'
                },
                {
                    'id': '3',
                    'title': 'Update documentation',
                    'status': 'open',
                    'priority': 'low'
                }
            ]
            
            # Generate report using AI
            report_content = ai_service.generate_progress_report(
                tasks_data=tasks_data,
                timeframe="weekly"
            )
            
            # Store report in database (would implement Report model)
            report = {
                'id': f"report_{org_id}_weekly",
                'title': 'Weekly Progress Report',
                'content': report_content,
                'type': 'progress',
                'period': 'weekly',
                'organization_id': org_id,
                'project_id': project_id,
                'generated_by_ai': True,
                'created_at': '2024-01-01T00:00:00Z'
            }
            
            logger.info(f"Generated weekly report for org {org_id}")
            return {
                'status': 'success',
                'report': report
            }
            
    except Exception as e:
        logger.error(f"Weekly report generation failed: {e}")
        return {'status': 'error', 'message': str(e)}

@celery_app.task
def analyze_team_productivity(org_id, timeframe_days=7):
    """Analyze team productivity patterns using AI"""
    try:
        with app.app_context():
            # Mock productivity data - would fetch real metrics
            productivity_data = {
                'tasks_completed': 12,
                'average_completion_time': '2.5 days',
                'high_priority_completed': 4,
                'team_velocity': 'increasing',
                'collaboration_events': 28,
                'blockers_resolved': 3
            }
            
            # AI analysis of productivity patterns
            analysis_prompt = f"""Analyze team productivity data for the last {timeframe_days} days:
            {productivity_data}
            
            Provide insights on:
            1. Team performance trends
            2. Productivity bottlenecks
            3. Recommendations for improvement
            4. Recognition for achievements"""
            
            analysis = ai_service.generate_with_fallback(
                prompt=analysis_prompt,
                system_prompt="You are a productivity analyst providing actionable insights for team improvement."
            )
            
            logger.info(f"Completed productivity analysis for org {org_id}")
            return {
                'status': 'success',
                'analysis': analysis,
                'data': productivity_data
            }
            
    except Exception as e:
        logger.error(f"Productivity analysis failed: {e}")
        return {'status': 'error', 'message': str(e)}