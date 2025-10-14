#!/usr/bin/env python3
"""
🧪 LIVE TEST: WebSocket Hybrid Implementation
Test all endpoints and verify core vs experimental channels
"""
import asyncio
import websockets
import json
from datetime import datetime
import os

UW_TOKEN = os.getenv("UW_API_TOKEN", "5809ee6a-bcb6-48ce-a16d-9f3bd634fd50")

async def test_backend_endpoint(endpoint_name, uri, duration=5):
    """Test a single backend WebSocket endpoint"""
    print(f"\n{'='*80}")
    print(f"🧪 Testing: {endpoint_name}")
    print(f"{'='*80}")
    print(f"URI: {uri}")
    
    try:
        async with websockets.connect(uri, timeout=10) as ws:
            print(f"✅ Connected successfully")
            print(f"⏳ Listening for {duration} seconds...")
            
            message_count = 0
            start_time = asyncio.get_event_loop().time()
            
            while (asyncio.get_event_loop().time() - start_time) < duration:
                try:
                    message = await asyncio.wait_for(ws.recv(), timeout=1.0)
                    message_count += 1
                    
                    # Parse message
                    try:
                        data = json.loads(message)
                        print(f"\n📨 Message #{message_count}:")
                        print(f"   Channel: {data.get('channel', 'N/A')}")
                        print(f"   Timestamp: {data.get('timestamp', 'N/A')}")
                        
                        if 'data' in data:
                            payload = data['data']
                            if isinstance(payload, dict):
                                print(f"   Keys: {', '.join(payload.keys())}")
                            else:
                                print(f"   Data: {str(payload)[:100]}")
                    except:
                        print(f"📨 Raw: {message[:150]}")
                        
                except asyncio.TimeoutError:
                    print(".", end="", flush=True)
                    continue
            
            print(f"\n\n📊 Result: {message_count} messages received in {duration}s")
            return {"status": "success", "messages": message_count}
            
    except Exception as e:
        print(f"\n❌ Error: {e}")
        return {"status": "error", "error": str(e)}


async def test_uw_direct(channel_name, duration=5):
    """Test UW WebSocket channel directly (bypass backend)"""
    print(f"\n{'='*80}")
    print(f"🐋 Testing UW Direct: {channel_name}")
    print(f"{'='*80}")
    
    uri = f"wss://api.unusualwhales.com/socket?token={UW_TOKEN}"
    
    try:
        async with websockets.connect(uri, timeout=10) as ws:
            print(f"✅ Connected to UW")
            
            # Subscribe to channel
            subscribe_msg = {
                "channel": channel_name,
                "msg_type": "join"
            }
            await ws.send(json.dumps(subscribe_msg))
            print(f"📡 Subscribed to: {channel_name}")
            
            message_count = 0
            start_time = asyncio.get_event_loop().time()
            
            while (asyncio.get_event_loop().time() - start_time) < duration:
                try:
                    message = await asyncio.wait_for(ws.recv(), timeout=1.0)
                    message_count += 1
                    
                    # Parse
                    try:
                        data = json.loads(message)
                        if isinstance(data, list) and len(data) >= 2:
                            ch, payload = data[0], data[1]
                            if payload != "ok":
                                print(f"\n📨 Message #{message_count}:")
                                print(f"   Channel: {ch}")
                                print(f"   Payload: {str(payload)[:150]}")
                    except:
                        print(f"📨 Raw: {message[:100]}")
                        
                except asyncio.TimeoutError:
                    print(".", end="", flush=True)
                    continue
            
            print(f"\n\n📊 Result: {message_count} messages received")
            return {"status": "success", "messages": message_count}
            
    except Exception as e:
        print(f"\n❌ Error: {e}")
        return {"status": "error", "error": str(e)}


