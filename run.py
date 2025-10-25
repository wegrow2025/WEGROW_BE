#!/usr/bin/env python3
"""
We:Grow RealTime Audio API 실행 스크립트
"""

import uvicorn
from config import settings

if __name__ == "__main__":
    print("Starting We:Grow RealTime Audio API server...")
    print(f"Server address: http://{settings.host}:{settings.port}")
    print(f"WebSocket: ws://{settings.host}:{settings.port}/ws")
    print(f"API documentation: http://{settings.host}:{settings.port}/docs")
    print(f"WebSocket test: http://{settings.host}:{settings.port}/ws/test")
    print("=" * 50)
    
    uvicorn.run(
        "main:app",
        host=settings.host,
        port=settings.port,
        reload=True,
        log_level="info"
    )
