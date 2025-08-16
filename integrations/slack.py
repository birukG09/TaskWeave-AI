"""
TaskWeave AI - Slack integration
"""
from typing import Dict, Any, List, Optional
import httpx
import structlog

from .base import BaseIntegration
from config import settings

logger = structlog.get_logger()

class SlackIntegration(BaseIntegration):
    """Slack integration for TaskWeave AI"""
    
    def __init__(self, access_token: str, metadata: Dict[str, Any] = None):
        super().__init__(access_token, metadata)
        self.base_url = "https://slack.com/api"
    
    async def test_connection(self) -> bool:
        """Test Slack connection"""
        try:
            async with httpx.AsyncClient() as client:
                response = await client.get(
                    f"{self.base_url}/auth.test",
                    headers={"Authorization": f"Bearer {self.access_token}"}
                )
                return response.status_code == 200 and response.json().get("ok", False)
        except Exception as e:
            logger.error("Slack connection test failed", error=str(e))
            return False
    
    async def fetch_events(self, since: Optional[str] = None) -> List[Dict[str, Any]]:
        """Fetch Slack messages and events"""
        try:
            async with httpx.AsyncClient() as client:
                # Get channel list
                channels_response = await client.get(
                    f"{self.base_url}/conversations.list",
                    headers={"Authorization": f"Bearer {self.access_token}"},
                    params={"types": "public_channel,private_channel"}
                )
                
                if not channels_response.json().get("ok", False):
                    return []
                
                channels = channels_response.json().get("channels", [])
                events = []
                
                # Get messages from each channel
                for channel in channels[:5]:  # Limit to first 5 channels
                    messages_response = await client.get(
                        f"{self.base_url}/conversations.history",
                        headers={"Authorization": f"Bearer {self.access_token}"},
                        params={
                            "channel": channel["id"],
                            "limit": 50,
                            "oldest": since
                        }
                    )
                    
                    if messages_response.json().get("ok", False):
                        messages = messages_response.json().get("messages", [])
                        for message in messages:
                            events.append(await self.normalize_event({
                                "id": message.get("ts"),
                                "type": "message",
                                "channel": channel["name"],
                                "channel_id": channel["id"],
                                "user": message.get("user"),
                                "text": message.get("text"),
                                "timestamp": message.get("ts"),
                                "raw": message
                            }))
                
                return events
                
        except Exception as e:
            logger.error("Failed to fetch Slack events", error=str(e))
            return []
    
    async def create_task(self, task_data: Dict[str, Any]) -> bool:
        """Post task as Slack message"""
        try:
            channel_id = self.metadata.get("default_channel")
            if not channel_id:
                return False
            
            message = f"📋 *New Task:* {task_data.get('title')}"
            if task_data.get('description'):
                message += f"\n{task_data['description']}"
            
            async with httpx.AsyncClient() as client:
                response = await client.post(
                    f"{self.base_url}/chat.postMessage",
                    headers={"Authorization": f"Bearer {self.access_token}"},
                    json={
                        "channel": channel_id,
                        "text": message,
                        "unfurl_links": False
                    }
                )
                
                return response.status_code == 200 and response.json().get("ok", False)
                
        except Exception as e:
            logger.error("Failed to create Slack task", error=str(e))
            return False
