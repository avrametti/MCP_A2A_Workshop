# Claude Code Implementation Prompt: Production Agent

I need you to implement a Production Agent - an A2A (Agent-to-Agent) compliant FastAPI server for Press 103 manufacturing data.

## PROJECT CONTEXT

**Location:** `C:\Users\Ionut\Workspace\Codebase\MCP_A2A_Workshop\day2\production_agent`  
**Reference implementation:** `C:\Users\Ionut\Workspace\Codebase\MCP_A2A_Workshop\day1\mes_server\src\mes_mcp_server.py`

## REQUIRED FILES TO CREATE

### 1. requirements.txt
```
fastapi>=0.104.0
uvicorn>=0.24.0
paho-mqtt>=2.0.0
mysql-connector-python>=8.0.0
python-dotenv>=1.0.0
```

### 2. src/production_agent.py
Main FastAPI application

---

## TECHNICAL SPECIFICATIONS

### Environment Configuration
- Load .env from: `Path(__file__).parent.parent.parent.parent / ".env"`
- **MQTT**: `MQTT_BROKER`, `MQTT_PORT` (1883), `MQTT_USERNAME`, `MQTT_PASSWORD`
- **MySQL**: `MYSQL_HOST`, `MYSQL_PORT` (3306), `MYSQL_USERNAME`, `MYSQL_PASSWORD`, `MYSQL_DATABASE="mes_lite"`

### Press 103 Constants
```python
PRESS_103_LINE_ID = 1
PRESS_103_UNS_BASE = "Enterprise/Dallas/Press/Press 103"
```

### UNS Topics to Subscribe
Subscribe to `{PRESS_103_UNS_BASE}/#` wildcard. Topics include:
- `Dashboard/Running`
- `Line/State`
- `MQTT/Dashboard Machine Speed`
- `Line/Rate Setpoint`
- `Dashboard/Shift Name`
- `Line/OEE/OEE`
- `Line/OEE/OEE Availability`
- `Line/OEE/OEE Performance`
- `Line/OEE/OEE Quality`
- `Line/OEE/Good Count`
- `Line/OEE/Bad Count`
- `Line/OEE/Target Count`
- `Line/OEE/WorkOrder`
- `Line/OEE/Runtime`
- `Line/OEE/Unplanned Downtime`

---

## MQTT CLIENT REQUIREMENTS

- Use **paho-mqtt 2.0+** with `CallbackAPIVersion.VERSION2`
- Subscribe to `"{PRESS_103_UNS_BASE}/#"` on connect
- Cache messages to `"production_cache.json"` with thread-safe atomic writes
- Unique client ID with UUID suffix
- **Pattern**: Copy from `day1/mes_server/src/mes_mcp_server.py` MQTTClient class

---

## MYSQL REQUIREMENTS

- Connection pool with **3 connections** (`mysql.connector.pooling`)
- Read-only **SELECT queries** only
- Pool name: `"production_agent_pool"`
- **Pattern**: Copy from `day1/mes_server/src/mes_mcp_server.py` MySQLPool class

---

## ENDPOINTS TO IMPLEMENT

### 1. `GET /.well-known/agent.json`
Returns Agent Card with:
```json
{
  "name": "Production Agent",
  "description": "Monitors Press 103 equipment status, OEE, and production metrics for the Flexible Packaging line",
  "url": "http://localhost:8001",
  "version": "1.0.0",
  "provider": {
    "organization": "IIoT University"
  },
  "capabilities": {
    "streaming": false,
    "pushNotifications": false
  },
  "skills": [
    {
      "id": "get_equipment_status",
      "name": "Get Equipment Status",
      "description": "Returns current running state, speed, setpoint, and shift for Press 103",
      "inputModes": ["text/plain"],
      "outputModes": ["application/json"]
    },
    {
      "id": "get_oee_summary",
      "name": "Get OEE Summary",
      "description": "Returns OEE breakdown (Availability, Performance, Quality) and production counts",
      "inputModes": ["text/plain"],
      "outputModes": ["application/json"]
    },
    {
      "id": "get_downtime_summary",
      "name": "Get Downtime Summary",
      "description": "Returns downtime analysis with top reasons from the last 24 hours",
      "inputModes": ["text/plain"],
      "outputModes": ["application/json"]
    }
  ]
}
```

### 2. `POST /a2a/message/send`
- Accepts message with `role` and `parts[{type, text}]`
- **Routes to skill based on keywords**:
  - `"status|running|state|speed|shift"` → `get_equipment_status`
  - `"oee|performance|availability|quality|count"` → `get_oee_summary`
  - `"downtime|down|stopped|reason|why"` → `get_downtime_summary`
  - **default** → `get_equipment_status`
- Returns task with `task_id` (UUID), `state="completed"`, `artifacts` array

