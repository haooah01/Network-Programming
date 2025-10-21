import asyncio
import json
import struct
import time
from common import *

# Global clients registry: addr -> (writer, last_seen)
clients = {}

async def broadcast(msg, exclude_writer=None):
    """Broadcast message to all clients except the sender."""
    tasks = []
    for writer, _ in list(clients.values()):
        if writer != exclude_writer:
            tasks.append(send_msg_async(writer, msg))
    if tasks:
        await asyncio.gather(*tasks, return_exceptions=True)

async def send_msg_async(writer, obj):
    """Send JSON object asynchronously."""
    payload = json.dumps(obj, ensure_ascii=False).encode('utf-8')
    if len(payload) > MAX_MESSAGE:
        raise ValueError(f"Message too large: {len(payload)}")
    length = struct.pack('>I', len(payload))
    writer.write(length + payload)
    await writer.drain()

async def recv_msg_async(reader):
    """Receive JSON object asynchronously."""
    length_bytes = await reader.readexactly(4)
    length = struct.unpack('>I', length_bytes)[0]
    if length > MAX_MESSAGE:
        raise ValueError(f"Message too large: {length}")
    payload = await reader.readexactly(length)
    return json.loads(payload.decode('utf-8'))

async def heartbeat():
    """Send pings to idle clients and disconnect unresponsive ones."""
    while True:
        await asyncio.sleep(20)
        now = time.time()
        to_remove = []
        for addr, (writer, last_seen) in list(clients.items()):
            if now - last_seen > 40:  # Timeout after 2 heartbeats
                print(f"Disconnecting idle client: {addr}")
                writer.close()
                to_remove.append(addr)
            else:
                try:
                    ping = build_ping('server', 'default')
                    await send_msg_async(writer, ping)
                except Exception as e:
                    print(f"Heartbeat error for {addr}: {e}")
                    to_remove.append(addr)
        for addr in to_remove:
            if addr in clients:
                del clients[addr]

async def handle_client(reader, writer):
    """Handle a single async client."""
    addr = writer.get_extra_info('peername')
    addr_str = f"{addr[0]}:{addr[1]}"
    clients[addr_str] = (writer, time.time())
    print(f"Async client connected: {addr_str}")
    try:
        while True:
            msg = await recv_msg_async(reader)
            clients[addr_str] = (writer, time.time())  # Update last seen
            if msg['type'] == 'chat':
                await broadcast(msg, writer)
            elif msg['type'] == 'pong':
                pass  # Heartbeat response
            # Add more message types as needed
    except Exception as e:
        print(f"Client {addr_str} error: {e}")
    finally:
        if addr_str in clients:
            del clients[addr_str]
        writer.close()
        await writer.wait_closed()
        print(f"Client disconnected: {addr_str}")

async def main(host='0.0.0.0', port=5050):
    """Main async server."""
    server = await asyncio.start_server(handle_client, host, port)
    print(f"Async server listening on {host}:{port}")
    asyncio.create_task(heartbeat())
    try:
        await server.serve_forever()
    except KeyboardInterrupt:
        print("Async server shutting down")
    finally:
        server.close()
        await server.wait_closed()

if __name__ == '__main__':
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument('--host', default='0.0.0.0')
    parser.add_argument('--port', type=int, default=5050)
    args = parser.parse_args()
    asyncio.run(main(args.host, args.port))