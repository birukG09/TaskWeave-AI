"""
TaskWeave AI - OAuth2 integration
"""
from typing import Dict, Any, Optional
import httpx
import structlog
from urllib.parse import urlencode

from config import settings

logger = structlog.get_logger()

# OAuth2 provider configurations
OAUTH_PROVIDERS = {
    "google": {
        "authorize_url": "https://accounts.google.com/o/oauth2/v2/auth",
        "token_url": "https://oauth2.googleapis.com/token",
        "user_info_url": "https://www.googleapis.com/oauth2/v2/userinfo",
        "scope": "openid email profile",
        "client_id": settings.OAUTH_GOOGLE_CLIENT_ID,
        "client_secret": settings.OAUTH_GOOGLE_CLIENT_SECRET,
    },
    "github": {
        "authorize_url": "https://github.com/login/oauth/authorize",
        "token_url": "https://github.com/login/oauth/access_token",
        "user_info_url": "https://api.github.com/user",
        "scope": "user:email",
        "client_id": settings.OAUTH_GITHUB_CLIENT_ID,
        "client_secret": settings.OAUTH_GITHUB_CLIENT_SECRET,
    },
    "slack": {
        "authorize_url": "https://slack.com/oauth/v2/authorize",
        "token_url": "https://slack.com/api/oauth.v2.access",
        "user_info_url": "https://slack.com/api/users.identity",
        "scope": "identity.basic identity.email",
        "client_id": settings.SLACK_CLIENT_ID,
        "client_secret": settings.SLACK_CLIENT_SECRET,
    }
}

def get_oauth_url(provider: str, state: str) -> Optional[str]:
    """Generate OAuth authorization URL"""
    if provider not in OAUTH_PROVIDERS:
        return None
    
    config = OAUTH_PROVIDERS[provider]
    if not config["client_id"]:
        return None
    
    params = {
        "client_id": config["client_id"],
        "response_type": "code",
        "scope": config["scope"],
        "state": state,
        "redirect_uri": f"{settings.API_BASE_URL}/api/v1/oauth/{provider}/callback"
    }
    
    return f"{config['authorize_url']}?{urlencode(params)}"

async def handle_oauth_callback(provider: str, code: str) -> Optional[Dict[str, Any]]:
    """Handle OAuth callback and get user info"""
    if provider not in OAUTH_PROVIDERS:
        return None
    
    config = OAUTH_PROVIDERS[provider]
    if not config["client_id"] or not config["client_secret"]:
        return None
    
    # Exchange code for access token
    token_data = {
        "client_id": config["client_id"],
        "client_secret": config["client_secret"],
        "code": code,
        "grant_type": "authorization_code",
        "redirect_uri": f"{settings.API_BASE_URL}/api/v1/oauth/{provider}/callback"
    }
    
    async with httpx.AsyncClient() as client:
        try:
            # Get access token
            token_response = await client.post(
                config["token_url"],
                data=token_data,
                headers={"Accept": "application/json"}
            )
            token_response.raise_for_status()
            token_json = token_response.json()
            
            access_token = token_json.get("access_token")
            if not access_token:
                logger.error("No access token in OAuth response", provider=provider)
                return None
            
            # Get user info
            headers = {"Authorization": f"Bearer {access_token}"}
            user_response = await client.get(config["user_info_url"], headers=headers)
            user_response.raise_for_status()
            user_data = user_response.json()
            
            # Normalize user data across providers
            if provider == "google":
                return {
                    "email": user_data.get("email"),
                    "name": user_data.get("name"),
                    "provider": provider,
                    "provider_id": user_data.get("id")
                }
            elif provider == "github":
                return {
                    "email": user_data.get("email"),
                    "name": user_data.get("name") or user_data.get("login"),
                    "provider": provider,
                    "provider_id": str(user_data.get("id"))
                }
            elif provider == "slack":
                return {
                    "email": user_data.get("user", {}).get("email"),
                    "name": user_data.get("user", {}).get("name"),
                    "provider": provider,
                    "provider_id": user_data.get("user", {}).get("id")
                }
            
        except Exception as e:
            logger.error("OAuth callback failed", provider=provider, error=str(e))
            return None
    
    return None
