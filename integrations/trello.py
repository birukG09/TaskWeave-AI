"""
TaskWeave AI - Trello integration
"""
from typing import Dict, Any, List, Optional
import httpx
import structlog

from .base import BaseIntegration
from config import settings

logger = structlog.get_logger()

class TrelloIntegration(BaseIntegration):
    """Trello integration for TaskWeave AI"""
    
    def __init__(self, access_token: str, metadata: Dict[str, Any] = None):
        super().__init__(access_token, metadata)
        self.base_url = "https://api.trello.com/1"
        self.api_key = settings.TRELLO_KEY
    
    async def test_connection(self) -> bool:
        """Test Trello connection"""
        try:
            async with httpx.AsyncClient() as client:
                response = await client.get(
                    f"{self.base_url}/members/me",
                    params={"key": self.api_key, "token": self.access_token}
                )
                return response.status_code == 200
        except Exception as e:
            logger.error("Trello connection test failed", error=str(e))
            return False
    
    async def fetch_events(self, since: Optional[str] = None) -> List[Dict[str, Any]]:
        """Fetch Trello cards and board activities"""
        try:
            async with httpx.AsyncClient() as client:
                events = []
                
                # Get user boards
                boards_response = await client.get(
                    f"{self.base_url}/members/me/boards",
                    params={"key": self.api_key, "token": self.access_token}
                )
                
                if boards_response.status_code != 200:
                    return []
                
                boards = boards_response.json()
                
                for board in boards[:5]:  # Limit to 5 boards
                    board_id = board["id"]
                    
                    # Get cards from board
                    cards_response = await client.get(
                        f"{self.base_url}/boards/{board_id}/cards",
                        params={"key": self.api_key, "token": self.access_token}
                    )
                    
                    if cards_response.status_code == 200:
                        cards = cards_response.json()
                        for card in cards:
                            events.append(await self.normalize_event({
                                "id": f"card-{card['id']}",
                                "type": "card",
                                "board": board["name"],
                                "board_id": board_id,
                                "list_id": card.get("idList"),
                                "name": card["name"],
                                "description": card.get("desc", ""),
                                "due_date": card.get("due"),
                                "labels": [l["name"] for l in card.get("labels", [])],
                                "members": card.get("idMembers", []),
                                "timestamp": card.get("dateLastActivity"),
                                "url": card.get("url"),
                                "closed": card.get("closed", False),
                                "raw": card
                            }))
                    
                    # Get recent board activities
                    activities_response = await client.get(
                        f"{self.base_url}/boards/{board_id}/actions",
                        params={
                            "key": self.api_key, 
                            "token": self.access_token,
                            "limit": 20,
                            "since": since
                        }
                    )
                    
                    if activities_response.status_code == 200:
                        activities = activities_response.json()
                        for activity in activities:
                            events.append(await self.normalize_event({
                                "id": f"activity-{activity['id']}",
                                "type": "activity",
                                "board": board["name"],
                                "board_id": board_id,
                                "action_type": activity.get("type"),
                                "member": activity.get("memberCreator", {}).get("username"),
                                "data": activity.get("data", {}),
                                "timestamp": activity.get("date"),
                                "raw": activity
                            }))
                
                return events
                
        except Exception as e:
            logger.error("Failed to fetch Trello events", error=str(e))
            return []
    
    async def create_task(self, task_data: Dict[str, Any]) -> bool:
        """Create Trello card"""
        try:
            list_id = self.metadata.get("default_list_id")
            if not list_id:
                return False
            
            card_data = {
                "key": self.api_key,
                "token": self.access_token,
                "name": task_data.get("title"),
                "desc": task_data.get("description", ""),
                "idList": list_id
            }
            
            if task_data.get("due_date"):
                card_data["due"] = task_data["due_date"]
            
            async with httpx.AsyncClient() as client:
                response = await client.post(
                    f"{self.base_url}/cards",
                    params=card_data
                )
                
                if response.status_code == 200:
                    card = response.json()
                    
                    # Add labels if specified
                    labels = task_data.get("labels", [])
                    if labels:
                        for label_name in labels:
                            await client.post(
                                f"{self.base_url}/cards/{card['id']}/labels",
                                params={
                                    "key": self.api_key,
                                    "token": self.access_token,
                                    "name": label_name
                                }
                            )
                    
                    return True
                
                return False
                
        except Exception as e:
            logger.error("Failed to create Trello card", error=str(e))
            return False
