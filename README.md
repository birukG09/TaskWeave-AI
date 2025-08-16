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
# TaskWeave AI

````
           _.-``__ ''-._                                              
      _.-``    `.  `_.  ''-._           Redis 7.2.10 (00000000/0) 64 bit
  .-`` .-```.  ```\/    _.,_ ''-._                                  
 (    '      ,       .-`  | `,    )     Running in standalone mode
 |`-._`-...-` __...-.``-._|'` _.-'|     Port: 6379
 |    `-._   `._    /     _.-'    |     PID: 6506
  `-._    `-._  `-./  _.-'    _.-'                                   
 |`-._`-._    `-.__.-'    _.-'_.-'|                                  
 |    `-._`-._        _.-'_.-'    |           https://redis.io      
  `-._    `-._`-.__.-'_.-'    _.-'                                   
 |`-._`-._    `-.__.-'    _.-'_.-'|                                  
 |    `-._`-._        _.-'_.-'    |                                  
  `-._    `-._`-.__.-'_.-'    _.-'                                   
      `-._    `-.__.-'    _.-'                                       
          `-._        _.-'                                           
              `-.__.-'                                                
````

## Overview

TaskWeave AI is a production-ready backend system designed for smart task extraction and automated reporting, integrating AI with Slack and Notion.

This project demonstrates asynchronous AI orchestration, vector database memory, and multi-service integration for remote-friendly backend development.

## Features

* AI-powered task extraction using OpenAI GPT-4.1 and Anthropic Claude fallback
* Slack message monitoring and event handling
* Automated task creation in Notion workspace
* Daily and weekly AI-generated task reports sent to Slack
* Async background job processing with Celery + Redis
* Persistent storage with MySQL + SQLAlchemy
* Optional vector database (Pinecone) for context-aware AI memory
* Dockerized deployment for portability
* CI/CD friendly with GitHub Actions

## Tech Stack

* **Backend:** Flask
* **Database:** MySQL + SQLAlchemy
* **Async Processing:** Celery + Redis
* **AI Orchestration:** LangChain, OpenAI, Anthropic
* **Vector Database:** Pinecone (optional)
* **Integrations:** Slack API, Notion API
* **DevOps:** Docker, Docker Compose, GitHub Actions, Sentry for monitoring

## Environment Variables

| Variable                    | Description              |
| --------------------------- | ------------------------ |
| OPENAI\_API\_KEY            | API key for OpenAI       |
| ANTHROPIC\_API\_KEY         | API key for Anthropic    |
| NOTION\_INTEGRATION\_SECRET | Notion API secret        |
| NOTION\_DATABASE\_ID        | Notion tasks database ID |
| SLACK\_BOT\_TOKEN           | Slack bot token          |
| SLACK\_CHANNEL\_ID          | Slack channel ID         |
| MYSQL\_USER                 | MySQL username           |
| MYSQL\_PASSWORD             | MySQL password           |
| MYSQL\_HOST                 | MySQL host               |
| MYSQL\_DB                   | MySQL database name      |

## Getting Started

1. Clone the repository:

```bash
git clone https://github.com/yourusername/taskweave_ai.git
cd taskweave_ai
```

2. Copy the environment variables template:

```bash
cp .env.example .env
# Fill in your keys and database credentials
```

3. Start the services with Docker Compose:

```bash
docker-compose up --build
```

4. Access the API endpoints:

* `/extract-tasks` → Send text/messages to extract tasks
* `/daily-report` → Generate daily report and send to Slack

## Contributing

1. Fork the repository
2. Create a feature branch
3. Commit your changes with clear messages
4. Open a Pull Request

## License

MIT
