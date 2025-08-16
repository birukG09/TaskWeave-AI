# TaskWeave

Task automation & orchestration platform for small remote teams.

## Features

- **Multi-Service Integration**: Connect with Slack, GitHub, Gmail, Trello, Notion, and Google Drive
- **Smart Task Extraction**: Automatically extract actionable tasks from communications and events
- **Intelligent Prioritization**: Context-driven priority scoring based on urgency and importance
- **Automation Engine**: Rule-based automations to trigger cross-app actions
- **Automated Reports**: Daily and weekly summaries and progress reports
- **Enterprise Security**: JWT authentication, OAuth2 integration, OWASP security practices
- **Scalable Architecture**: FastAPI backend with Redis queues and PostgreSQL database

## Quick Start

### Prerequisites

- Python 3.11+
- PostgreSQL 15+
- Redis 7+
- Docker & Docker Compose (recommended)

### Using Docker Compose (Recommended)

1. Clone the repository:
```bash
git clone <repository-url>
cd taskweave
