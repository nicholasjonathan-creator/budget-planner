#!/usr/bin/env python3
"""
Render-specific monitoring script
Handles free tier sleep/wake patterns
"""

import asyncio
import aiohttp
import time
from datetime import datetime

class RenderMonitor:
    def __init__(self, backend_url, frontend_url):
        self.backend_url = backend_url
        self.frontend_url = frontend_url
    
    async def wake_services(self):
        """Wake up sleeping services on Render free tier"""
        print("🌅 Waking up services...")
        
        async with aiohttp.ClientSession() as session:
            # Wake backend
            try:
                async with session.get(f"{self.backend_url}/api/health", timeout=30) as response:
                    if response.status == 200:
                        print("✅ Backend is awake")
                    else:
                        print(f"⚠️  Backend responded with {response.status}")
            except Exception as e:
                print(f"❌ Backend wake failed: {e}")
            
            # Wake frontend
            try:
                async with session.get(self.frontend_url, timeout=30) as response:
                    if response.status == 200:
                        print("✅ Frontend is awake")
                    else:
                        print(f"⚠️  Frontend responded with {response.status}")
            except Exception as e:
                print(f"❌ Frontend wake failed: {e}")
    
    async def keep_alive(self, interval_minutes=10):
        """Keep services alive by pinging them regularly"""
        print(f"🔄 Starting keep-alive (every {interval_minutes} minutes)")
        
        while True:
            await self.wake_services()
            print(f"💤 Sleeping for {interval_minutes} minutes...")
            await asyncio.sleep(interval_minutes * 60)

if __name__ == "__main__":
    import sys
    
    if len(sys.argv) < 3:
        print("Usage: python monitor-render.py <backend_url> <frontend_url>")
        sys.exit(1)
    
    backend_url = sys.argv[1]
    frontend_url = sys.argv[2]
    
    monitor = RenderMonitor(backend_url, frontend_url)
    
    if len(sys.argv) > 3 and sys.argv[3] == "--keep-alive":
        asyncio.run(monitor.keep_alive())
    else:
        asyncio.run(monitor.wake_services())
