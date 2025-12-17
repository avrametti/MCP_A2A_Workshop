# Advanced MCP and Agent to Agent Workshop

**IIoT University | December 16-17, 2025**

A hands-on workshop for engineers, integrators, and digital transformation professionals in industrial automation. Learn to build multi-server MCP architectures and implement the Agent2Agent protocol for collaborative AI systems.

---

## 🎯 Workshop Status

**Day 1:** ✅ **COMPLETE** - All sessions finished, code tested and published  
**Day 2:** 🚧 **UPCOMING** - Starting soon

---

## Workshop Overview

| Day | Topic | Focus | Status |
|-----|-------|-------|--------|
| Day 1 | Advanced MCP | Multi-server architectures connecting AI to industrial data | ✅ Complete |
| Day 2 | Agent2Agent | Collaborative intelligence with coordinating AI agents | 🚧 Coming Soon |

### What We Built on Day 1

- **3 MCP Servers:** MQTT (UNS), MySQL (MES Database), and domain-specific MES server
- **Multi-server architecture** enabling Claude to query both real-time and historical data
- **Domain-specific tooling** for manufacturing operations (OEE, work orders, downtime analysis)
- **React dashboard** with real-time monitoring and AI-powered recommendations
- **Write capabilities** allowing AI agents to log observations back to the UNS

---

## Learning Outcomes

By completing this workshop, participants will be able to:

### Day 1 Outcomes ✅
- ✅ Build MCP servers in Python from scratch
- ✅ Connect AI agents to industrial MQTT brokers (UNS)
- ✅ Integrate AI agents with relational databases (MySQL)
- ✅ Configure multi-server architectures in Claude Desktop
- ✅ Design domain-specific tooling for manufacturing operations
- ✅ Implement read and write capabilities for AI agents
- ✅ Generate industrial dashboards from natural language prompts
- ✅ Integrate Claude API into web applications

### Day 2 Outcomes (Coming Soon)
- 🚧 Design specialized AI agents for different domains
- 🚧 Implement agent-to-agent communication protocols
- 🚧 Orchestrate workflows across multiple agents
- 🚧 Apply the A2A protocol to industrial scenarios
- 🚧 Build collaborative intelligence systems

---

## Quick Start

### 1. Clone the Repository

```bash
git clone https://github.com/iiot-university/MCP_A2A_Workshop.git
cd MCP_A2A_Workshop
```

### 2. Configure Environment

```bash
cp .env.example .env
# Edit .env with your credentials
```

### 3. Follow the Day 1 or Day 2 Guide

Each session has its own README with step-by-step instructions.

**Day 1:** Start with [day1/mqtt_server/README.md](day1/mqtt_server/README.md)  
**Day 2:** Coming soon

---

## Project Structure

```
MCP_A2A_Workshop/
├── .env                    # Credentials (gitignored - create from .env.example)
├── .env.example            # Template with placeholder values
├── README.md               # This file
│
├── day1/                   # Advanced MCP - Multi-Server Architectures
│   ├── mqtt_server/        # Session 2: MQTT MCP Server
│   │   ├── README.md       # Step-by-step guide
│   │   ├── requirements.txt
│   │   └── src/
│   │       └── mqtt_mcp_server.py
│   │
│   ├── mysql_server/       # Session 3: MySQL MCP Server
│   │   ├── README.md       # Step-by-step guide
│   │   ├── requirements.txt
│   │   └── src/
│   │       └── mysql_mcp_server.py
│   │
│   ├── mes_server/         # Session 4: MES Domain Server
│   │   ├── README.md       # Full specification
│   │   ├── CURSOR_PROMPT.md # Build prompt for Cursor
│   │   ├── requirements.txt
│   │   └── src/
│   │       └── mes_mcp_server.py
│   │
│   └── use_cases/          # Session 4: Documentation
│       └── README.md       # Session guide and use cases
│
└── day2/                   # Agent2Agent - Collaborative Intelligence
    └── (Day 2 content - coming soon)
```

---

## Day 1: Advanced MCP - Multi-Server Architectures ✅ COMPLETE

**Status:** All sessions completed and tested. Code pushed to repository.

### Session 1: Introduction & Workshop Overview (9:00 - 9:45) ✅

Instructor-led introduction covering:
- Learning objectives for both days
- Infrastructure overview (cloud and local)
- Virtual Factory data sources
- What is MCP and why manufacturers should care

### Session 2: Building Your First MCP Server — MQTT & UNS (10:00 - 10:45) ✅

**Guide:** [day1/mqtt_server/README.md](day1/mqtt_server/README.md)

**Status:** Complete and tested

Built a Python MCP server that connects to the Flexible Packager Unified Namespace via MQTT. Enables querying and publishing to the UNS using natural language through Claude Desktop.

