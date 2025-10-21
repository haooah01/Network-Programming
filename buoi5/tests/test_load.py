import asyncio
import socket
from app.common import send_msg, build_chat

async def test_load():
    # Simple load test: connect multiple clients
    async def client_task():
        reader, writer = await asyncio.open_connection('127.0.0.1', 5050)
        msg = build_chat("load test", "client")
        # Send message
        payload = json.dumps(msg).encode('utf-8')
        length = struct.pack('>I', len(payload))
        writer.write(length + payload)
        await writer.drain()
        writer.close()
        await writer.wait_closed()

    # Run 10 clients
    tasks = [client_task() for _ in range(10)]
    await asyncio.gather(*tasks)
    assert True  # Placeholder

# Note: Requires server running on 5050