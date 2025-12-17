# Production Agent Troubleshooting Guide

This guide helps resolve common issues with the Production Agent.

---

## Server Won't Start

### Issue: "ModuleNotFoundError" when starting

**Symptom**:
```
ModuleNotFoundError: No module named 'fastapi'
```

**Solution**:
```bash
# Activate virtual environment
cd day2/production_agent
venv\Scripts\activate  # Windows
source venv/bin/activate  # Linux/Mac

# Install dependencies
pip install -r requirements.txt
```

### Issue: Port 8001 already in use

**Symptom**:
```
ERROR: [Errno 48] Address already in use
```

**Solution**:
```bash
# Windows - Find and kill process
netstat -ano | findstr :8001
taskkill /PID <PID> /F

# Linux/Mac - Find and kill process
lsof -ti:8001 | xargs kill -9

# Or change port in code
uvicorn.run(app, host="0.0.0.0", port=8002)
```

---

## Connection Issues

### Issue: MQTT Connection Failed

**Symptom in logs**:
```
WARNING - MQTT connection failed. Real-time data may not be available.
```

**Diagnosis**:
```bash
# Test MQTT connectivity
telnet broker.virtualfactory.online 1883
# OR
ping broker.virtualfactory.online
```

**Common Causes**:
1. **Firewall blocking port 1883**
   - Solution: Open port 1883 in firewall
   - Windows: `netsh advfirewall firewall add rule name="MQTT" dir=in action=allow protocol=TCP localport=1883`

2. **Incorrect broker address**
   - Check `.env` file: `MQTT_BROKER=broker.virtualfactory.online`
   - Verify DNS resolution: `nslookup broker.virtualfactory.online`

3. **Network connectivity**
   - Check internet connection
   - Try different network (disable VPN if active)

**Workaround**:
- Server will continue to run using cached data from `production_cache.json`

### Issue: MySQL Connection Failed

**Symptom in logs**:
```
ERROR - Failed to create MySQL connection pool: 2003 (HY000): Can't connect to MySQL server
```

**Diagnosis**:
```bash
# Test MySQL connectivity
telnet proveit.virtualfactory.online 3306
# OR
mysql -h proveit.virtualfactory.online -u mcpworkshop -p
```

**Common Causes**:
1. **Firewall blocking port 3306**
   - Solution: Open port 3306 in firewall

2. **Incorrect credentials**
   - Check `.env` file:
     ```
     MYSQL_HOST=proveit.virtualfactory.online
     MYSQL_PORT=3306
     MYSQL_USERNAME=mcpworkshop
     MYSQL_PASSWORD=mcpworkshoppassword
     ```

3. **Database not accessible**
   - Verify database server is running
   - Check if your IP is whitelisted

**Workaround**:
- Equipment status and OEE still work (use MQTT data)
- Downtime summary will return empty results

---

## Data Issues

### Issue: All values are zero/Unknown

**Symptom**:
```json
{
  "running": false,
  "state": "0",
  "speed": 0.0,
  "setpoint": 0.0,
  "shift": "Unknown"
}
```

**Common Causes**:
1. **MQTT cache is empty**
   - Check if `production_cache.json` exists and has data
   - Wait 10-15 seconds after server start for MQTT to populate

2. **Press 103 is offline**
   - Check if Press 103 is publishing data to UNS
   - Verify topic path: `Enterprise/Dallas/Press/Press 103/#`

3. **Subscribed to wrong topic**
   - Check logs for: `Subscribed to Enterprise/Dallas/Press/Press 103/#`

**Diagnosis**:
```bash
# Check cache file
cat day2/production_agent/src/production_cache.json

# Should contain topics like:
# "Enterprise/Dallas/Press/Press 103/Dashboard/Running": {"value": "true", ...}
```

**Solution**:
1. Restart server to re-subscribe to MQTT
2. Wait 30 seconds for cache to populate
3. Check health endpoint: `curl http://localhost:8001/health`

### Issue: Stale Data

**Symptom**: Data doesn't update in real-time

**Cause**: MQTT not receiving new messages

**Solution**:
1. Check MQTT connection: `curl http://localhost:8001/health`
2. Verify `mqtt_connected: true`
3. If false, restart server
4. Check server logs for MQTT reconnection attempts

---

## API Issues

### Issue: CORS Error in Browser

**Symptom**:
```
Access to fetch at 'http://localhost:8001' from origin 'http://localhost:3000' has been blocked by CORS policy
```

