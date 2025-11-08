import asyncio
import os

# Use the same host/port as the server
from ex2_server import HOST, PORT  # type: ignore


def _ensure_dummy(filename: str, size: int):
    if not os.path.exists(filename) or os.path.getsize(filename) != size:
        print(f"Creating dummy file {filename} ({size} bytes)")
        with open(filename, 'wb') as f:
            f.write(os.urandom(size))


def create_dummy_files():
    _ensure_dummy('sample1.mp3', 10 * 1024)
    _ensure_dummy('sample2.mp4', 20 * 1024)


async def upload_file(filename: str):
    size = os.path.getsize(filename)
    reader, writer = await asyncio.open_connection(HOST, PORT)
    header = f"UPLOAD {os.path.basename(filename)} {size}\n".encode()
    writer.write(header)
    await writer.drain()

    with open(filename, 'rb') as f:
        while True:
            chunk = f.read(64 * 1024)
            if not chunk:
                break
            writer.write(chunk)
            await writer.drain()

    reply = await reader.readline()
    print(f"Upload {filename} -> server reply: {reply.decode().strip()}")
    writer.close(); await writer.wait_closed()


if __name__ == '__main__':
    # simple manual run: create and upload both files concurrently
    create_dummy_files()
    async def _run():
        await asyncio.gather(upload_file('sample1.mp3'), upload_file('sample2.mp4'))
    asyncio.run(_run())

