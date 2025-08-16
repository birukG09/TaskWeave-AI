"""
TaskWeave AI - Celery tasks for Notion integration
"""
import logging
import os
from celery import current_app as celery_app
from notion_client import Client
from simple_app import app

logger = logging.getLogger(__name__)

# Initialize Notion client
notion_client = None
notion_database_id = None

def get_notion_client():
    """Get initialized Notion client"""
    global notion_client, notion_database_id
    
    if not notion_client:
        notion_secret = os.environ.get('NOTION_INTEGRATION_SECRET')
        notion_database_id = os.environ.get('NOTION_DATABASE_ID')
        
        if notion_secret and notion_database_id:
            notion_client = Client(auth=notion_secret)
            logger.info("Notion client initialized")
        else:
            logger.warning("Notion credentials not available")
    
    return notion_client

@celery_app.task
def sync_task_to_notion(task_data):
    """Sync task to Notion database"""
    try:
        with app.app_context():
            client = get_notion_client()
            if not client or not notion_database_id:
                return {'status': 'error', 'message': 'Notion not configured'}
            
            # Create page in Notion database
            notion_page = {
                "parent": {"database_id": notion_database_id},
                "properties": {
                    "Title": {
                        "title": [
                            {
                                "text": {
                                    "content": task_data.get('title', 'Untitled Task')
                                }
                            }
                        ]
                    },
                    "Status": {
                        "select": {
                            "name": task_data.get('status', 'Open').title()
                        }
                    },
                    "Priority": {
                        "select": {
                            "name": task_data.get('priority', 'Medium').title()
                        }
                    },
                    "Source": {
                        "rich_text": [
                            {
                                "text": {
                                    "content": task_data.get('source', 'manual')
                                }
                            }
                        ]
                    }
                }
            }
            
            # Add description if provided
            if task_data.get('description'):
                notion_page["children"] = [
                    {
                        "object": "block",
                        "type": "paragraph",
                        "paragraph": {
                            "rich_text": [
                                {
                                    "type": "text",
                                    "text": {
                                        "content": task_data['description']
                                    }
                                }
                            ]
                        }
                    }
                ]
            
            # Create the page
            response = client.pages.create(**notion_page)
            
            logger.info(f"Task synced to Notion: {response['id']}")
            return {
                'status': 'success',
                'notion_page_id': response['id'],
                'task_title': task_data.get('title')
            }
            
    except Exception as e:
        logger.error(f"Notion sync failed: {e}")
        return {'status': 'error', 'message': str(e)}

@celery_app.task
def update_notion_task_status(notion_page_id, new_status):
    """Update task status in Notion"""
    try:
        with app.app_context():
            client = get_notion_client()
            if not client:
                return {'status': 'error', 'message': 'Notion not configured'}
            
            # Update page properties
            response = client.pages.update(
                page_id=notion_page_id,
                properties={
                    "Status": {
                        "select": {
                            "name": new_status.title()
                        }
                    }
                }
            )
            
            logger.info(f"Notion task status updated: {notion_page_id} -> {new_status}")
            return {
                'status': 'success',
                'notion_page_id': notion_page_id,
                'new_status': new_status
            }
            
    except Exception as e:
        logger.error(f"Notion status update failed: {e}")
        return {'status': 'error', 'message': str(e)}

@celery_app.task
def create_notion_report(report_data):
    """Create progress report in Notion"""
    try:
        with app.app_context():
            client = get_notion_client()
            if not client:
                return {'status': 'error', 'message': 'Notion not configured'}
            
            # Create a new page for the report
            report_page = {
                "parent": {"database_id": notion_database_id},
                "properties": {
                    "Title": {
                        "title": [
                            {
                                "text": {
                                    "content": report_data.get('title', 'Progress Report')
                                }
                            }
                        ]
                    },
                    "Type": {
                        "select": {
                            "name": "Report"
                        }
                    }
                },
                "children": [
                    {
                        "object": "block",
                        "type": "heading_2",
                        "heading_2": {
                            "rich_text": [
                                {
                                    "type": "text",
                                    "text": {
                                        "content": "Executive Summary"
                                    }
                                }
                            ]
                        }
                    },
                    {
                        "object": "block",
                        "type": "paragraph",
                        "paragraph": {
                            "rich_text": [
                                {
                                    "type": "text",
                                    "text": {
                                        "content": report_data.get('content', 'Report content not available.')
                                    }
                                }
                            ]
                        }
                    }
                ]
            }
            
            response = client.pages.create(**report_page)
            
            logger.info(f"Report created in Notion: {response['id']}")
            return {
                'status': 'success',
                'notion_page_id': response['id'],
                'report_title': report_data.get('title')
            }
            
    except Exception as e:
        logger.error(f"Notion report creation failed: {e}")
        return {'status': 'error', 'message': str(e)}

@celery_app.task
def bulk_sync_tasks_to_notion(tasks_list):
    """Bulk sync multiple tasks to Notion"""
    try:
        with app.app_context():
            client = get_notion_client()
            if not client:
                return {'status': 'error', 'message': 'Notion not configured'}
            
            synced_tasks = []
            failed_tasks = []
            
            for task_data in tasks_list:
                try:
                    # Use the individual sync task
                    result = sync_task_to_notion.apply_async(args=[task_data]).get()
                    if result['status'] == 'success':
                        synced_tasks.append(result)
                    else:
                        failed_tasks.append({'task': task_data, 'error': result['message']})
                except Exception as e:
                    failed_tasks.append({'task': task_data, 'error': str(e)})
            
            logger.info(f"Bulk sync completed: {len(synced_tasks)} success, {len(failed_tasks)} failed")
            return {
                'status': 'completed',
                'synced_count': len(synced_tasks),
                'failed_count': len(failed_tasks),
                'synced_tasks': synced_tasks,
                'failed_tasks': failed_tasks
            }
            
    except Exception as e:
        logger.error(f"Bulk Notion sync failed: {e}")
        return {'status': 'error', 'message': str(e)}