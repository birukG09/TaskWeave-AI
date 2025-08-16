"""
TaskWeave AI - Notion integration
"""
from typing import Dict, Any, List, Optional
import httpx
import structlog

from .base import BaseIntegration
from config import settings

logger = structlog.get_logger()

class NotionIntegration(BaseIntegration):
    """Notion integration for TaskWeave AI"""
    
    def __init__(self, access_token: str, metadata: Dict[str, Any] = None):
        super().__init__(access_token, metadata)
        self.base_url = "https://api.notion.com/v1"
        self.headers = {
            "Authorization": f"Bearer {self.access_token}",
            "Notion-Version": "2022-06-28",
            "Content-Type": "application/json"
        }
    
    async def test_connection(self) -> bool:
        """Test Notion connection"""
        try:
            async with httpx.AsyncClient() as client:
                response = await client.get(
                    f"{self.base_url}/users/me",
                    headers=self.headers
                )
                return response.status_code == 200
        except Exception as e:
            logger.error("Notion connection test failed", error=str(e))
            return False
    
    async def fetch_events(self, since: Optional[str] = None) -> List[Dict[str, Any]]:
        """Fetch Notion pages and database entries"""
        try:
            async with httpx.AsyncClient() as client:
                events = []
                
                # Search for recently updated pages
                search_payload = {
                    "query": "",
                    "sort": {
                        "direction": "descending",
                        "timestamp": "last_edited_time"
                    },
                    "page_size": 50
                }
                
                if since:
                    search_payload["filter"] = {
                        "property": "last_edited_time",
                        "date": {"after": since}
                    }
                
                search_response = await client.post(
                    f"{self.base_url}/search",
                    headers=self.headers,
                    json=search_payload
                )
                
                if search_response.status_code != 200:
                    return []
                
                search_results = search_response.json()
                results = search_results.get("results", [])
                
                for result in results:
                    if result.get("object") == "page":
                        # Get page properties
                        properties = result.get("properties", {})
                        
                        # Extract title
                        title = ""
                        for prop_name, prop_value in properties.items():
                            if prop_value.get("type") == "title":
                                title_array = prop_value.get("title", [])
                                if title_array:
                                    title = title_array[0].get("plain_text", "")
                                break
                        
                        events.append(await self.normalize_event({
                            "id": f"page-{result['id']}",
                            "type": "page",
                            "title": title or "Untitled",
                            "url": result.get("url"),
                            "parent": result.get("parent", {}),
                            "properties": properties,
                            "timestamp": result.get("last_edited_time"),
                            "created_time": result.get("created_time"),
                            "raw": result
                        }))
                    
                    elif result.get("object") == "database":
                        events.append(await self.normalize_event({
                            "id": f"database-{result['id']}",
                            "type": "database",
                            "title": result.get("title", [{}])[0].get("plain_text", "Untitled Database"),
                            "url": result.get("url"),
                            "properties": result.get("properties", {}),
                            "timestamp": result.get("last_edited_time"),
                            "created_time": result.get("created_time"),
                            "raw": result
                        }))
                
                return events
                
        except Exception as e:
            logger.error("Failed to fetch Notion events", error=str(e))
            return []
    
    async def create_task(self, task_data: Dict[str, Any]) -> bool:
        """Create Notion page"""
        try:
            parent_id = self.metadata.get("default_parent_id")
            if not parent_id:
                return False
            
            # Determine if parent is a page or database
            parent_type = self.metadata.get("parent_type", "page")
            
            if parent_type == "database":
                # Create database entry
                page_data = {
                    "parent": {"database_id": parent_id},
                    "properties": {
                        "Name": {
                            "title": [
                                {
                                    "text": {
                                        "content": task_data.get("title", "Untitled Task")
                                    }
                                }
                            ]
                        }
                    }
                }
                
                # Add description if available
                if task_data.get("description"):
                    page_data["children"] = [
                        {
                            "object": "block",
                            "type": "paragraph",
                            "paragraph": {
                                "rich_text": [
                                    {
                                        "type": "text",
                                        "text": {
                                            "content": task_data["description"]
                                        }
                                    }
                                ]
                            }
                        }
                    ]
            else:
                # Create page
                page_data = {
                    "parent": {"page_id": parent_id},
                    "properties": {
                        "title": [
                            {
                                "text": {
                                    "content": task_data.get("title", "Untitled Task")
                                }
                            }
                        ]
                    }
                }
                
                if task_data.get("description"):
                    page_data["children"] = [
                        {
                            "object": "block",
                            "type": "paragraph",
                            "paragraph": {
                                "rich_text": [
                                    {
                                        "type": "text",
                                        "text": {
                                            "content": task_data["description"]
                                        }
                                    }
                                ]
                            }
                        }
                    ]
            
            async with httpx.AsyncClient() as client:
                response = await client.post(
                    f"{self.base_url}/pages",
                    headers=self.headers,
                    json=page_data
                )
                
                return response.status_code == 200
                
        except Exception as e:
            logger.error("Failed to create Notion page", error=str(e))
            return False
