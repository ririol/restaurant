import aiohttp
import asyncio

from config import BACKEND_WS


async def consumer(status):
    async with aiohttp.ClientSession(trust_env = True) as session:
        status.subheader(f"Connecting to {BACKEND_WS}")
        async with session.ws_connect(BACKEND_WS) as websocket:
            status.subheader(f"Connected to: {BACKEND_WS}")
            async for message in websocket:
                status.write(message.data)


    