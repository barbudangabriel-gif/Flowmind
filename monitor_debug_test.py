#!/usr/bin/env python3
"""
Debug Monitor Issue - Check why monitor stops immediately
"""

import requests
import json
import time
from datetime import datetime

def log(message):
    timestamp = datetime.now().strftime("%H:%M:%S")
    print(f"[{timestamp}] {message}")

def test_monitor_debug():
    base_url = "https://put-selling-dash.preview.emergentagent.com"
    api_url = f"{base_url}/api"
    
    # Proper payload format
    demo_payload = {
        "positions": [
            {
                "ticker": "AAPL",
                "price": 150.0,
                "strike": 145.0,
                "delta": 0.28,
                "dte": 30,
                "premium": 2.50,
                "iv_rank": 45.0,
                "vix": 20.0,
                "selected": True
            }
        ],
        "config": {
            "capital_base": 500000
        },
        "mode": "equal",
        "interval_seconds": 15
    }
    
    log("🔍 DEBUG: Testing monitor workflow step by step")
    
    # Step 1: Check initial status
    log("\n📊 Step 1: Check initial monitor status")
    try:
        response = requests.get(f"{api_url}/options/selling/monitor/status", timeout=10)
        if response.status_code == 200:
            data = response.json()
            log(f"   Initial Status: {json.dumps(data, indent=2)}")
        else:
            log(f"   Status check failed: {response.status_code}")
    except Exception as e:
        log(f"   Status check error: {str(e)}")
    
    # Step 2: Start monitor
    log("\n🚀 Step 2: Start monitor")
    try:
        response = requests.post(
            f"{api_url}/options/selling/monitor/start", 
            json=demo_payload, 
            headers={'Content-Type': 'application/json'},
            timeout=10
        )
        if response.status_code == 200:
            data = response.json()
            log(f"   Start Response: {json.dumps(data, indent=2)}")
        else:
            log(f"   Start failed: {response.status_code} - {response.text}")
            return
    except Exception as e:
        log(f"   Start error: {str(e)}")
        return
    
    # Step 3: Check status immediately after start
    log("\n📊 Step 3: Check status immediately after start")
    try:
        response = requests.get(f"{api_url}/options/selling/monitor/status", timeout=10)
        if response.status_code == 200:
            data = response.json()
            log(f"   Immediate Status: {json.dumps(data, indent=2)}")
        else:
            log(f"   Status check failed: {response.status_code}")
    except Exception as e:
        log(f"   Status check error: {str(e)}")
    
    # Step 4: Wait a few seconds and check again
    log("\n⏳ Step 4: Wait 5 seconds and check status")
    time.sleep(5)
    try:
        response = requests.get(f"{api_url}/options/selling/monitor/status", timeout=10)
        if response.status_code == 200:
            data = response.json()
            log(f"   Status after 5s: {json.dumps(data, indent=2)}")
        else:
            log(f"   Status check failed: {response.status_code}")
    except Exception as e:
        log(f"   Status check error: {str(e)}")
    
    # Step 5: Wait longer and check
    log("\n⏳ Step 5: Wait 20 seconds total and check status")
    time.sleep(15)  # Total 20 seconds
    try:
        response = requests.get(f"{api_url}/options/selling/monitor/status", timeout=10)
        if response.status_code == 200:
            data = response.json()
            log(f"   Status after 20s: {json.dumps(data, indent=2)}")
            
            # Check if monitor is running and has cycles
            running = data.get('running', False)
            cycles = data.get('cycles', 0)
            
            if running and cycles > 0:
                log("✅ Monitor is working correctly!")
            elif running and cycles == 0:
                log("⚠️  Monitor is running but no cycles completed yet")
            elif not running and cycles > 0:
                log("⚠️  Monitor stopped but had completed cycles")
            else:
                log("❌ Monitor is not running and no cycles completed")
                
        else:
            log(f"   Status check failed: {response.status_code}")
    except Exception as e:
        log(f"   Status check error: {str(e)}")
    
    # Step 6: Try to stop monitor
    log("\n🛑 Step 6: Stop monitor")
    try:
        response = requests.post(f"{api_url}/options/selling/monitor/stop", timeout=10)
        if response.status_code == 200:
            data = response.json()
            log(f"   Stop Response: {json.dumps(data, indent=2)}")
        else:
            log(f"   Stop failed: {response.status_code} - {response.text}")
    except Exception as e:
        log(f"   Stop error: {str(e)}")

if __name__ == "__main__":
    test_monitor_debug()