# TaskWeave - API Documentation

## Overview

TaskWeave provides a REST API for task automation and orchestration. The API is built with Flask and uses JWT authentication.

**Base URL**: `http://localhost:5000/api/v1`

## Authentication

### Registration
```bash
POST /api/v1/auth/register
Content-Type: application/json

{
  "email": "user@example.com",
  "password": "securepassword123",
  "full_name": "John Doe"
}
```

**Response:**
```json
{
  "access_token": "eyJ...",
  "refresh_token": "eyJ...",
  "user": {
    "id": "uuid",
    "email": "user@example.com", 
    "full_name": "John Doe"
  }
}
```

### Login
```bash
POST /api/v1/auth/login
Content-Type: application/json

{
  "email": "user@example.com",
  "password": "securepassword123"
}
```

### Get Current User
```bash
GET /api/v1/auth/me
Authorization: Bearer <access_token>
```

### Refresh Token
```bash
POST /api/v1/auth/refresh
Authorization: Bearer <refresh_token>
```

## Core Endpoints

### Health Check
```bash
GET /healthz
```
**Response:**
```json
{
  "status": "healthy",
  "version": "1.0.0"
}
```

### API Information
```bash
GET /api/v1
```

## Task Management

### Get Tasks
```bash
GET /api/v1/orgs/{org_id}/projects/{project_id}/tasks
Authorization: Bearer <access_token>
```

**Sample Response:**
```json
[
  {
    "id": "1",
    "title": "Sample AI-extracted Task",
    "description": "This task was automatically created from a Slack message using AI",
    "status": "open",
    "priority": "medium",
    "project_id": "1",
    "source": "slack",
    "created_at": "2024-01-01T00:00:00Z"
  },
  {
    "id": "2",
    "title": "Review GitHub PR #123", 
    "description": "AI detected this GitHub PR needs review based on team activity",
    "status": "in_progress",
    "priority": "high",
    "project_id": "1", 
    "source": "github",
    "created_at": "2024-01-01T01:00:00Z"
  }
]
```

### Create Task
```bash
POST /api/v1/orgs/{org_id}/projects/{project_id}/tasks
Authorization: Bearer <access_token>
Content-Type: application/json

{
  "title": "New Task",
  "description": "Task description",
  "priority": "high"
}
```

## Organizations

### Get Organizations
```bash
GET /api/v1/orgs
Authorization: Bearer <access_token>
```

**Response:**
```json
[
  {
    "id": "1",
    "name": "My Organization",
    "description": "Default organization for TaskWeave AI",
    "role": "owner"
  }
]
```

## Integrations

### Get Integrations
```bash
GET /api/v1/orgs/{org_id}/integrations
Authorization: Bearer <access_token>
```

**Response:**
```json
[
  {
    "id": "1",
    "type": "slack",
    "name": "Slack Integration",
    "status": "connected",
    "last_sync": "2024-01-01T00:00:00Z"
  },
  {
    "id": "2", 
    "type": "github",
    "name": "GitHub Integration",
    "status": "connected",
    "last_sync": "2024-01-01T00:30:00Z"
  }
]
```

## Reports

### Get Reports
```bash
GET /api/v1/orgs/{org_id}/reports
Authorization: Bearer <access_token>
```

**Response:**
```json
[
  {
    "id": "1",
    "title": "Weekly Progress Report",
    "type": "progress", 
    "period": "weekly",
    "generated_at": "2024-01-01T00:00:00Z",
    "summary": "AI-generated summary: This week your team completed 8 tasks, with 3 high-priority items resolved. Slack activity increased by 20% and 5 new GitHub issues were created."
  }
]
```

## Webhooks

### Slack Webhook
```bash
POST /api/v1/webhooks/slack
Content-Type: application/json
```

This endpoint handles Slack webhook events for URL verification and message processing.

## Error Responses

All endpoints return JSON error responses:

```json
{
  "error": "Error description"
}
```

Common HTTP status codes:
- `200` - Success
- `201` - Created  
- `400` - Bad Request
- `401` - Unauthorized
- `404` - Not Found
- `422` - Validation Error
- `503` - Service Unavailable

## Testing Examples

### Complete Authentication Flow
```bash
# 1. Register
curl -X POST http://localhost:5000/api/v1/auth/register \
  -H "Content-Type: application/json" \
  -d '{"email": "test@example.com", "password": "testpass123", "full_name": "Test User"}'

# 2. Login and extract token
TOKEN=$(curl -s -X POST http://localhost:5000/api/v1/auth/login \
  -H "Content-Type: application/json" \
  -d '{"email": "test@example.com", "password": "testpass123"}' | \
  python3 -c "import json, sys; data=json.load(sys.stdin); print(data['access_token'])")

# 3. Test protected endpoint
curl -X GET http://localhost:5000/api/v1/auth/me \
  -H "Authorization: Bearer $TOKEN"

# 4. Get tasks
curl -X GET "http://localhost:5000/api/v1/orgs/1/projects/1/tasks" \
  -H "Authorization: Bearer $TOKEN"
```

## AI & Automation Endpoints

### Analyze Text for Tasks
```bash
POST /api/v1/analyze-text
Authorization: Bearer <access_token>
Content-Type: application/json

{
  "text": "We need to review the API documentation and fix the authentication bug by Friday. @john should create a dashboard.",
  "source": "slack"
}
```

**Response:**
```json
{
  "status": "success",
  "tasks_extracted": 2,
  "tasks": [
    {
      "title": "review the API documentation",
      "description": "We need to review the API documentation and fix the authentication bug by Friday",
      "priority": "medium",
      "assignee": "unassigned",
      "due_date": "Friday",
      "source": "slack",
      "extracted_by": "rule_based"
    }
  ]
}
```

### Generate Report  
```bash
POST /api/v1/generate-report
Authorization: Bearer <access_token>
Content-Type: application/json

{
  "org_id": "my_org",
  "project_id": "project_1",
  "timeframe": "weekly"
}
```

### Get Scheduled Jobs
```bash
GET /api/v1/scheduler/jobs
Authorization: Bearer <access_token>
```

### Trigger Scheduled Job
```bash
POST /api/v1/scheduler/trigger/<job_name>
Authorization: Bearer <access_token>

# Available jobs: daily_summary, weekly_report, productivity_analysis, notion_sync
```

### Background Task Status
```bash
GET /api/v1/tasks/status/<task_id>
Authorization: Bearer <access_token>
```

## Current Status

The API is now running with:
- ✅ Full authentication system (register, login, JWT tokens)
- ✅ User management with PostgreSQL storage
- ✅ Smart task extraction (rule-based processing)
- ✅ Celery background task processing with Redis
- ✅ APScheduler for automated task scheduling  
- ✅ Webhook support for Slack integration
- ✅ CORS support and comprehensive error handling
- 🔧 Ready for external processing API integration
- 🔧 Ready for Slack/Notion service integration
- 🔧 Vector database support for context memory