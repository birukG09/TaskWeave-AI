"""
TaskWeave AI - Report service
"""
from datetime import datetime, timedelta
from sqlalchemy.orm import Session
import structlog

from models.report import Report, ReportType
from models.task import Task, TaskStatus
from models.event import Event
from ai.pipelines import ReportGenerator

logger = structlog.get_logger()

class ReportService:
    def __init__(self, db: Session):
        self.db = db
    
    async def generate_report(self, org_id: str, report_type: ReportType) -> Report:
        """Generate AI-powered report"""
        # Gather data for report
        if report_type == ReportType.DAILY:
            start_date = datetime.utcnow() - timedelta(days=1)
        else:  # WEEKLY
            start_date = datetime.utcnow() - timedelta(days=7)
        
        # Get tasks data
        tasks = self.db.query(Task).filter(
            Task.org_id == org_id,
            Task.updated_at >= start_date
        ).all()
        
        # Get events data
        events = self.db.query(Event).filter(
            Event.org_id == org_id,
            Event.ingested_at >= start_date
        ).all()
        
        # Prepare data for AI
        report_data = {
            "period": report_type.value,
            "start_date": start_date.isoformat(),
            "end_date": datetime.utcnow().isoformat(),
            "tasks": {
                "total": len(tasks),
                "completed": len([t for t in tasks if t.status == TaskStatus.DONE]),
                "in_progress": len([t for t in tasks if t.status == TaskStatus.IN_PROGRESS]),
                "todo": len([t for t in tasks if t.status == TaskStatus.TODO]),
                "blocked": len([t for t in tasks if t.status == TaskStatus.BLOCKED]),
                "by_priority": {
                    "high": len([t for t in tasks if t.priority >= 4]),
                    "medium": len([t for t in tasks if t.priority == 3]),
                    "low": len([t for t in tasks if t.priority <= 2])
                }
            },
            "events": {
                "total": len(events),
                "by_provider": {}
            }
        }
        
        # Group events by provider
        for event in events:
            provider = event.provider
            if provider not in report_data["events"]["by_provider"]:
                report_data["events"]["by_provider"][provider] = 0
            report_data["events"]["by_provider"][provider] += 1
        
        # Generate AI content
        report_generator = ReportGenerator()
        ai_content = await report_generator.generate_report(report_data)
        
        # Create report
        report = Report(
            org_id=org_id,
            type=report_type,
            content={
                "summary": ai_content,
                "data": report_data,
                "generated_at": datetime.utcnow().isoformat()
            }
        )
        
        self.db.add(report)
        self.db.commit()
        self.db.refresh(report)
        
        logger.info("Report generated", report_id=str(report.id), org_id=org_id, type=report_type)
        
        return report
