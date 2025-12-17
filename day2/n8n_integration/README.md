# N8N Integration — MES HTTP Server

**Purpose:** Integrate N8N workflow orchestration with MES data from the Virtual Factory.

**Status:** ✅ WORKING (December 17, 2025)

**Workshop Use:** Day 2, Session 3 — Multi-Agent Workflows with N8N

---

## What This Demonstrates

1. **Python FastAPI server** exposes MES data via REST endpoints
2. **N8N running in Docker** reaches the server using `host.docker.internal`
3. **MQTT + MySQL connections** work from the HTTP server to Virtual Factory
4. **Read and Write operations** both succeed (GET endpoints + POST observation)
5. **Multi-step workflows** gather data, process it, and write back to UNS

---

## Architecture

```
┌─────────────────────────────────────────────────────────────────┐
│  Docker                                                         │
│  ┌─────────────┐                                                │
│  │    N8N      │                                                │
│  │  :5678      │                                                │
│  └──────┬──────┘                                                │
│         │ HTTP Request                                          │
│         │ http://host.docker.internal:8001                      │
└─────────┼───────────────────────────────────────────────────────┘
          │
          ▼
┌─────────────────────────────────────────────────────────────────┐
│  Mac (localhost)                                                │
│  ┌─────────────────────────────┐                                │
│  │   MES HTTP Server           │                                │
│  │   FastAPI on :8001          │                                │
│  │                             │                                │
│  │   /health                   │                                │
│  │   /equipment/status         │                                │
│  │   /workorder/active         │                                │
│  │   /oee/summary              │                                │
│  │   /downtime/summary         │                                │
│  │   /observation (POST)       │                                │
│  └──────────┬──────────────────┘                                │
│             │                                                   │
└─────────────┼───────────────────────────────────────────────────┘
              │
              ▼
┌─────────────────────────────────────────────────────────────────┐
│  Virtual Factory (Cloud)                                        │
│                                                                 │
│  ┌─────────────────────┐    ┌─────────────────────┐             │
│  │ MQTT Broker         │    │ MySQL Database      │             │
│  │ balancer.virtual    │    │ proveit.virtual     │             │
│  │ factory.online:1883 │    │ factory.online:3306 │             │
│  │                     │    │                     │             │
│  │ Press 103 UNS Data  │    │ mes_lite schema     │             │
│  └─────────────────────┘    └─────────────────────┘             │
└─────────────────────────────────────────────────────────────────┘
```

---

## Files

| File | Description |
|------|-------------|
| `mes_http_server.py` | FastAPI server exposing MES endpoints |
| `requirements.txt` | Python dependencies |
| `mes_cache.json` | MQTT message cache (auto-generated) |
| `n8n_shift_status_workflow.json` | N8N workflow for Session 3 exercise |
| `README.md` | This file |

---

## Setup

### 1. Create Virtual Environment

```bash
cd /Users/walkerreynolds/PycharmProjects/mcp_a2a/MCP_A2A_Workshop/day2/n8n_integration
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

### 2. Run the Server

```bash
python mes_http_server.py
```

Server starts on **http://localhost:8001**

### 3. Verify with curl

```bash
# Health check
curl http://localhost:8001/health

# Equipment status
curl http://localhost:8001/equipment/status

# OEE summary
curl http://localhost:8001/oee/summary

# Log an observation
curl -X POST http://localhost:8001/observation \
  -H "Content-Type: application/json" \
  -d '{"message": "Test from curl", "category": "test"}'
```

---

## API Endpoints

### GET /health
Health check with connection status.

**Response:**
```json
{
  "status": "ok",
  "mqtt_connected": true,
  "mysql_connected": true,
  "timestamp": "2025-12-17T13:13:10.926976Z"
}
```

### GET /equipment/status
Current operational status of Press 103.

**Response:**
```json
{
  "running": false,
  "state": "0",
  "speed": 0.0,
  "setpoint": 25500.0,
  "speed_percent": 0.0,
  "shift": "Day",
  "mqtt_connected": true
}
```

### GET /workorder/active
Active work order information.

**Response:**
```json
{
  "work_order": "12237611",
  "product_code": "342765",
  "good_count": 8576,
  "target_count": 9804,
  "remaining": 1228,
  "percent_complete": 87.5,
  "run_id": "57465"
}
```

### GET /oee/summary
OEE metrics breakdown.

**Response:**
```json
{
  "oee": 0.0,
  "availability": 0.1,
  "performance": 0.0,
  "quality": 1.0,
  "good_count": 8576,
  "bad_count": 0,
  "total_count": 8576,
  "runtime_minutes": 1024.0,
  "downtime_minutes": 6450.0,
  "rating": "Needs Improvement"
}
```

### GET /downtime/summary
Downtime analysis with Pareto.

**Query Parameters:**
- `hours_back` (int, default=24): Hours to analyze

**Response:**
```json
{
  "current_state": "0",
  "is_running": false,
  "hours_analyzed": 24,
  "total_downtime_minutes": 0.0,
  "planned_minutes": 0.0,
  "unplanned_minutes": 0.0,
  "top_reasons": []
}
```

### POST /observation
Log an observation to the UNS.

**Request Body:**
```json
{
  "message": "Test observation",
  "category": "test"
}
```

**Response:**
```json
{
  "success": true,
  "topic": "Enterprise/Dallas/Press/Press 103/Agent/Observations",
  "message": "Test observation",
  "category": "test",
  "timestamp": "2025-12-17T13:13:11.169214Z"
}
```

---

## N8N Integration

### Connecting from N8N (Docker) to Local Server

Since N8N runs in Docker, use `host.docker.internal` to reach localhost:

| From N8N | URL |
|----------|-----|
| Health | `http://host.docker.internal:8001/health` |
| Equipment | `http://host.docker.internal:8001/equipment/status` |
| Work Order | `http://host.docker.internal:8001/workorder/active` |
| OEE | `http://host.docker.internal:8001/oee/summary` |
| Downtime | `http://host.docker.internal:8001/downtime/summary` |
| Observation | `http://host.docker.internal:8001/observation` (POST) |

