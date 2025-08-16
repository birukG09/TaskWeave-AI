"""
TaskWeave AI - Report generation worker
"""
import asyncio
from datetime import datetime, timedelta
from typing import Dict, Any
from sqlalchemy.orm import Session
import structlog

from database import SessionLocal
from models.organization import Organization
from models.report import Report, ReportType
from services.report_service import ReportService

logger = structlog.get_logger()

class ReportWorker:
    """Background worker for generating scheduled reports"""
    
    def __init__(self):
        pass
    
    async def generate_daily_reports(self) -> None:
        """Generate daily reports for all organizations"""
        db = SessionLocal()
        try:
            # Get all organizations
            organizations = db.query(Organization).all()
            
            logger.info("Generating daily reports", org_count=len(organizations))
            
            for org in organizations:
                try:
                    await self._generate_report_for_org(org.id, ReportType.DAILY)
                except Exception as e:
                    logger.error("Daily report generation failed", 
                               org_id=str(org.id), error=str(e))
            
        except Exception as e:
            logger.error("Daily reports batch failed", error=str(e))
        finally:
            db.close()
    
    async def generate_weekly_reports(self) -> None:
        """Generate weekly reports for all organizations"""
        db = SessionLocal()
        try:
            # Get all organizations
            organizations = db.query(Organization).all()
            
            logger.info("Generating weekly reports", org_count=len(organizations))
            
            for org in organizations:
                try:
                    await self._generate_report_for_org(org.id, ReportType.WEEKLY)
                except Exception as e:
                    logger.error("Weekly report generation failed", 
                               org_id=str(org.id), error=str(e))
            
        except Exception as e:
            logger.error("Weekly reports batch failed", error=str(e))
        finally:
            db.close()
    
    async def _generate_report_for_org(self, org_id: str, report_type: ReportType) -> None:
        """Generate report for specific organization"""
        db = SessionLocal()
        try:
            # Check if report already exists for today/this week
            today = datetime.utcnow().date()
            
            if report_type == ReportType.DAILY:
                start_of_period = datetime.combine(today, datetime.min.time())
            else:  # WEEKLY
                # Get start of week (Monday)
                days_since_monday = today.weekday()
                start_of_week = today - timedelta(days=days_since_monday)
                start_of_period = datetime.combine(start_of_week, datetime.min.time())
            
            existing_report = db.query(Report).filter(
                Report.org_id == org_id,
                Report.type == report_type,
                Report.generated_at >= start_of_period
            ).first()
            
            if existing_report:
                logger.info("Report already exists", 
                           org_id=org_id, type=report_type.value)
                return
            
            # Generate new report
            report_service = ReportService(db)
            report = await report_service.generate_report(org_id, report_type)
            
            logger.info("Report generated", 
                       org_id=org_id, 
                       type=report_type.value,
                       report_id=str(report.id))
            
        except Exception as e:
            logger.error("Report generation failed", 
                        org_id=org_id, type=report_type.value, error=str(e))
        finally:
            db.close()
    
    async def run_scheduler(self) -> None:
        """Run report generation scheduler"""
        logger.info("Starting report generation scheduler")
        
        last_daily_run = None
        last_weekly_run = None
        
        while True:
            try:
                now = datetime.utcnow()
                current_hour = now.hour
                current_day = now.weekday()  # 0 = Monday
                
                # Generate daily reports at 8 AM UTC
                if current_hour == 8 and (not last_daily_run or last_daily_run.date() != now.date()):
                    await self.generate_daily_reports()
                    last_daily_run = now
                
                # Generate weekly reports on Monday at 9 AM UTC
                if (current_day == 0 and current_hour == 9 and 
                    (not last_weekly_run or (now - last_weekly_run).days >= 7)):
                    await self.generate_weekly_reports()
                    last_weekly_run = now
                
                # Sleep for 1 hour
                await asyncio.sleep(3600)
                
            except Exception as e:
                logger.error("Report scheduler error", error=str(e))
                await asyncio.sleep(300)  # 5 minute sleep on error
    
    async def generate_on_demand_report(self, org_id: str, report_type: ReportType) -> str:
        """Generate report on demand"""
        db = SessionLocal()
        try:
            report_service = ReportService(db)
            report = await report_service.generate_report(org_id, report_type)
            
            logger.info("On-demand report generated", 
                       org_id=org_id, 
                       type=report_type.value,
                       report_id=str(report.id))
            
            return str(report.id)
            
        except Exception as e:
            logger.error("On-demand report generation failed", 
                        org_id=org_id, type=report_type.value, error=str(e))
            raise
        finally:
            db.close()
