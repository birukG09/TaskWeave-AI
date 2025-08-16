"""
TaskWeave AI - APScheduler for automated task scheduling
"""
import logging
from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.triggers.cron import CronTrigger
from apscheduler.triggers.interval import IntervalTrigger
from tasks.ai_tasks import generate_weekly_report, analyze_team_productivity
from tasks.slack_tasks import send_daily_summary, send_slack_report
from tasks.notion_tasks import bulk_sync_tasks_to_notion
import atexit

logger = logging.getLogger(__name__)

class TaskScheduler:
    """APScheduler wrapper for TaskWeave AI automated tasks"""
    
    def __init__(self):
        self.scheduler = BackgroundScheduler()
        self.setup_jobs()
        
    def setup_jobs(self):
        """Setup all scheduled jobs"""
        
        # Daily Slack summary at 6 PM
        self.scheduler.add_job(
            func=self._send_daily_summaries,
            trigger=CronTrigger(hour=18, minute=0),
            id='daily_slack_summary',
            name='Send daily summary to Slack',
            replace_existing=True
        )
        
        # Weekly progress reports on Fridays at 5 PM
        self.scheduler.add_job(
            func=self._generate_weekly_reports,
            trigger=CronTrigger(day_of_week='fri', hour=17, minute=0),
            id='weekly_progress_report',
            name='Generate weekly progress reports',
            replace_existing=True
        )
        
        # Team productivity analysis every 3 days
        self.scheduler.add_job(
            func=self._analyze_productivity,
            trigger=IntervalTrigger(days=3),
            id='productivity_analysis',
            name='Analyze team productivity patterns',
            replace_existing=True
        )
        
        # Sync pending tasks to Notion every 2 hours
        self.scheduler.add_job(
            func=self._sync_notion_tasks,
            trigger=IntervalTrigger(hours=2),
            id='notion_sync',
            name='Sync tasks to Notion',
            replace_existing=True
        )
        
        # Health check and cleanup every 6 hours
        self.scheduler.add_job(
            func=self._system_maintenance,
            trigger=IntervalTrigger(hours=6),
            id='system_maintenance',
            name='System health check and maintenance',
            replace_existing=True
        )
        
        logger.info("Scheduled jobs configured")
    
    def _send_daily_summaries(self):
        """Send daily summaries to all active organizations"""
        try:
            # Mock org IDs - would fetch from database
            active_orgs = ['org_1', 'org_2', 'default_org']
            
            for org_id in active_orgs:
                send_daily_summary.delay(org_id)
            
            logger.info(f"Daily summaries scheduled for {len(active_orgs)} organizations")
        except Exception as e:
            logger.error(f"Failed to schedule daily summaries: {e}")
    
    def _generate_weekly_reports(self):
        """Generate weekly reports for all organizations"""
        try:
            # Mock org IDs and projects
            organizations = [
                {'org_id': 'org_1', 'projects': ['proj_1', 'proj_2']},
                {'org_id': 'default_org', 'projects': ['main_project']}
            ]
            
            for org in organizations:
                # Generate org-level report
                generate_weekly_report.delay(org['org_id'])
                
                # Generate project-level reports
                for project_id in org['projects']:
                    generate_weekly_report.delay(org['org_id'], project_id)
            
            logger.info("Weekly reports scheduled for all organizations")
        except Exception as e:
            logger.error(f"Failed to schedule weekly reports: {e}")
    
    def _analyze_productivity(self):
        """Analyze productivity for all organizations"""
        try:
            active_orgs = ['org_1', 'org_2', 'default_org']
            
            for org_id in active_orgs:
                analyze_team_productivity.delay(org_id, timeframe_days=7)
            
            logger.info("Productivity analysis scheduled for all organizations")
        except Exception as e:
            logger.error(f"Failed to schedule productivity analysis: {e}")
    
    def _sync_notion_tasks(self):
        """Sync pending tasks to Notion"""
        try:
            # Mock pending tasks - would fetch from database
            pending_tasks = [
                {
                    'id': 'task_1',
                    'title': 'Review API documentation',
                    'description': 'Complete review of REST API docs',
                    'status': 'open',
                    'priority': 'medium',
                    'source': 'manual'
                },
                {
                    'id': 'task_2',
                    'title': 'Fix authentication bug',
                    'description': 'Resolve JWT token refresh issue',
                    'status': 'in_progress',
                    'priority': 'high',
                    'source': 'github'
                }
            ]
            
            if pending_tasks:
                bulk_sync_tasks_to_notion.delay(pending_tasks)
                logger.info(f"Notion sync scheduled for {len(pending_tasks)} tasks")
            
        except Exception as e:
            logger.error(f"Failed to schedule Notion sync: {e}")
    
    def _system_maintenance(self):
        """Perform system maintenance tasks"""
        try:
            # Health check tasks
            logger.info("Performing system maintenance...")
            
            # Could add tasks like:
            # - Clean up old completed tasks
            # - Archive old reports
            # - Update integration statuses
            # - Optimize database
            
            logger.info("System maintenance completed")
        except Exception as e:
            logger.error(f"System maintenance failed: {e}")
    
    def start(self):
        """Start the scheduler"""
        try:
            self.scheduler.start()
            logger.info("Task scheduler started successfully")
            
            # Log scheduled jobs
            jobs = self.scheduler.get_jobs()
            for job in jobs:
                logger.info(f"Scheduled job: {job.name} - Next run: {job.next_run_time}")
                
        except Exception as e:
            logger.error(f"Failed to start scheduler: {e}")
    
    def stop(self):
        """Stop the scheduler"""
        try:
            self.scheduler.shutdown()
            logger.info("Task scheduler stopped")
        except Exception as e:
            logger.error(f"Failed to stop scheduler: {e}")
    
    def add_custom_job(self, func, trigger, job_id, name, **kwargs):
        """Add a custom scheduled job"""
        try:
            self.scheduler.add_job(
                func=func,
                trigger=trigger,
                id=job_id,
                name=name,
                replace_existing=True,
                **kwargs
            )
            logger.info(f"Custom job added: {name}")
        except Exception as e:
            logger.error(f"Failed to add custom job {name}: {e}")
    
    def remove_job(self, job_id):
        """Remove a scheduled job"""
        try:
            self.scheduler.remove_job(job_id)
            logger.info(f"Job removed: {job_id}")
        except Exception as e:
            logger.error(f"Failed to remove job {job_id}: {e}")
    
    def get_job_status(self):
        """Get status of all scheduled jobs"""
        jobs = self.scheduler.get_jobs()
        return [
            {
                'id': job.id,
                'name': job.name,
                'next_run': str(getattr(job, 'next_run_time', 'Not scheduled')),
                'trigger': str(job.trigger),
                'scheduled': self.scheduler.running
            }
            for job in jobs
        ]

# Create global scheduler instance
task_scheduler = TaskScheduler()

# Register cleanup on exit
atexit.register(lambda: task_scheduler.stop())