---

## Session 3 Exercise: Shift Status Check Workflow

### Overview

This workflow demonstrates orchestrated multi-step agent coordination:

1. **Gather** data from multiple endpoints
2. **Process** the data using JavaScript
3. **Write** a summary observation back to the UNS

### Workflow Diagram

```
┌──────────────┐    ┌──────────────┐    ┌──────────────┐    ┌──────────────┐    ┌──────────────┐    ┌──────────────┐
│   Manual     │───▶│     Get      │───▶│    Get       │───▶│    Get       │───▶│    Build     │───▶│    Post      │
│   Trigger    │    │   Equipment  │    │    OEE       │    │  Work Order  │    │ Observation  │    │ Observation  │
│              │    │    Status    │    │              │    │              │    │   Message    │    │              │
└──────────────┘    └──────────────┘    └──────────────┘    └──────────────┘    └──────────────┘    └──────────────┘
```

### Import the Workflow

1. Open **http://localhost:5678**
2. Click the **⋮** menu (top right) → **Import from File**
3. Select `n8n_shift_status_workflow.json`
4. Click **Test Workflow**

### What Each Node Does

| Node | Type | Purpose |
|------|------|---------|
| Manual Trigger | Trigger | Starts workflow on demand |
| Get Equipment Status | HTTP Request | GET /equipment/status |
| Get OEE | HTTP Request | GET /oee/summary |
| Get Work Order | HTTP Request | GET /workorder/active |
| Build Observation | Code | JavaScript combines data into message |
| Post Observation | HTTP Request | POST /observation to UNS |

### Build Observation Code

```javascript
// Get data from previous nodes
const status = $('Get Equipment Status').first().json;
const oee = $('Get OEE').first().json;
const workOrder = $('Get Work Order').first().json;

// Build status text
const runningText = status.running ? 'RUNNING' : 'STOPPED';
const stateText = status.state || 'Unknown';

// Format OEE values
const oeeVal = (oee.oee * 100).toFixed(1);
const availVal = (oee.availability * 100).toFixed(1);
const perfVal = (oee.performance * 100).toFixed(1);
const qualVal = (oee.quality * 100).toFixed(1);

// Build observation message
const message = `Shift Status Check: Press 103 is ${runningText} (state: ${stateText}). ` +
  `OEE: ${oeeVal}% (A: ${availVal}%, P: ${perfVal}%, Q: ${qualVal}%). ` +
  `Work Order ${workOrder.work_order || 'N/A'}: ${workOrder.percent_complete}% complete ` +
  `(${workOrder.good_count} good, ${workOrder.remaining} remaining).`;

return [{
  json: {
    message: message,
    category: 'shift-check'
  }
}];
```

### Example Output

**Observation posted to UNS topic:**
`Enterprise/Dallas/Press/Press 103/Agent/Observations`

**Message:**
> Shift Status Check: Press 103 is STOPPED (state: 0). OEE: 0.0% (A: 10.0%, P: 0.0%, Q: 100.0%). Work Order 12237611: 87.5% complete (8576 good, 1228 remaining).

### Test Results (December 17, 2025)

✅ Workflow executed successfully
✅ All HTTP requests returned data
✅ JavaScript code processed data correctly  
✅ Observation posted to UNS

---

## Key Learnings

1. **Docker networking:** Use `host.docker.internal` from Docker containers to reach Mac localhost

2. **Environment path:** Server loads `.env` from project root:
   ```python
   env_path = Path(__file__).parent.parent.parent / ".env"
   ```

3. **CORS required:** N8N needs CORS enabled on the server:
   ```python
   app.add_middleware(CORSMiddleware, allow_origins=["*"], ...)
   ```

4. **Pydantic models:** Define response schemas for clean API documentation

5. **Same data sources:** HTTP server connects to same MQTT/MySQL as MCP server

6. **N8N Code node:** Use `$('Node Name').first().json` to access previous node outputs

7. **Multi-step workflows:** Chain HTTP requests → process → write back

---

## Extending the Workflow

Ideas for more complex workflows:

- **Add IF node:** Branch based on OEE threshold (e.g., OEE < 50% → alert path)
- **Scheduled trigger:** Run every hour instead of manual
- **Parallel requests:** Fetch all endpoints simultaneously  
- **Error handling:** Add error output paths for failed requests
- **Slack/Email:** Send alerts when conditions met