**Solution**:
The agent already has CORS enabled for all origins. If still seeing error:
1. Check browser console for exact error
2. Ensure using correct URL scheme (http:// not https://)
3. Clear browser cache
4. Try different browser

### Issue: 404 Not Found for endpoints

**Symptom**:
```
{"detail": "Not Found"}
```

**Common Causes**:
1. **Wrong URL**: Check spelling
   - Correct: `/a2a/skills/get_equipment_status`
   - Wrong: `/a2a/skill/get_equipment_status` (missing 's')

2. **Server not running**: Check if server is active
   ```bash
   curl http://localhost:8001/health
   ```

### Issue: Task not found (404)

**Symptom**:
```json
{"detail": "Task not found"}
```

**Cause**:
1. Invalid task_id (typo)
2. Server restarted (in-memory storage cleared)
3. Task never created

**Solution**:
1. Verify task_id from POST response
2. Use correct task_id in GET request
3. For persistent storage, see [CODE_REVIEW.md](CODE_REVIEW.md)

---

## Performance Issues

### Issue: Slow Response Times

**Symptom**: Requests take >5 seconds

**Diagnosis**:
```bash
# Time a request
time curl http://localhost:8001/a2a/skills/get_equipment_status
```

**Common Causes**:
1. **MySQL query timeout**
   - Check MySQL connection latency
   - Reduce `hours_back` parameter

2. **MQTT cache lock contention**
   - Multiple rapid requests
   - Cache file corruption

**Solutions**:
1. Restart server
2. Delete and recreate cache file
3. Check system resources (CPU, memory)

### Issue: High Memory Usage

**Symptom**: Python process using excessive RAM

**Causes**:
1. Large cache file
2. Many tasks in memory

**Solutions**:
1. Clear cache file: `del day2\production_agent\src\production_cache.json`
2. Restart server
3. Implement task cleanup (see CODE_REVIEW.md)

---

## Logging & Debugging

### Enable Debug Logging

Edit [src/production_agent.py](src/production_agent.py):
```python
# Line 38-42
logging.basicConfig(
    level=logging.DEBUG,  # Change from INFO to DEBUG
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    stream=sys.stderr,
)
```

### Check Server Logs

**Real-time logs**:
```bash
cd day2/production_agent
python src/production_agent.py 2>&1 | tee server.log
```

**Log file**: `server.log`

**Key log patterns**:
```
✅ INFO - Connected to MQTT broker
✅ INFO - MySQL connection pool created
✅ INFO - Subscribed to Enterprise/Dallas/Press/Press 103/#
⚠️ WARNING - MQTT connection failed
⚠️ WARNING - MySQL connection pool failed
❌ ERROR - Failed to write to cache file
```

### Test Individual Components

**Test MQTT only**:
```python
from src.production_agent import mqtt_client
mqtt_client.connect()
print(mqtt_client.connected)
print(mqtt_client.get_all_topics())
```

**Test MySQL only**:
```python
from src.production_agent import init_db_pool, execute_query
init_db_pool()
results = execute_query("SELECT 1")
print(results)
```

---

## Environment Issues

### Issue: .env file not found

**Symptom**:
```
INFO - Loading environment from: C:\...\MCP_A2A_Workshop\.env
```
But variables use defaults (localhost)

**Solution**:
```bash
# Check if .env exists in project root
ls .env

# If not, create from example
cp .env.example .env

# Verify contents
cat .env
```

### Issue: Wrong environment variables

**Diagnosis**:
```python
# Add to production_agent.py temporarily
print(f"MQTT_BROKER: {MQTT_BROKER}")
print(f"MYSQL_HOST: {MYSQL_HOST}")
```

**Solution**:
1. Check `.env` file location (must be in project root)
2. No quotes around values in .env
3. No spaces around `=`
4. Restart server after editing .env

---

## Common Error Messages

### "Connection pool not initialized"

**Cause**: MySQL pool creation failed

**Solution**: Check MySQL connection settings in .env

### "Not connected to MQTT broker"

**Cause**: Attempting to publish without connection

**Solution**: Check MQTT connection in health endpoint

### "Cache file corrupted"

**Cause**: Invalid JSON in cache file

**Solution**:
```bash
# Backup and delete
mv production_cache.json production_cache.json.bak
# Server will create new one on next start
```

---

## Getting Help

If issues persist after trying solutions above:

1. **Check logs**: Look for specific error messages
2. **Verify environment**: `.env` file has correct values
3. **Test connectivity**: MQTT and MySQL accessible
4. **Review code**: [CODE_REVIEW.md](CODE_REVIEW.md) for known issues
5. **Check version**: Python 3.10+ required

### Useful Commands

```bash
# Check Python version
python --version

# Check installed packages
pip list

# Verify server is running
curl http://localhost:8001/health

# Check all environment variables
python -c "from dotenv import load_dotenv; load_dotenv('.env'); import os; print(os.environ)"

# Test MQTT subscription
mosquitto_sub -h broker.virtualfactory.online -t "Enterprise/Dallas/Press/Press 103/#" -v
```

---

## Emergency Reset

If all else fails, complete reset:

```bash
# Stop server
taskkill /F /IM python.exe  # Windows
pkill -9 python  # Linux/Mac

# Delete virtual environment
rmdir /s venv  # Windows
rm -rf venv  # Linux/Mac

# Delete cache
del day2\production_agent\src\production_cache.json  # Windows
rm day2/production_agent/src/production_cache.json  # Linux/Mac

# Recreate from scratch
python -m venv venv
venv\Scripts\activate
pip install -r requirements.txt
python src/production_agent.py
```

---

**Last Updated**: 2025-12-17
**For**: Production Agent v1.0.0