**Request Body:**
```json
{
  "message": {
    "role": "user",
    "parts": [
      {
        "type": "text",
        "text": "What is the OEE for Press 103?"
      }
    ]
  }
}
```

**Response:**
```json
{
  "task_id": "550e8400-e29b-41d4-a716-446655440000",
  "state": "completed",
  "artifacts": [
    {
      "type": "application/json",
      "data": { ... }
    }
  ]
}
```

### 3. `GET /a2a/tasks/{task_id}`
- Retrieve task by ID from in-memory dict
- Return **404** if not found

### 4. `GET /a2a/skills/get_equipment_status`
Returns:
```json
{
  "skill": "get_equipment_status",
  "timestamp": "2025-12-17T13:45:00Z",
  "data": {
    "running": false,
    "state": "0",
    "speed": 0.0,
    "setpoint": 25500.0,
    "speed_percent": 0.0,
    "shift": "Day",
    "mqtt_connected": true
  }
}
```

### 5. `GET /a2a/skills/get_oee_summary`
Returns:
```json
{
  "skill": "get_oee_summary",
  "timestamp": "2025-12-17T13:45:00Z",
  "data": {
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
}
```

### 6. `GET /a2a/skills/get_downtime_summary?hours_back=24`
Query MySQL `statehistory` table for `Line_ID=1`:
```sql
SELECT state, state_name, COUNT(*) as occurrences, SUM(duration_minutes) as total_minutes
WHERE timestamp >= NOW() - INTERVAL {hours_back} HOUR
GROUP BY state, state_name 
ORDER BY total_minutes DESC
```

Returns:
```json
{
  "skill": "get_downtime_summary",
  "timestamp": "2025-12-17T13:45:00Z",
  "data": {
    "current_state": "0",
    "is_running": false,
    "hours_analyzed": 24,
    "total_downtime_minutes": 0.0,
    "planned_minutes": 0.0,
    "unplanned_minutes": 0.0,
    "top_reasons": []
  }
}
```

### 7. `GET /health`
Returns:
```json
{
  "status": "ok",
  "agent": "Production Agent",
  "mqtt_connected": true,
  "mysql_connected": true,
  "timestamp": "2025-12-17T13:45:00Z"
}
```

---

## PYDANTIC MODELS NEEDED

### For A2A Message Protocol
- `MessagePart` - type, text
- `Message` - role, parts
- `MessageRequest` - message
- `Artifact` - type, data
- `Task` - task_id, state, artifacts

### For Agent Discovery
- `AgentCard` - name, description, url, version, provider, capabilities, skills
- `Skill` - id, name, description, inputModes, outputModes
- `Provider` - organization
- `Capabilities` - streaming, pushNotifications

---

## FASTAPI CONFIGURATION

- **Port**: 8001
- **CORS**: Allow all origins (add_middleware CORSMiddleware with `allow_origins=["*"]`)
- **Startup event**: Initialize MQTT and MySQL
- **Shutdown event**: Cleanup connections
- **Logging**: INFO level to stderr

---

## KEY IMPLEMENTATION DETAILS

### Task Storage
- In-memory `dict[str, Task]`

### OEE Rating Logic
```python
if oee > 0.85: "World Class"
elif oee > 0.60: "Acceptable"
else: "Needs Improvement"
```

### Speed Calculation
```python
speed_percent = (speed / setpoint) * 100 if setpoint > 0 else 0
```

### Cache Access Pattern
```python
cache.get(topic, default_value)
```

### Skill Response Format
All skill responses wrapped in:
```json
{
  "skill": "skill_name",
  "timestamp": "ISO8601",
  "data": { ... }
}
```

---

## MYSQL DOWNTIME QUERY DETAILS

- Use `statehistory` table
- Filter by `Line_ID = 1` and time range
- Calculate **planned vs unplanned** based on state codes (you'll need to determine logic from data)
- Return top reasons sorted by duration descending

---

## RUN COMMAND

```bash
python src/production_agent.py
```

### Main Block
```python
if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8001)
```

---

## IMPLEMENTATION NOTES

1. **Refer to** `day1/mes_server/src/mes_mcp_server.py` for MQTT and MySQL patterns
2. **Adapt for FastAPI** instead of MCP
3. **All endpoints** must return proper JSON
4. **Handle errors gracefully** with appropriate HTTP status codes
5. **Thread-safe operations** for cache writes
6. **Atomic file writes** using temp file + rename pattern

---

## SUCCESS CRITERIA

- [ ] Server starts without errors on port 8001
- [ ] MQTT connects to broker and caches data
- [ ] MySQL connection pool established
- [ ] Agent Card accessible at `/.well-known/agent.json`
- [ ] All three skill endpoints return valid JSON
- [ ] A2A message/send routes correctly based on keywords
- [ ] Health endpoint shows connection status
- [ ] CORS enabled for browser access