async def main():
    """Run comprehensive tests"""
    
    print("\n" + "="*80)
    print("🚀 WEBSOCKET HYBRID IMPLEMENTATION - LIVE TEST")
    print("="*80)
    print(f"Timestamp: {datetime.now().isoformat()}")
    print(f"Backend: http://localhost:8000")
    print(f"UW Token: {UW_TOKEN[:20]}...")
    print("="*80)
    
    results = {}
    
    # ========================================================================
    # PART 1: Test Core Channels (Backend)
    # ========================================================================
    
    print("\n\n" + "="*80)
    print("✅ TESTING CORE CHANNELS (Verified)")
    print("="*80)
    
    core_endpoints = [
        ("Flow Alerts", "ws://localhost:8000/api/stream/ws/flow"),
        ("Gamma Exposure - SPY", "ws://localhost:8000/api/stream/ws/gex/SPY"),
        ("Gamma Exposure - TSLA", "ws://localhost:8000/api/stream/ws/gex/TSLA"),
    ]
    
    for name, uri in core_endpoints:
        results[name] = await test_backend_endpoint(name, uri, duration=5)
        await asyncio.sleep(1)
    
    # ========================================================================
    # PART 2: Test Experimental Channels (Backend)
    # ========================================================================
    
    print("\n\n" + "="*80)
    print("⚠️  TESTING EXPERIMENTAL CHANNELS")
    print("="*80)
    
    experimental_endpoints = [
        ("Market Movers", "ws://localhost:8000/api/stream/ws/market-movers"),
        ("Dark Pool", "ws://localhost:8000/api/stream/ws/dark-pool"),
        ("Congress Trades", "ws://localhost:8000/api/stream/ws/congress"),
    ]
    
    for name, uri in experimental_endpoints:
        results[name] = await test_backend_endpoint(name, uri, duration=5)
        await asyncio.sleep(1)
    
    # ========================================================================
    # PART 3: Test UW Channels Directly
    # ========================================================================
    
    print("\n\n" + "="*80)
    print("🐋 TESTING UW CHANNELS DIRECTLY (Bypass Backend)")
    print("="*80)
    
    uw_channels = [
        "flow-alerts",
        "gex:SPY",
        "market-movers",
        "market_movers",
        "dark-pool",
        "dark_pool",
        "congress",
        "congress-trades",
    ]
    
    for channel in uw_channels:
        results[f"UW Direct: {channel}"] = await test_uw_direct(channel, duration=3)
        await asyncio.sleep(0.5)
    
    # ========================================================================
    # FINAL SUMMARY
    # ========================================================================
    
    print("\n\n" + "="*80)
    print("📊 COMPREHENSIVE TEST RESULTS")
    print("="*80)
    
    print("\n✅ CORE CHANNELS (Backend):")
    for name in ["Flow Alerts", "Gamma Exposure - SPY", "Gamma Exposure - TSLA"]:
        result = results.get(name, {})
        status = result.get("status", "unknown")
        messages = result.get("messages", 0)
        emoji = "✅" if status == "success" else "❌"
        print(f"  {emoji} {name:<30} {status.upper():<10} {messages} msgs")
    
    print("\n⚠️  EXPERIMENTAL CHANNELS (Backend):")
    for name in ["Market Movers", "Dark Pool", "Congress Trades"]:
        result = results.get(name, {})
        status = result.get("status", "unknown")
        messages = result.get("messages", 0)
        emoji = "✅" if status == "success" else "❌"
        print(f"  {emoji} {name:<30} {status.upper():<10} {messages} msgs")
    
    print("\n🐋 UW DIRECT CHANNELS:")
    for channel in uw_channels:
        key = f"UW Direct: {channel}"
        result = results.get(key, {})
        status = result.get("status", "unknown")
        messages = result.get("messages", 0)
        emoji = "✅" if status == "success" else "❌"
        print(f"  {emoji} {channel:<30} {status.upper():<10} {messages} msgs")
    
    # ========================================================================
    # RECOMMENDATIONS
    # ========================================================================
    
    print("\n\n" + "="*80)
    print("💡 RECOMMENDATIONS")
    print("="*80)
    
    # Count successful core channels
    core_success = sum(1 for name in ["Flow Alerts", "Gamma Exposure - SPY", "Gamma Exposure - TSLA"] 
                      if results.get(name, {}).get("status") == "success")
    
    # Count experimental channels with data
    exp_with_data = sum(1 for name in ["Market Movers", "Dark Pool", "Congress Trades"]
                       if results.get(name, {}).get("messages", 0) > 0)
    
    print(f"\n1. Core Channels: {core_success}/3 working")
    if core_success == 3:
        print("   ✅ All core channels operational - ready for production!")
    elif core_success >= 2:
        print("   ⚠️  Most core channels working - investigate failures")
    else:
        print("   ❌ Core channels not working - check backend logs")
    
    print(f"\n2. Experimental Channels: {exp_with_data}/3 receiving data")
    if exp_with_data == 0:
        print("   ⚠️  No experimental channels receiving data")
        print("   → Recommendation: Keep hidden by default (hybrid approach working as designed)")
    elif exp_with_data < 3:
        print("   ⚠️  Some experimental channels receiving data")
        print("   → Recommendation: Verify which channels work and move to core")
    else:
        print("   ✅ All experimental channels working!")
        print("   → Recommendation: Move to core channels and update docs")
    
    print("\n3. Next Actions:")
    if exp_with_data == 0:
        print("   a) ✅ Keep hybrid approach (2 core + 3 hidden experimental)")
        print("   b) 📧 Contact UW support to confirm experimental channel names")
        print("   c) 🧪 Monitor logs for any data on experimental channels")
    else:
        print("   a) ✅ Update documentation with working experimental channels")
        print("   b) 🔄 Move verified experimental → core channels")
        print("   c) 📝 Update frontend to show working channels by default")
    
    print("\n" + "="*80)
    print("✅ TEST COMPLETE")
    print("="*80)
    
    # Save results to JSON
    output_file = "websocket_live_test_results.json"
    with open(output_file, "w") as f:
        json.dump({
            "timestamp": datetime.now().isoformat(),
            "results": results,
            "summary": {
                "core_working": core_success,
                "experimental_with_data": exp_with_data
            }
        }, f, indent=2)
    
    print(f"\n💾 Results saved to: {output_file}")


if __name__ == "__main__":
    asyncio.run(main())
