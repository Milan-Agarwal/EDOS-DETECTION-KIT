#!/usr/bin/env python3
"""
Quick test script to verify the backend is working correctly
"""

import sys
import os
import asyncio
import httpx
import json

# Add the backend directory to Python path
sys.path.append("/home/puneet/dev/WEB/edos-security-dashboard/backend")


async def test_backend():
    """Test the backend endpoints"""
    base_url = "http://localhost:8000"

    print("🧪 Testing EDoS Security Dashboard Backend")
    print("=" * 50)

    async with httpx.AsyncClient() as client:
        try:
            # Test health endpoint
            print("1. Testing health endpoint...")
            response = await client.get(f"{base_url}/health")
            if response.status_code == 200:
                print("   ✅ Health check passed")
                print(f"   📊 Response: {response.json()}")
            else:
                print(f"   ❌ Health check failed: {response.status_code}")

            # Test root endpoint
            print("\n2. Testing root endpoint...")
            response = await client.get(base_url)
            if response.status_code == 200:
                print("   ✅ Root endpoint working")
                print(f"   📊 Response: {response.json()}")
            else:
                print(f"   ❌ Root endpoint failed: {response.status_code}")

            # Test login (this should work without authentication)
            print("\n3. Testing authentication...")
            login_data = {"username": "admin", "password": "admin123"}
            response = await client.post(f"{base_url}/api/auth/login", json=login_data)
            if response.status_code == 200:
                print("   ✅ Authentication working")
                auth_response = response.json()
                token = auth_response.get("access_token")
                print(f"   🔑 Token received: {token[:20]}...")

                # Test authenticated endpoints
                headers = {"Authorization": f"Bearer {token}"}

                # Test alerts endpoint
                print("\n4. Testing alerts endpoint...")
                response = await client.get(f"{base_url}/api/alerts/", headers=headers)
                if response.status_code == 200:
                    alerts = response.json()
                    print(f"   ✅ Alerts endpoint working - Found {len(alerts)} alerts")
                else:
                    print(f"   ❌ Alerts endpoint failed: {response.status_code}")

                # Test network traffic endpoint
                print("\n5. Testing network traffic endpoint...")
                response = await client.get(
                    f"{base_url}/api/network/traffic/real-time", headers=headers
                )
                if response.status_code == 200:
                    traffic = response.json()
                    print(f"   ✅ Network traffic endpoint working")
                    print(
                        f"   🌐 Arcs: {len(traffic.get('arcs', []))}, Points: {len(traffic.get('points', []))}"
                    )
                else:
                    print(
                        f"   ❌ Network traffic endpoint failed: {response.status_code}"
                    )

                # Test metrics endpoint
                print("\n6. Testing metrics endpoint...")
                response = await client.get(
                    f"{base_url}/api/metrics/dashboard", headers=headers
                )
                if response.status_code == 200:
                    metrics = response.json()
                    print(f"   ✅ Metrics endpoint working")
                    print(f"   📈 Overview: {metrics.get('overview', {})}")
                else:
                    print(f"   ❌ Metrics endpoint failed: {response.status_code}")

            else:
                print(f"   ❌ Authentication failed: {response.status_code}")
                print(f"   🚫 Response: {response.text}")

        except Exception as e:
            print(f"❌ Error testing backend: {e}")
            return False

    print("\n🎉 Backend test completed!")
    return True


if __name__ == "__main__":
    asyncio.run(test_backend())
