"""
TaskWeave AI - Google Drive integration
"""
from typing import Dict, Any, List, Optional
import httpx
import structlog

from .base import BaseIntegration
from config import settings

logger = structlog.get_logger()

class GDriveIntegration(BaseIntegration):
    """Google Drive integration for TaskWeave AI"""
    
    def __init__(self, access_token: str, metadata: Dict[str, Any] = None):
        super().__init__(access_token, metadata)
        self.base_url = "https://www.googleapis.com/drive/v3"
    
    async def test_connection(self) -> bool:
        """Test Google Drive connection"""
        try:
            async with httpx.AsyncClient() as client:
                response = await client.get(
                    f"{self.base_url}/about",
                    headers={"Authorization": f"Bearer {self.access_token}"},
                    params={"fields": "user"}
                )
                return response.status_code == 200
        except Exception as e:
            logger.error("Google Drive connection test failed", error=str(e))
            return False
    
    async def fetch_events(self, since: Optional[str] = None) -> List[Dict[str, Any]]:
        """Fetch Google Drive files and activities"""
        try:
            async with httpx.AsyncClient() as client:
                events = []
                
                # Get recent files
                params = {
                    "orderBy": "modifiedTime desc",
                    "pageSize": 50,
                    "fields": "files(id,name,mimeType,parents,createdTime,modifiedTime,webViewLink,owners,lastModifyingUser)"
                }
                
                if since:
                    params["q"] = f"modifiedTime > '{since}'"
                
                files_response = await client.get(
                    f"{self.base_url}/files",
                    headers={"Authorization": f"Bearer {self.access_token}"},
                    params=params
                )
                
                if files_response.status_code != 200:
                    return []
                
                files_data = files_response.json()
                files = files_data.get("files", [])
                
                for file in files:
                    # Determine file type
                    mime_type = file.get("mimeType", "")
                    file_type = "file"
                    
                    if "folder" in mime_type:
                        file_type = "folder"
                    elif "document" in mime_type:
                        file_type = "document"
                    elif "spreadsheet" in mime_type:
                        file_type = "spreadsheet"
                    elif "presentation" in mime_type:
                        file_type = "presentation"
                    
                    # Get last modifying user
                    modifier = file.get("lastModifyingUser", {})
                    
                    events.append(await self.normalize_event({
                        "id": f"file-{file['id']}",
                        "type": file_type,
                        "name": file.get("name", ""),
                        "mime_type": mime_type,
                        "url": file.get("webViewLink"),
                        "parents": file.get("parents", []),
                        "created_time": file.get("createdTime"),
                        "modified_time": file.get("modifiedTime"),
                        "timestamp": file.get("modifiedTime"),
                        "owners": [o.get("emailAddress") for o in file.get("owners", [])],
                        "last_modifier": modifier.get("emailAddress"),
                        "raw": file
                    }))
                
                # Get changes/activities (requires additional setup)
                # This would require the Drive Activity API for detailed activity tracking
                
                return events
                
        except Exception as e:
            logger.error("Failed to fetch Google Drive events", error=str(e))
            return []
    
    async def create_task(self, task_data: Dict[str, Any]) -> bool:
        """Create Google Doc with task details"""
        try:
            folder_id = self.metadata.get("default_folder_id")
            
            # Create document metadata
            file_metadata = {
                "name": f"Task: {task_data.get('title', 'Untitled Task')}",
                "mimeType": "application/vnd.google-apps.document"
            }
            
            if folder_id:
                file_metadata["parents"] = [folder_id]
            
            async with httpx.AsyncClient() as client:
                # Create empty document
                create_response = await client.post(
                    f"{self.base_url}/files",
                    headers={"Authorization": f"Bearer {self.access_token}"},
                    json=file_metadata
                )
                
                if create_response.status_code != 200:
                    return False
                
                doc = create_response.json()
                doc_id = doc["id"]
                
                # Add content to document using Google Docs API
                docs_url = f"https://docs.googleapis.com/v1/documents/{doc_id}:batchUpdate"
                
                content = f"""Task Details

Title: {task_data.get('title', 'Untitled Task')}

Description:
{task_data.get('description', 'No description provided')}

Priority: {task_data.get('priority', 3)}

Labels: {', '.join(task_data.get('labels', []))}

Created by TaskWeave AI
"""
                
                requests = [
                    {
                        "insertText": {
                            "location": {"index": 1},
                            "text": content
                        }
                    }
                ]
                
                update_response = await client.post(
                    docs_url,
                    headers={"Authorization": f"Bearer {self.access_token}"},
                    json={"requests": requests}
                )
                
                return update_response.status_code == 200
                
        except Exception as e:
            logger.error("Failed to create Google Drive task document", error=str(e))
            return False