**Tools Implemented:**
- `list_uns_topics` - Discover available topics
- `get_topic_value` - Read specific topic values  
- `search_topics` - Search topics by pattern
- `publish_message` - Publish messages to topics

**Key Features:**
- File-based MQTT caching for instant responses
- Unique client IDs to prevent collisions
- Automatic reconnection with exponential backoff
- Thread-safe cache operations

### Session 3: Multi-Server Architecture — Adding MySQL (11:00 - 11:45) ✅

**Guide:** [day1/mysql_server/README.md](day1/mysql_server/README.md)

**Status:** Complete and tested

Added a second MCP server for relational database access. Configured Claude Desktop for multiple servers and demonstrated cross-server queries combining real-time and historical data.

**Tools Implemented:**
- `list_schemas` - Discover available databases
- `list_tables` - List tables with row counts
- `describe_table` - Get column definitions
- `execute_query` - Run read-only SELECT queries

**Key Features:**
- Read-only query validation with dangerous keyword blocking
- Schema allowlist for security
- Connection pooling for efficiency
- Row limits and query auditing

### Session 4: Practical Industrial Use Cases (12:00 - 12:45) ✅

**Guide:** [day1/use_cases/README.md](day1/use_cases/README.md)

**Status:** Complete and tested

Built a domain-specific MES MCP server for Press 103 that combines MQTT and MySQL into unified MES-objective tools. Demonstrated the "single-asset agent" pattern with manufacturing-specific operations.

**What We Built:**
- MES MCP Server scoped to Press 103 (single-asset agent pattern)
- Tools: `get_equipment_status`, `get_active_work_order`, `get_oee_summary`, `get_downtime_summary`, `log_observation`
- React dashboard with real-time tab and AI recommendations tab
- Claude API integration in artifacts for analysis

**Key Insights:**
- Domain-specific servers reduce token usage and improve accuracy
- MES-objective tools map directly to manufacturing decisions
- Combining real-time (UNS) and historical (MySQL) data in single tools
- Agent observations can be written back to the UNS for tracking

### Day 1 Achievements

✅ Three fully functional MCP servers (MQTT, MySQL, MES)  
✅ Multi-server architecture with Claude Desktop  
✅ Cross-server queries combining real-time and historical data  
✅ Domain-specific tooling for manufacturing operations  
✅ React dashboard with AI-powered recommendations  
✅ Write capabilities to the UNS for agent observations

---

## Day 2: Agent2Agent - Collaborative Intelligence (Coming Soon)

**Focus:** Building coordinating AI agents that work together using the Agent2Agent protocol.

**Planned Topics:**
- Agent specialization (Production, Quality, Maintenance agents)
- Agent-to-agent communication patterns
- Workflow orchestration across multiple agents
- The A2A protocol for industrial automation
- Collaborative intelligence in manufacturing

**Prerequisites:** Completion of Day 1 (all three MCP servers)

---

## Infrastructure

### Cloud Resources

| Resource | Endpoint | Purpose |
|----------|----------|---------|
| HiveMQ Broker | balancer.virtualfactory.online:1883 | MQTT / Unified Namespace |
| MySQL Database | proveit.virtualfactory.online:3306 | MES and batch data |
| Ignition | ignition.virtualfactory.online:8088 | SCADA (internal use) |

### Virtual Factory Data

Data comes from the Flexible Packager virtual factory built for ProveIt! Conference 2025. The UNS follows ISA-95 hierarchy and publishes to the HiveMQ broker.

### Database Schemas

| Schema | Purpose |
|--------|---------|
| hivemq_ese_db | HiveMQ Enterprise Security -- user accounts and broker permissions |
| mes_custom | Custom extensions and user-defined fields |
| mes_lite | Core MES data -- work orders, production runs, equipment |
| proveitdb | ProveIt! demo data -- batches, quality checks, recipes |

---

## Local Development

### Prerequisites

- Python 3.10+
- Claude Desktop
- Cursor IDE (recommended)
- Git

### Tools We Use

| Tool | Purpose |
|------|---------|
| Claude Desktop | MCP client for natural language interaction |
| Cursor | IDE with AI-assisted coding |
| Python | MCP server implementation |
| paho-mqtt | MQTT client library |
| mysql-connector-python | MySQL client library |

---

## Environment Variables

All credentials are stored in the root `.env` file. This file is gitignored and never committed.

```bash
# MQTT Broker Configuration
MQTT_BROKER=balancer.virtualfactory.online
MQTT_PORT=1883
MQTT_USERNAME=your_username
MQTT_PASSWORD=your_password
# Note: MQTT_CLIENT_ID is auto-generated with a unique suffix (e.g., mcp-mqtt-a1b2c3d4)
# to allow multiple MCP server instances to run simultaneously without conflicts

# MySQL Database Configuration
MYSQL_HOST=proveit.virtualfactory.online
MYSQL_PORT=3306
MYSQL_USERNAME=your_username
MYSQL_PASSWORD=your_password
MYSQL_SCHEMAS=hivemq_ese_db,mes_custom,mes_lite,proveitdb
```

