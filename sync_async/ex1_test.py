import asyncio
import os
import sys

# ensure module imports from this folder work when run via full path
sys.path.insert(0, os.path.dirname(__file__))

from ex1_server import handle, HOST, PORT
from ex1_client import send_number

async def main():
    server = await asyncio.start_server(handle, HOST, PORT)
    addr = server.sockets[0].getsockname()
    print(f"test: started server on {addr}")
    async with server:
        # run two client tasks that connect to server while server runs in-process
        await asyncio.gather(
            send_number(10),
            send_number(2)
        )
        # short sleep to let server print its final logs
        await asyncio.sleep(0.1)

if __name__ == '__main__':
    asyncio.run(main())
