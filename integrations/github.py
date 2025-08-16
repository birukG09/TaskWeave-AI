"""
TaskWeave AI - GitHub integration
"""
from typing import Dict, Any, List, Optional
import httpx
import structlog

from .base import BaseIntegration
from config import settings

logger = structlog.get_logger()

class GitHubIntegration(BaseIntegration):
    """GitHub integration for TaskWeave AI"""
    
    def __init__(self, access_token: str, metadata: Dict[str, Any] = None):
        super().__init__(access_token, metadata)
        self.base_url = "https://api.github.com"
    
    async def test_connection(self) -> bool:
        """Test GitHub connection"""
        try:
            async with httpx.AsyncClient() as client:
                response = await client.get(
                    f"{self.base_url}/user",
                    headers={"Authorization": f"token {self.access_token}"}
                )
                return response.status_code == 200
        except Exception as e:
            logger.error("GitHub connection test failed", error=str(e))
            return False
    
    async def fetch_events(self, since: Optional[str] = None) -> List[Dict[str, Any]]:
        """Fetch GitHub issues, PRs, and commits"""
        try:
            async with httpx.AsyncClient() as client:
                events = []
                
                # Get user repositories
                repos_response = await client.get(
                    f"{self.base_url}/user/repos",
                    headers={"Authorization": f"token {self.access_token}"},
                    params={"sort": "updated", "per_page": 10}
                )
                
                if repos_response.status_code != 200:
                    return []
                
                repos = repos_response.json()
                
                for repo in repos:
                    repo_name = repo["full_name"]
                    
                    # Get recent issues
                    issues_response = await client.get(
                        f"{self.base_url}/repos/{repo_name}/issues",
                        headers={"Authorization": f"token {self.access_token}"},
                        params={"state": "all", "since": since, "per_page": 20}
                    )
                    
                    if issues_response.status_code == 200:
                        issues = issues_response.json()
                        for issue in issues:
                            # Skip pull requests (they appear in issues API)
                            if "pull_request" not in issue:
                                events.append(await self.normalize_event({
                                    "id": f"issue-{issue['id']}",
                                    "type": "issue",
                                    "repo": repo_name,
                                    "title": issue["title"],
                                    "body": issue["body"],
                                    "state": issue["state"],
                                    "assignees": [a["login"] for a in issue.get("assignees", [])],
                                    "labels": [l["name"] for l in issue.get("labels", [])],
                                    "timestamp": issue["updated_at"],
                                    "url": issue["html_url"],
                                    "raw": issue
                                }))
                    
                    # Get recent pull requests
                    prs_response = await client.get(
                        f"{self.base_url}/repos/{repo_name}/pulls",
                        headers={"Authorization": f"token {self.access_token}"},
                        params={"state": "all", "per_page": 10}
                    )
                    
                    if prs_response.status_code == 200:
                        prs = prs_response.json()
                        for pr in prs:
                            events.append(await self.normalize_event({
                                "id": f"pr-{pr['id']}",
                                "type": "pull_request",
                                "repo": repo_name,
                                "title": pr["title"],
                                "body": pr["body"],
                                "state": pr["state"],
                                "assignees": [a["login"] for a in pr.get("assignees", [])],
                                "timestamp": pr["updated_at"],
                                "url": pr["html_url"],
                                "raw": pr
                            }))
                
                return events
                
        except Exception as e:
            logger.error("Failed to fetch GitHub events", error=str(e))
            return []
    
    async def create_task(self, task_data: Dict[str, Any]) -> bool:
        """Create GitHub issue"""
        try:
            repo_name = self.metadata.get("default_repo")
            if not repo_name:
                return False
            
            issue_data = {
                "title": task_data.get("title"),
                "body": task_data.get("description", ""),
                "labels": task_data.get("labels", [])
            }
            
            if task_data.get("assignee"):
                issue_data["assignees"] = [task_data["assignee"]]
            
            async with httpx.AsyncClient() as client:
                response = await client.post(
                    f"{self.base_url}/repos/{repo_name}/issues",
                    headers={"Authorization": f"token {self.access_token}"},
                    json=issue_data
                )
                
                return response.status_code == 201
                
        except Exception as e:
            logger.error("Failed to create GitHub issue", error=str(e))
            return False
