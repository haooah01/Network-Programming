import asyncio
import datetime

HOST = '127.0.0.1'
PORT = 8888

async def handle(reader: asyncio.StreamReader, writer: asyncio.StreamWriter):
    addr = writer.get_extra_info('peername')
    line = await reader.readline()
    if not line:
        writer.close()
        await writer.wait_closed()
        return
    try:
        n = int(line.decode().strip())
    except Exception as e:
        writer.write(b"ERROR: invalid number\n")
        await writer.drain()
        writer.close()
        await writer.wait_closed()
        return

    print(f"[{datetime.datetime.now().isoformat()}] Received {n} from {addr}, sleeping {n}s")
    # simulate work that takes n seconds
    await asyncio.sleep(n)
    resp = f"RESULT {n} after {n}s\n".encode()
    writer.write(resp)
    await writer.drain()
    writer.close()
    await writer.wait_closed()
    print(f"[{datetime.datetime.now().isoformat()}] Replied for {n} to {addr}")

async def main():
    server = await asyncio.start_server(handle, HOST, PORT)
    addr = server.sockets[0].getsockname()
    print(f"ex1_server serving on {addr}")
    async with server:
        await server.serve_forever()

if __name__ == '__main__':
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print('Server stopped')
