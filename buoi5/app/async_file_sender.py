import asyncio
import os
import hashlib
import base64
from common import *

MAX_CHUNK_BYTES = 65536

async def send_file_async(reader, writer, filepath, name, from_user, room):
    """Send file asynchronously."""
    loop = asyncio.get_event_loop()
    if not await loop.run_in_executor(None, os.path.exists, filepath):
        raise FileNotFoundError(f"File not found: {filepath}")

    size = await loop.run_in_executor(None, os.path.getsize, filepath)
    with open(filepath, 'rb') as f:
        data = await loop.run_in_executor(None, f.read)
    sha256 = hashlib.sha256(data).hexdigest()

    meta = build_file_meta(name, size, sha256, from_user, room)
    await send_msg_async(writer, meta)

    # Wait for ACK
    ack = await recv_msg_async(reader)
    if not ack.get('ok', False):
        raise Exception(f"Meta not acknowledged: {ack.get('error', 'Unknown')}")

    # Send chunks
    offset = 0
    while offset < size:
        chunk = data[offset:offset + MAX_CHUNK_BYTES]
        chunk_b64 = base64.b64encode(chunk).decode('ascii')
        chunk_msg = build_file_chunk(offset, chunk_b64, from_user, room, meta['corr_id'])
        await send_msg_async(writer, chunk_msg)
        offset += len(chunk)

    # Wait for final ACK
    final_ack = await recv_msg_async(reader)
    if not final_ack.get('ok', False):
        raise Exception(f"File transfer failed: {final_ack.get('error', 'Unknown')}")

async def main(host='127.0.0.1', port=5050, filepath='', name='sender', room='default'):
    """Main async file sender."""
    reader, writer = await asyncio.open_connection(host, port)
    filename = os.path.basename(filepath)
    print(f"Sending file {filename} to {host}:{port}")
    await send_file_async(reader, writer, filepath, filename, name, room)
    print("File sent successfully")
    writer.close()
    await writer.wait_closed()

if __name__ == '__main__':
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument('--host', default='127.0.0.1')
    parser.add_argument('--port', type=int, default=5050)
    parser.add_argument('--path', required=True, help='Path to file to send')
    parser.add_argument('--name', default='sender')
    parser.add_argument('--room', default='default')
    args = parser.parse_args()
    asyncio.run(main(args.host, args.port, args.path, args.name, args.room))