---

## For Cursor / AI Agents

When building code for this workshop:

1. **Read the session README first** -- Each session directory contains a README with specifications for what to build

2. **Use the root .env for credentials** -- Load environment variables from the project root, not from session directories

3. **Follow MCP patterns** -- Servers use stdio transport, expose tools for actions and resources for data

4. **Ground examples in the Virtual Factory** -- Use real topic paths and table names from the infrastructure described above

5. **Keep code simple and readable** -- This is teaching code, prioritize clarity over optimization

---

## GitHub Repository

**Public:** https://github.com/iiot-university/MCP_A2A_Workshop

**Day 1 Status:** ✅ Complete - All code published and tested  
**Day 2 Status:** 🚧 In development

Students can clone the repository to access:
- Complete Day 1 implementation (MQTT, MySQL, MES servers)
- Step-by-step guides and documentation
- Requirements files and configuration templates
- Database schema documentation

---

## Day 1 Summary & Lessons Learned

### Technical Achievements

**Architecture:**
- Successfully implemented multi-server MCP architecture
- Demonstrated separation of concerns (MQTT, MySQL, domain-specific)
- Proved domain-specific servers reduce token usage and improve accuracy

**Implementation:**
- 3 fully functional MCP servers with 12 total tools
- File-based MQTT caching for instant responses
- Connection pooling for database efficiency
- Thread-safe operations throughout
- Comprehensive error handling and logging

**Security:**
- Read-only query validation
- Dangerous keyword blocking
- Schema allowlist enforcement
- Query auditing and logging
- Unique client IDs preventing collisions

### Key Insights

1. **Domain-Specific Beats Generic**
   - MES server with 5 tools outperforms generic MQTT + MySQL with 8 tools
   - Tools map to business objectives, not data structures
   - Reduces token usage and improves response accuracy

2. **Multi-Server Architecture Works**
   - Claude seamlessly routes requests to appropriate servers
   - Cross-server queries combine real-time and historical data
   - Independent scaling and maintenance per server

3. **Caching is Critical**
   - File-based MQTT cache enables instant topic lookups
   - Persists across reconnections for stability
   - Thread-safe operations prevent race conditions

4. **Write Capabilities Enable Feedback**
   - Agents can log observations back to the UNS
   - Creates audit trail of AI decisions
   - Enables agent-to-agent communication (Day 2 preview)

### Production Readiness Checklist

For deploying these servers in production:

- [ ] Add authentication/authorization to MCP servers
- [ ] Implement topic allowlists for MQTT writes
- [ ] Add rate limiting on database queries
- [ ] Set up monitoring and alerting
- [ ] Implement proper secrets management
- [ ] Add comprehensive error recovery
- [ ] Create deployment automation
- [ ] Document operational procedures
- [ ] Set up log aggregation
- [ ] Implement health checks

### Next Steps (Day 2)

Building on Day 1's foundation:
- Specialized agents (Production, Quality, Maintenance)
- Agent-to-agent communication protocols
- Workflow orchestration across agents
- The A2A protocol implementation
- Collaborative intelligence patterns

---

## Resources

### MCP & AI
- [MCP Documentation](https://modelcontextprotocol.io)
- [Anthropic MCP GitHub](https://github.com/anthropics/anthropic-cookbook/tree/main/misc/model_context_protocol)
- [Claude API Documentation](https://docs.anthropic.com)

### Industrial Protocols
- [Paho MQTT Python](https://eclipse.dev/paho/files/paho.mqtt.python/html/)
- [HiveMQ MQTT Essentials](https://www.hivemq.com/mqtt-essentials/)
- [ISA-95 Standard](https://www.isa.org/isa95)

### Development Tools
- [Python MySQL Connector](https://dev.mysql.com/doc/connector-python/en/)
- [React Documentation](https://react.dev)
- [Tailwind CSS](https://tailwindcss.com)

---

## Support & Community

**Workshop Repository:** https://github.com/iiot-university/MCP_A2A_Workshop  
**IIoT University:** [Contact Information]

For questions, issues, or contributions, please open an issue on GitHub.

---

## License

MIT License - See LICENSE file for details.

---

## Acknowledgments

Built for the IIoT University Advanced MCP and Agent2Agent Workshop, December 2025.

Special thanks to:
- The Virtual Factory team for providing the industrial data infrastructure
- Anthropic for the MCP protocol and Claude API
- All workshop participants and contributors

**Day 1 Complete!** ✅ Ready for Day 2.
