import asyncio
import datetime
import os

HOST = '127.0.0.1'
PORT = 8889


def _uploads_dir() -> str:
    base = os.path.dirname(__file__)
    path = os.path.join(base, 'uploads')
    os.makedirs(path, exist_ok=True)
    return path


async def handle(reader: asyncio.StreamReader, writer: asyncio.StreamWriter):
    addr = writer.get_extra_info('peername')
    header = await reader.readline()
    if not header:
        writer.close(); await writer.wait_closed()
        return

    try:
        parts = header.decode().strip().split()
        if len(parts) != 3 or parts[0].upper() != 'UPLOAD':
            raise ValueError('bad header')
        _, filename, size_str = parts
        size = int(size_str)
        if size < 0:
            raise ValueError('negative size')
    except Exception:
        writer.write(b"ERROR invalid header\n")
        await writer.drain()
        writer.close(); await writer.wait_closed()
        return

    ts = datetime.datetime.now().strftime('%Y%m%d-%H%M%S')
    saved_name = f"{ts}_{os.path.basename(filename)}"
    target_path = os.path.join(_uploads_dir(), saved_name)

    print(f"Receiving upload from {addr}: {filename} ({size} bytes) -> {target_path}")

    remaining = size
    chunk_size = 64 * 1024
    with open(target_path, 'wb') as f:
        while remaining > 0:
            to_read = min(chunk_size, remaining)
            chunk = await reader.readexactly(to_read)
            f.write(chunk)
            remaining -= len(chunk)

    writer.write(f"OK {saved_name}\n".encode())
    await writer.drain()
    writer.close(); await writer.wait_closed()
    print(f"Saved {target_path} ({size} bytes)")


async def main():
    server = await asyncio.start_server(handle, HOST, PORT)
    addr = server.sockets[0].getsockname()
    print(f"ex2_server serving on {addr}")
    async with server:
        await server.serve_forever()


if __name__ == '__main__':
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print('Server stopped')

