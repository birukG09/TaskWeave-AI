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

TaskWeave AI is a cutting-edge task automation and orchestration platform designed for small to medium remote teams. It intelligently extracts actionable tasks from messages, emails, and events, then organizes, prioritizes, and reports them across multiple services like Slack, Notion, and more. With a robust asynchronous backend and AI orchestration, TaskWeave is built for scalability, reliability, and production-ready deployment.

This platform demonstrates:

* Advanced AI orchestration using OpenAI GPT-4.1 and Anthropic Claude fallback
* Asynchronous processing for seamless multi-service automation
* Contextual task memory with vector database support
* Remote-friendly architecture suitable for small team operations

## Key Features

* **Multi-Service Integration:** Connect Slack, GitHub, Gmail, Trello, Notion, and Google Drive for comprehensive workflow automation.
* **Smart Task Extraction:** AI-powered extraction identifies actionable tasks from messages, comments, emails, and event feeds.
* **Intelligent Prioritization:** Assigns task priority scores using AI-driven context analysis considering urgency, importance, and deadlines.
* **Automation Engine:** Rule-based triggers execute cross-app actions, such as creating tasks in Notion when a Slack message matches criteria.
* **Automated Reports:** Generate daily or weekly summaries of team progress, task status, and AI insights.
* **Enterprise-Grade Security:** Implements JWT authentication, OAuth2 integrations, and OWASP best practices.
* **Scalable Architecture:** Flask backend, Redis + Celery for async tasks, MySQL for persistent storage, Dockerized deployment.

## Tech Stack

* **Backend:** Flask
* **Database:** MySQL + SQLAlchemy
* **Async Processing:** Celery + Redis
* **AI Orchestration:** LangChain, OpenAI, Anthropic
* **Vector Database (Optional):** Pinecone for contextual memory
* **Integrations:** Slack API, Notion API, Google APIs, GitHub
* **DevOps & Monitoring:** Docker, Docker Compose, GitHub Actions, Sentry for error tracking

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

## Quick Start

### Prerequisites

* Python 3.11+
* MySQL 8+ or 5.7+
* Redis 7+
* Docker & Docker Compose (recommended for production)

### Using Docker Compose (Recommended)

1. Clone the repository:

```bash
git clone https://github.com/yourusername/taskweave_ai.git
cd taskweave_ai
```

2. Copy environment variables template and update with your secrets:

```bash
cp .env.example .env
# Fill in your keys and database credentials
```

3. Start all services:

```bash
docker-compose up --build
```

4. API Endpoints:

* `/extract-tasks` → Accepts messages and extracts tasks
* `/daily-report` → Generates AI-powered task report and posts to Slack

## Contributing

1. Fork the repository
2. Create a feature branch
3. Commit your changes with descriptive messages
4. Open a Pull Request

## License

MIT

## Contact & Support

For questions, support, or collaboration, reach out at **[support@taskweave.ai](mailto:support@taskweave.ai)** or open an issue in the repository.
