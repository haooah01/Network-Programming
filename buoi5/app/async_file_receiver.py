import asyncio
import os
import hashlib
import base64
from common import *

MAX_CHUNK_BYTES = 65536

# Ongoing transfers: corr_id -> {'file': file_obj, 'size': int, 'sha256': hashlib, 'received': int, 'expected_sha256': str}
ongoing = {}

async def handle_client(reader, writer):
    """Handle async file transfer client."""
    addr = writer.get_extra_info('peername')
    addr_str = f"{addr[0]}:{addr[1]}"
    print(f"Async file receiver client connected: {addr_str}")
    loop = asyncio.get_event_loop()
    try:
        while True:
            msg = await recv_msg_async(reader)
            if msg['type'] == 'file_meta':
                filename = msg['name']
                size = msg['size']
                expected_sha256 = msg['sha256']
                filepath = os.path.join('./inbox', filename)
                await loop.run_in_executor(None, os.makedirs, './inbox', exist_ok=True)
                file_obj = await loop.run_in_executor(None, open, filepath, 'wb')
                ongoing[msg['corr_id']] = {
                    'file': file_obj,
                    'size': size,
                    'sha256': hashlib.sha256(),
                    'received': 0,
                    'expected_sha256': expected_sha256
                }
                ack = build_ack(True, msg['corr_id'], from_user='receiver')
                await send_msg_async(writer, ack)
            elif msg['type'] == 'file_chunk':
                corr_id = msg['corr_id']
                if corr_id in ongoing:
                    transfer = ongoing[corr_id]
                    chunk_bytes = base64.b64decode(msg['bytes_b64'])
                    await loop.run_in_executor(None, transfer['file'].write, chunk_bytes)
                    transfer['sha256'].update(chunk_bytes)
                    transfer['received'] += len(chunk_bytes)
                    if transfer['received'] >= transfer['size']:
                        await loop.run_in_executor(None, transfer['file'].close)
                        actual_sha256 = transfer['sha256'].hexdigest()
                        ok = actual_sha256 == transfer['expected_sha256']
                        ack = build_ack(ok, corr_id, error='Checksum mismatch' if not ok else None, from_user='receiver')
                        await send_msg_async(writer, ack)
                        del ongoing[corr_id]
    except Exception as e:
        print(f"Client {addr_str} error: {e}")
    finally:
        writer.close()
        await writer.wait_closed()

async def main(host='0.0.0.0', port=5050):
    """Main async file receiver server."""
    server = await asyncio.start_server(handle_client, host, port)
    print(f"Async file receiver listening on {host}:{port}")
    try:
        await server.serve_forever()
    except KeyboardInterrupt:
        print("Async file receiver shutting down")
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