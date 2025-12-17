#!/usr/bin/env python3
"""
Test script for Production Agent endpoints.
Run this while the server is running to verify all endpoints.
"""

import requests
import json
import time

BASE_URL = "http://localhost:8001"

def test_agent_card():
    """Test /.well-known/agent.json endpoint."""
    print("\n" + "="*60)
    print("Testing Agent Card Endpoint")
    print("="*60)
    response = requests.get(f"{BASE_URL}/.well-known/agent.json")
    print(f"Status Code: {response.status_code}")
    if response.status_code == 200:
        data = response.json()
        print(f"Agent Name: {data.get('name')}")
        print(f"Version: {data.get('version')}")
        print(f"Skills: {len(data.get('skills', []))}")
        print("✓ Agent Card OK")
    else:
        print("✗ Agent Card FAILED")
    return response.status_code == 200

def test_health():
    """Test /health endpoint."""
    print("\n" + "="*60)
    print("Testing Health Endpoint")
    print("="*60)
    response = requests.get(f"{BASE_URL}/health")
    print(f"Status Code: {response.status_code}")
    if response.status_code == 200:
        data = response.json()
        print(f"Status: {data.get('status')}")
        print(f"MQTT Connected: {data.get('mqtt_connected')}")
        print(f"MySQL Connected: {data.get('mysql_connected')}")
        print("✓ Health Check OK")
    else:
        print("✗ Health Check FAILED")
    return response.status_code == 200

def test_equipment_status():
    """Test /a2a/skills/get_equipment_status endpoint."""
    print("\n" + "="*60)
    print("Testing Equipment Status Skill")
    print("="*60)
    response = requests.get(f"{BASE_URL}/a2a/skills/get_equipment_status")
    print(f"Status Code: {response.status_code}")
    if response.status_code == 200:
        data = response.json()
        print(f"Skill: {data.get('skill')}")
        print(f"Running: {data.get('data', {}).get('running')}")
        print(f"State: {data.get('data', {}).get('state')}")
        print(f"Speed: {data.get('data', {}).get('speed')}")
        print("✓ Equipment Status OK")
    else:
        print("✗ Equipment Status FAILED")
    return response.status_code == 200

def test_oee_summary():
    """Test /a2a/skills/get_oee_summary endpoint."""
    print("\n" + "="*60)
    print("Testing OEE Summary Skill")
    print("="*60)
    response = requests.get(f"{BASE_URL}/a2a/skills/get_oee_summary")
    print(f"Status Code: {response.status_code}")
    if response.status_code == 200:
        data = response.json()
        print(f"Skill: {data.get('skill')}")
        print(f"OEE: {data.get('data', {}).get('oee')}%")
        print(f"Availability: {data.get('data', {}).get('availability')}%")
        print(f"Performance: {data.get('data', {}).get('performance')}%")
        print(f"Quality: {data.get('data', {}).get('quality')}%")
        print(f"Rating: {data.get('data', {}).get('rating')}")
        print("✓ OEE Summary OK")
    else:
        print("✗ OEE Summary FAILED")
    return response.status_code == 200

def test_downtime_summary():
    """Test /a2a/skills/get_downtime_summary endpoint."""
    print("\n" + "="*60)
    print("Testing Downtime Summary Skill")
    print("="*60)
    response = requests.get(f"{BASE_URL}/a2a/skills/get_downtime_summary?hours_back=24")
    print(f"Status Code: {response.status_code}")
    if response.status_code == 200:
        data = response.json()
        print(f"Skill: {data.get('skill')}")
        print(f"Current State: {data.get('data', {}).get('current_state')}")
        print(f"Is Running: {data.get('data', {}).get('is_running')}")
        print(f"Total Downtime: {data.get('data', {}).get('total_downtime_minutes')} min")
        print(f"Top Reasons: {len(data.get('data', {}).get('top_reasons', []))}")
        print("✓ Downtime Summary OK")
    else:
        print("✗ Downtime Summary FAILED")
    return response.status_code == 200

def test_a2a_message_send():
    """Test /a2a/message/send endpoint."""
    print("\n" + "="*60)
    print("Testing A2A Message Send Endpoint")
    print("="*60)

    # Test with OEE keyword
    message = {
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

    response = requests.post(f"{BASE_URL}/a2a/message/send", json=message)
    print(f"Status Code: {response.status_code}")
    if response.status_code == 200:
        data = response.json()
        print(f"Task ID: {data.get('task_id')}")
        print(f"State: {data.get('state')}")
        print(f"Artifacts: {len(data.get('artifacts', []))}")
        if data.get('artifacts'):
            artifact = data['artifacts'][0]
            print(f"Skill Executed: {artifact.get('data', {}).get('skill')}")
        print("✓ A2A Message Send OK")
        return response.status_code == 200, data.get('task_id')
    else:
        print("✗ A2A Message Send FAILED")
        return False, None

def test_get_task(task_id):
    """Test /a2a/tasks/{task_id} endpoint."""
    print("\n" + "="*60)
    print("Testing Get Task Endpoint")
    print("="*60)
    response = requests.get(f"{BASE_URL}/a2a/tasks/{task_id}")
    print(f"Status Code: {response.status_code}")
    if response.status_code == 200:
        data = response.json()
        print(f"Task ID: {data.get('task_id')}")
        print(f"State: {data.get('state')}")
        print("✓ Get Task OK")
    else:
        print("✗ Get Task FAILED")
    return response.status_code == 200

def main():
    """Run all tests."""
    print("\n" + "="*60)
    print("Production Agent Endpoint Tests")
    print("="*60)
    print(f"Base URL: {BASE_URL}")

    # Give server a moment to fully start if just launched
    time.sleep(2)

    results = []

    # Run all tests
    results.append(("Agent Card", test_agent_card()))
    results.append(("Health Check", test_health()))
    results.append(("Equipment Status", test_equipment_status()))
    results.append(("OEE Summary", test_oee_summary()))
    results.append(("Downtime Summary", test_downtime_summary()))

    success, task_id = test_a2a_message_send()
    results.append(("A2A Message Send", success))

    if task_id:
        results.append(("Get Task", test_get_task(task_id)))

    # Print summary
    print("\n" + "="*60)
    print("TEST SUMMARY")
    print("="*60)
    for name, result in results:
        status = "✓ PASS" if result else "✗ FAIL"
        print(f"{name:.<40} {status}")

    total = len(results)
    passed = sum(1 for _, r in results if r)
    print(f"\nTotal: {passed}/{total} tests passed")

    if passed == total:
        print("\n🎉 All tests passed!")
    else:
        print(f"\n⚠️ {total - passed} test(s) failed")

if __name__ == "__main__":
    try:
        main()
    except requests.exceptions.ConnectionError:
        print("\n❌ ERROR: Could not connect to server.")
        print("Make sure the Production Agent is running on http://localhost:8001")
        print("Start it with: python src/production_agent.py")
