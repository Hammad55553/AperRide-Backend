"""
Vercel serverless entrypoint.
NOTE: Socket.IO (realtime) yahan disabled hai — Vercel serverless WebSocket
support nahi karta. Live location/chat/bids baad me Render/Railway par shift honge.
Yahan sirf REST API (auth, rides, drivers, wallet) chalti hai.
"""
from app.main import app

# Vercel Python runtime `app` naam ka ASGI callable dhoondhta hai
