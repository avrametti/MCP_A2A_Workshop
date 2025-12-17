# Production Agent Deployment Guide

This guide covers deploying the Production Agent to various environments.

---

## Table of Contents

1. [Local Development](#local-development)
2. [Docker Deployment](#docker-deployment)
3. [Cloud Deployment](#cloud-deployment)
4. [Production Considerations](#production-considerations)
5. [Monitoring & Maintenance](#monitoring--maintenance)

---

## Local Development

### Prerequisites

- Python 3.10 or higher
- pip package manager
- Access to MQTT broker and MySQL database

### Setup Steps

```bash
# 1. Clone or navigate to project
cd day2/production_agent

# 2. Create virtual environment
python -m venv venv

# 3. Activate virtual environment
# Windows:
venv\Scripts\activate
# Linux/Mac:
source venv/bin/activate

# 4. Install dependencies
pip install -r requirements.txt

# 5. Configure environment
cp ../../.env.example ../../.env
# Edit .env with your settings

# 6. Run server
python src/production_agent.py

# 7. Verify
curl http://localhost:8001/health
```

### Development Mode

For auto-reload during development:

```bash
# Install uvicorn[standard]
pip install "uvicorn[standard]"

# Run with auto-reload
uvicorn src.production_agent:app --host 0.0.0.0 --port 8001 --reload
```

---

## Docker Deployment

### Create Dockerfile

Create `Dockerfile` in `day2/production_agent/`:

```dockerfile
FROM python:3.11-slim

# Set working directory
WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    gcc \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements and install Python dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY src/ ./src/

# Create directory for cache
RUN mkdir -p /app/src

# Expose port
EXPOSE 8001

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
    CMD python -c "import requests; requests.get('http://localhost:8001/health')" || exit 1

# Run application
CMD ["python", "src/production_agent.py"]
```

### Create docker-compose.yml

Create `docker-compose.yml`:

```yaml
version: '3.8'

services:
  production-agent:
    build: .
    ports:
      - "8001:8001"
    environment:
      - MQTT_BROKER=${MQTT_BROKER}
      - MQTT_PORT=${MQTT_PORT}
      - MQTT_USERNAME=${MQTT_USERNAME}
      - MQTT_PASSWORD=${MQTT_PASSWORD}
      - MYSQL_HOST=${MYSQL_HOST}
      - MYSQL_PORT=${MYSQL_PORT}
      - MYSQL_USERNAME=${MYSQL_USERNAME}
      - MYSQL_PASSWORD=${MYSQL_PASSWORD}
    volumes:
      - ./src/production_cache.json:/app/src/production_cache.json
    restart: unless-stopped
    networks:
      - agent-network

networks:
  agent-network:
    driver: bridge
```

### Build and Run

```bash
# Build image
docker build -t production-agent:latest .

# Run with docker-compose
docker-compose up -d

# View logs
docker-compose logs -f

# Stop
docker-compose down
```

### Docker Best Practices

1. **Multi-stage build** for smaller images:
```dockerfile
# Stage 1: Builder
FROM python:3.11-slim as builder
WORKDIR /app
COPY requirements.txt .
RUN pip install --user --no-cache-dir -r requirements.txt

# Stage 2: Runtime
FROM python:3.11-slim
WORKDIR /app
COPY --from=builder /root/.local /root/.local
COPY src/ ./src/
ENV PATH=/root/.local/bin:$PATH
CMD ["python", "src/production_agent.py"]
```

2. **Use .dockerignore**:
```
venv/
__pycache__/
*.pyc
.env
.git/
*.md
test_*.py
```

---

## Cloud Deployment

### AWS Deployment (ECS/Fargate)

#### 1. Build and Push to ECR

```bash
# Authenticate to ECR
aws ecr get-login-password --region us-east-1 | docker login --username AWS --password-stdin <account-id>.dkr.ecr.us-east-1.amazonaws.com

# Create repository
aws ecr create-repository --repository-name production-agent

# Build and tag
docker build -t production-agent:latest .
docker tag production-agent:latest <account-id>.dkr.ecr.us-east-1.amazonaws.com/production-agent:latest

# Push
docker push <account-id>.dkr.ecr.us-east-1.amazonaws.com/production-agent:latest
```

#### 2. Create ECS Task Definition

`task-definition.json`:
```json
{
  "family": "production-agent",
  "networkMode": "awsvpc",
  "requiresCompatibilities": ["FARGATE"],
  "cpu": "256",
  "memory": "512",
  "containerDefinitions": [
    {
      "name": "production-agent",
      "image": "<account-id>.dkr.ecr.us-east-1.amazonaws.com/production-agent:latest",
      "portMappings": [
        {
          "containerPort": 8001,
          "protocol": "tcp"
        }
      ],
      "environment": [
        {"name": "MQTT_BROKER", "value": "broker.virtualfactory.online"},
        {"name": "MQTT_PORT", "value": "1883"}
      ],
      "secrets": [
        {
          "name": "MYSQL_PASSWORD",
          "valueFrom": "arn:aws:secretsmanager:region:account-id:secret:mysql-password"
        }
      ],
      "logConfiguration": {
        "logDriver": "awslogs",
        "options": {
          "awslogs-group": "/ecs/production-agent",
          "awslogs-region": "us-east-1",
          "awslogs-stream-prefix": "ecs"
        }
      },
      "healthCheck": {
        "command": ["CMD-SHELL", "curl -f http://localhost:8001/health || exit 1"],
        "interval": 30,
        "timeout": 5,
        "retries": 3,
        "startPeriod": 60
      }
    }
  ]
}
```

#### 3. Create ECS Service

```bash
# Register task definition
aws ecs register-task-definition --cli-input-json file://task-definition.json

# Create service
aws ecs create-service \
  --cluster production-cluster \
  --service-name production-agent-service \
  --task-definition production-agent \
  --desired-count 2 \
  --launch-type FARGATE \
  --network-configuration "awsvpcConfiguration={subnets=[subnet-xxx],securityGroups=[sg-xxx],assignPublicIp=ENABLED}"
```

### Azure Deployment (Container Instances)

```bash
# Create resource group
az group create --name production-agent-rg --location eastus

# Create container
az container create \
  --resource-group production-agent-rg \
  --name production-agent \
  --image <registry>.azurecr.io/production-agent:latest \
  --cpu 1 \
  --memory 1 \
  --ports 8001 \
  --environment-variables \
    MQTT_BROKER=broker.virtualfactory.online \
    MQTT_PORT=1883 \
  --secure-environment-variables \
    MYSQL_PASSWORD=<password> \
  --restart-policy Always
```

### Google Cloud Platform (Cloud Run)

```bash
# Build and push to GCR
gcloud builds submit --tag gcr.io/<project-id>/production-agent

# Deploy to Cloud Run
gcloud run deploy production-agent \
  --image gcr.io/<project-id>/production-agent \
  --platform managed \
  --region us-central1 \
  --allow-unauthenticated \
  --port 8001 \
  --set-env-vars MQTT_BROKER=broker.virtualfactory.online,MQTT_PORT=1883 \
  --set-secrets MYSQL_PASSWORD=mysql-password:latest
```

---

## Production Considerations

### 1. Security Hardening

#### Update production_agent.py

**Fix CORS** (Line 422-428):
```python
ALLOWED_ORIGINS = os.getenv("ALLOWED_ORIGINS", "").split(",")
app.add_middleware(
    CORSMiddleware,
    allow_origins=ALLOWED_ORIGINS,  # Restrict to specific origins
    allow_credentials=True,
    allow_methods=["GET", "POST"],
    allow_headers=["Content-Type", "Authorization"],
)
```

**Add API Key Authentication**:
```python
from fastapi import Security, HTTPException, status
from fastapi.security import APIKeyHeader

API_KEY = os.getenv("API_KEY")
api_key_header = APIKeyHeader(name="X-API-Key")

def verify_api_key(api_key: str = Security(api_key_header)):
    if api_key != API_KEY:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid API key"
        )
    return api_key

# Apply to endpoints
@app.get("/a2a/skills/get_equipment_status", dependencies=[Depends(verify_api_key)])
async def skill_get_equipment_status():
    ...
```

**Fix Deprecated datetime** (Lines 643, 651, 660, 669, 689):
```python
from datetime import datetime, timezone

# Replace all instances of:
datetime.utcnow().isoformat() + "Z"
# With:
datetime.now(timezone.utc).isoformat()
```

### 2. Environment Variables

Production `.env`:
```env
# Server
PORT=8001
LOG_LEVEL=INFO
ALLOWED_ORIGINS=https://app.example.com,https://dashboard.example.com

# Security
API_KEY=<strong-random-key>

# MQTT
MQTT_BROKER=broker.virtualfactory.online
MQTT_PORT=1883
MQTT_USERNAME=production_user
MQTT_PASSWORD=<secure-password>

# MySQL
MYSQL_HOST=proveit.virtualfactory.online
MYSQL_PORT=3306
MYSQL_USERNAME=production_user
MYSQL_PASSWORD=<secure-password>

# Performance
MYSQL_POOL_SIZE=10
CACHE_MAX_AGE=300
```

### 3. Persistent Task Storage

Add Redis for task persistence:

```python
import redis
import json

# Initialize Redis
redis_client = redis.Redis(
    host=os.getenv("REDIS_HOST", "localhost"),
    port=int(os.getenv("REDIS_PORT", 6379)),
    db=0,
    decode_responses=True
)

def store_task(task: Task):
    """Store task in Redis with 24hr expiration."""
    redis_client.setex(
        f"task:{task.task_id}",
        86400,  # 24 hours
        task.json()
    )

def get_task(task_id: str) -> Task | None:
    """Retrieve task from Redis."""
    data = redis_client.get(f"task:{task_id}")
    if data:
        return Task.parse_raw(data)
    return None
```

### 4. Rate Limiting

```bash
pip install slowapi
```

```python
from slowapi import Limiter, _rate_limit_exceeded_handler
from slowapi.util import get_remote_address
from slowapi.errors import RateLimitExceeded

limiter = Limiter(key_func=get_remote_address)
app.state.limiter = limiter
app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)

@app.get("/a2a/skills/get_equipment_status")
@limiter.limit("60/minute")
async def skill_get_equipment_status(request: Request):
    ...
```

### 5. Load Balancing

#### Nginx Configuration

```nginx
upstream production_agent {
    least_conn;
    server agent1:8001;
    server agent2:8001;
    server agent3:8001;
}

server {
    listen 80;
    server_name api.example.com;

    location / {
        proxy_pass http://production_agent;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;

        # Timeouts
        proxy_connect_timeout 60s;
        proxy_send_timeout 60s;
        proxy_read_timeout 60s;
    }

    # Health check endpoint
    location /health {
        access_log off;
        proxy_pass http://production_agent/health;
    }
}
```

---

## Monitoring & Maintenance

### 1. Logging

**Structured JSON Logging**:
```python
import json
import logging
from datetime import datetime

class JSONFormatter(logging.Formatter):
    def format(self, record):
        log_data = {
            "timestamp": datetime.utcnow().isoformat(),
            "level": record.levelname,
            "logger": record.name,
            "message": record.getMessage(),
            "module": record.module,
            "function": record.funcName,
        }
        if record.exc_info:
            log_data["exception"] = self.formatException(record.exc_info)
        return json.dumps(log_data)

handler = logging.StreamHandler(sys.stderr)
handler.setFormatter(JSONFormatter())
logger.addHandler(handler)
```

### 2. Prometheus Metrics

```bash
pip install prometheus-fastapi-instrumentator
```

```python
from prometheus_fastapi_instrumentator import Instrumentator

app = FastAPI(...)

# Add Prometheus instrumentation
Instrumentator().instrument(app).expose(app)

# Custom metrics
from prometheus_client import Counter, Histogram

mqtt_messages = Counter('mqtt_messages_total', 'Total MQTT messages received')
skill_requests = Counter('skill_requests_total', 'Skill requests by type', ['skill_name'])
response_time = Histogram('skill_response_seconds', 'Skill response time', ['skill_name'])
```

### 3. Health Checks

Enhanced health check:
```python
@app.get("/health")
async def health_check():
    health = {
        "status": "ok",
        "agent": "Production Agent",
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "connections": {
            "mqtt": {
                "connected": mqtt_client.connected,
                "messages_cached": len(mqtt_client.get_all_topics())
            },
            "mysql": {
                "connected": check_mysql_connection(),
                "pool_size": db_pool._cnx_queue.qsize() if db_pool else 0
            }
        },
        "cache": {
            "file_exists": CACHE_FILE.exists(),
            "topics_count": len(mqtt_client.get_all_topics())
        }
    }

    # Return 503 if critical services down
    if not health["connections"]["mqtt"]["connected"] and not health["connections"]["mysql"]["connected"]:
        return JSONResponse(status_code=503, content=health)

    return health
```

### 4. Alerting

Set up alerts for:
- MQTT disconnection > 5 minutes
- MySQL connection failures
- High error rate (>5% of requests)
- High response time (>2s p95)
- Memory usage > 80%
- CPU usage > 80%

### 5. Backup & Recovery

**Cache Backup**:
```bash
# Cron job to backup cache hourly
0 * * * * cp /app/src/production_cache.json /backups/cache-$(date +\%Y\%m\%d-\%H\%M).json

# Keep only 24 hours of backups
0 * * * * find /backups -name "cache-*.json" -mtime +1 -delete
```

**Recovery Procedure**:
1. Stop server
2. Restore cache from backup
3. Verify cache integrity: `python -m json.tool production_cache.json`
4. Restart server
5. Monitor logs for errors

---

## Deployment Checklist

### Pre-Deployment
- [ ] Code review completed ([CODE_REVIEW.md](CODE_REVIEW.md))
- [ ] All tests passing
- [ ] Security fixes applied
- [ ] Environment variables configured
- [ ] Secrets stored in secret manager
- [ ] SSL/TLS certificates obtained
- [ ] Monitoring and alerting configured

### Deployment
- [ ] Build Docker image
- [ ] Push to registry
- [ ] Deploy to staging environment
- [ ] Run smoke tests
- [ ] Deploy to production
- [ ] Verify health endpoint
- [ ] Check logs for errors
- [ ] Verify all skills working

### Post-Deployment
- [ ] Monitor metrics for 24 hours
- [ ] Check error logs
- [ ] Verify MQTT/MySQL connections stable
- [ ] Test failover scenarios
- [ ] Document any issues
- [ ] Update runbook

---

## Rollback Procedure

If deployment fails:

```bash
# Docker
docker-compose down
docker-compose up -d --force-recreate --build

# Kubernetes
kubectl rollout undo deployment/production-agent

# AWS ECS
aws ecs update-service \
  --cluster production-cluster \
  --service production-agent-service \
  --task-definition production-agent:<previous-revision>
```

---

## Support

For deployment issues, see:
- [TROUBLESHOOTING.md](TROUBLESHOOTING.md) - Common issues and solutions
- [CODE_REVIEW.md](CODE_REVIEW.md) - Known limitations and improvements
- [README.md](README.md) - General documentation

---

**Last Updated**: 2025-12-17
**Version**: 1.0.0
