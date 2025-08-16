"""
TaskWeave AI - Gmail integration
"""
from typing import Dict, Any, List, Optional
import httpx
import base64
import email
from email.mime.text import MIMEText
import structlog

from .base import BaseIntegration
from config import settings

logger = structlog.get_logger()

class GmailIntegration(BaseIntegration):
    """Gmail integration for TaskWeave AI"""
    
    def __init__(self, access_token: str, metadata: Dict[str, Any] = None):
        super().__init__(access_token, metadata)
        self.base_url = "https://gmail.googleapis.com/gmail/v1"
    
    async def test_connection(self) -> bool:
        """Test Gmail connection"""
        try:
            async with httpx.AsyncClient() as client:
                response = await client.get(
                    f"{self.base_url}/users/me/profile",
                    headers={"Authorization": f"Bearer {self.access_token}"}
                )
                return response.status_code == 200
        except Exception as e:
            logger.error("Gmail connection test failed", error=str(e))
            return False
    
    async def fetch_events(self, since: Optional[str] = None) -> List[Dict[str, Any]]:
        """Fetch Gmail emails"""
        try:
            async with httpx.AsyncClient() as client:
                # Build query for recent emails
                query = "is:unread"
                if since:
                    # Convert since to Gmail query format if needed
                    query += f" after:{since}"
                
                # Get message list
                messages_response = await client.get(
                    f"{self.base_url}/users/me/messages",
                    headers={"Authorization": f"Bearer {self.access_token}"},
                    params={"q": query, "maxResults": 50}
                )
                
                if messages_response.status_code != 200:
                    return []
                
                messages_data = messages_response.json()
                messages = messages_data.get("messages", [])
                events = []
                
                # Get full message details
                for message in messages[:20]:  # Limit to 20 messages
                    msg_response = await client.get(
                        f"{self.base_url}/users/me/messages/{message['id']}",
                        headers={"Authorization": f"Bearer {self.access_token}"}
                    )
                    
                    if msg_response.status_code == 200:
                        msg_data = msg_response.json()
                        
                        # Extract email headers
                        headers = {h["name"]: h["value"] for h in msg_data.get("payload", {}).get("headers", [])}
                        
                        # Extract email body
                        body = self._extract_body(msg_data.get("payload", {}))
                        
                        events.append(await self.normalize_event({
                            "id": f"email-{message['id']}",
                            "type": "email",
                            "subject": headers.get("Subject", ""),
                            "from": headers.get("From", ""),
                            "to": headers.get("To", ""),
                            "body": body,
                            "timestamp": msg_data.get("internalDate"),
                            "labels": msg_data.get("labelIds", []),
                            "raw": msg_data
                        }))
                
                return events
                
        except Exception as e:
            logger.error("Failed to fetch Gmail events", error=str(e))
            return []
    
    async def create_task(self, task_data: Dict[str, Any]) -> bool:
        """Send email with task details"""
        try:
            to_email = self.metadata.get("notification_email")
            if not to_email:
                return False
            
            subject = f"New Task: {task_data.get('title')}"
            body = f"""
A new task has been created:

Title: {task_data.get('title')}
Description: {task_data.get('description', 'N/A')}
Priority: {task_data.get('priority', 3)}
Labels: {', '.join(task_data.get('labels', []))}

This email was sent automatically by TaskWeave AI.
"""
            
            # Create email message
            message = MIMEText(body)
            message['to'] = to_email
            message['subject'] = subject
            
            # Encode message
            raw_message = base64.urlsafe_b64encode(message.as_bytes()).decode()
            
            async with httpx.AsyncClient() as client:
                response = await client.post(
                    f"{self.base_url}/users/me/messages/send",
                    headers={"Authorization": f"Bearer {self.access_token}"},
                    json={"raw": raw_message}
                )
                
                return response.status_code == 200
                
        except Exception as e:
            logger.error("Failed to send Gmail task notification", error=str(e))
            return False
    
    def _extract_body(self, payload: Dict[str, Any]) -> str:
        """Extract email body from Gmail payload"""
        try:
            if "parts" in payload:
                # Multipart message
                for part in payload["parts"]:
                    if part.get("mimeType") == "text/plain":
                        data = part.get("body", {}).get("data", "")
                        if data:
                            return base64.urlsafe_b64decode(data).decode('utf-8')
            else:
                # Single part message
                if payload.get("mimeType") == "text/plain":
                    data = payload.get("body", {}).get("data", "")
                    if data:
                        return base64.urlsafe_b64decode(data).decode('utf-8')
            
            return ""
        except Exception:
            return ""
