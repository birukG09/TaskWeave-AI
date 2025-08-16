"""
TaskWeave AI - Integrations module
"""
from .slack import SlackIntegration
from .github import GitHubIntegration
from .gmail import GmailIntegration
from .trello import TrelloIntegration
from .notion import NotionIntegration
from .gdrive import GDriveIntegration

__all__ = [
    "SlackIntegration",
    "GitHubIntegration", 
    "GmailIntegration",
    "TrelloIntegration",
    "NotionIntegration",
    "GDriveIntegration"
]
