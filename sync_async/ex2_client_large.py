import asyncio
import os

HOST = '127.0.0.1'
PORT = 8889

def create_large_dummy(filename: str, size: int):
    # keep helper in case user wants to create a synthetic file
    if not os.path.exists(filename) or os.path.getsize(filename) != size:
        print(f"Creating large dummy file {filename} ({size} bytes)")
        with open(filename, 'wb') as f:
            f.write(os.urandom(size))

async def upload_large_file(filename: str, slow: float = 0.02):
    size = os.path.getsize(filename)
    reader, writer = await asyncio.open_connection(HOST, PORT)
    header = f"UPLOAD {os.path.basename(filename)} {size}\n"
    writer.write(header.encode())
    await writer.drain()

    sent = 0
    chunk_size = 64 * 1024
    with open(filename, 'rb') as f:
        while True:
            chunk = f.read(chunk_size)
            if not chunk:
                break
            writer.write(chunk)
            await writer.drain()
            sent += len(chunk)
            pct = sent * 100 / size
            print(f"Uploading {filename}: {sent}/{size} bytes ({pct:.1f}%)")
            # slow down to make progress observable
            if slow:
                await asyncio.sleep(slow)

    reply = await reader.readline()
    print(f"Upload {filename} -> server reply: {reply.decode().strip()}")
    writer.close(); await writer.wait_closed()

if __name__ == '__main__':
    # For manual run
    fname = 'sample_large.bin'
    size = 5 * 1024 * 1024  # 5 MB
    create_large_dummy(fname, size)
    asyncio.run(upload_large_file(fname))
