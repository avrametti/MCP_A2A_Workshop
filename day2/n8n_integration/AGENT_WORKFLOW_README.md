# n8n Agent Analysis Workflow

## Overview

This enhanced workflow integrates with the **Production Agent (A2A)** to provide intelligent, agent-powered analysis of Press 103 data and publishes structured observations to the UNS (Unified Namespace).

## Workflow Flow

```
┌─────────────────────────────────────────────────────────────────────┐
│                                                                     │
│  Every 15 Minutes                                                   │
│         ↓                                                           │
│  Get Equipment Status (A2A)                                         │
│         ↓                                                           │
│  Get OEE Summary (A2A)                                              │
│         ↓                                                           │
│  Get Downtime Summary (A2A)                                         │
│         ↓                                                           │
│  Prepare Agent Context                                              │
│         ↓                                                           │
│  Send to Production Agent (A2A /a2a/message/send)                   │
│         ↓                                                           │
│  Format for UNS (Structured JSON)                                   │
│         ↓                                                           │
│  Publish to MQTT                                                    │
│   Topic: Enterprise/Dallas/Press/Press 103/Agent/Observations       │
│         ↓                                                           │
│  Log Result                                                         │
│                                                                     │
└─────────────────────────────────────────────────────────────────────┘
```

## Key Features

### 1. **Automated Scheduling**
- Runs every 15 minutes automatically
- Adjustable cron expression: `*/15 * * * *`

### 2. **A2A Integration**
- Fetches data from Production Agent's three skills
- Sends analysis request via A2A protocol
- Receives intelligent insights from the agent

### 3. **Agent-Powered Analysis**
The workflow sends this prompt to the agent:
```
Analyze the current production status of Press 103 and provide insights:

Equipment Status: Running/Stopped, Speed: X% of setpoint, Shift: Day
OEE: X% (Rating) - A: X%, P: X%, Q: X%
Production: X good, X bad
Downtime: X minutes total (Planned: X, Unplanned: X)
Top Issues: Issue1, Issue2, Issue3

Provide a concise shift status observation highlighting key concerns and recommendations.
```

### 4. **Structured UNS Publishing**
Publishes JSON to MQTT with this structure:
```json
{
  "timestamp": "2025-12-17T14:30:00Z",
  "source": "n8n-agent-workflow",
  "press": "Press 103",
  "shift": "Day",
  "status": {
    "running": true,
    "state": "5",
    "speed_percent": 98.5
  },
  "oee": {
    "overall": 0.82,
    "rating": "Acceptable",
    "availability": 0.85,
    "performance": 0.96,
    "quality": 1.0
  },
  "production": {
    "good_count": 8576,
    "bad_count": 12
  },
  "downtime": {
    "total_minutes": 45.0,
    "unplanned_minutes": 12.0,
    "top_reasons": [
      {"state_name": "Jam", "total_minutes": 8.5},
      {"state_name": "Changeover", "total_minutes": 6.2}
    ]
  },
  "agent_analysis": "Agent's intelligent analysis here...",
  "task_id": "550e8400-e29b-41d4-a716-446655440000"
}
```

## Configuration

### Environment Variables

The workflow uses these environment variables (set in n8n or .env):

```env
MQTT_BROKER=balancer.virtualfactory.online
MQTT_PORT=1883
MQTT_USERNAME=your_username
MQTT_PASSWORD=your_password
```

### Prerequisites

1. **Production Agent** running on `http://localhost:8001`
2. **MQTT Broker** accessible (balancer.virtualfactory.online)
3. **n8n** with MQTT node installed

## Import Instructions

1. Open n8n
2. Click **Import from File**
3. Select `n8n_agent_analysis_workflow.json`
4. Configure environment variables
5. Activate the workflow

## Testing

### Manual Test
1. Click "Execute Workflow" button in n8n
2. Watch each node execute in sequence
3. Check the final "Log Result" node for success

### Verify MQTT Publication
Subscribe to the MQTT topic to see observations:
```bash
mosquitto_sub -h balancer.virtualfactory.online -p 1883 \
  -u your_username -P your_password \
  -t "Enterprise/Dallas/Press/Press 103/Agent/Observations" -v
```

### Check UNS Topics
Use the MQTT UNS MCP server to list recent observations:
```python
# In Claude Desktop with MQTT UNS MCP
search_topics("Agent/Observations")
get_topic_value("Enterprise/Dallas/Press/Press 103/Agent/Observations")
```

## Customization

### Adjust Schedule
Change the cron expression in "Every 15 Minutes" node:
- Every 5 minutes: `*/5 * * * *`
- Hourly: `0 * * * *`
- Every shift change: `0 6,14,22 * * *`

### Modify Agent Prompt
Edit the prompt in "Prepare Agent Context" node to ask different questions:
- Focus on quality issues
- Predict maintenance needs
- Compare to historical performance
- Generate shift handover reports

### Change MQTT Topic
Edit the topic in "Format for UNS" node:
```javascript
topic: 'Enterprise/Dallas/Press/Press 103/Agent/ShiftReports'
// or
topic: 'Enterprise/Dallas/Press/Press 103/Agent/QualityAlerts'
```

## Differences from Original Workflow

| Feature | Original | Enhanced |
|---------|----------|----------|
| Trigger | Manual | Scheduled (15 min) |
| Data Source | HTTP endpoints | A2A Production Agent |
| Analysis | Hardcoded JS template | AI Agent powered |
| Output | HTTP POST | MQTT UNS Publishing |
| Format | Simple text message | Structured JSON |
| Intelligence | Template-based | Context-aware insights |

## Benefits

1. **Intelligent Analysis**: Agent provides context-aware insights, not just data formatting
2. **UNS Integration**: Data flows into the unified namespace for broader system access
3. **Automation**: Runs continuously without manual intervention
4. **Structured Data**: JSON format enables downstream processing and analytics
5. **Traceability**: Task IDs and timestamps for audit trails
6. **Scalability**: Easy to extend with more agents or data sources

## Troubleshooting

### Agent not responding
- Verify Production Agent is running: `curl http://localhost:8001/health`
- Check A2A endpoints are accessible

### MQTT connection fails
- Verify credentials in environment variables
- Test MQTT connection: `mosquitto_pub -h ... -t test -m "test"`
- Check firewall rules for port 1883

### No data in UNS
- Check "Publish to UNS" node execution
- Verify MQTT topic subscription
- Look for errors in "Log Result" node

## Next Steps

1. **Add Alerting**: Trigger alerts based on agent analysis
2. **Create Dashboards**: Visualize observations from UNS
3. **Multi-Press**: Replicate for other production lines
4. **Historical Analysis**: Store observations in time-series database
5. **Predictive Maintenance**: Use agent to predict failures

---

**Created**: December 2025  
**Workshop**: Day 2 - Agent-to-Agent Integration  
**Version**: 1.0
