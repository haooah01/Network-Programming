import asyncio
import os
import sys

# ensure imports from folder work
sys.path.insert(0, os.path.dirname(__file__))

from ex2_server import handle, HOST, PORT
from ex2_client import create_dummy_files, upload_file

async def main():
    # create dummy files first
    create_dummy_files()
    server = await asyncio.start_server(handle, HOST, PORT)
    addr = server.sockets[0].getsockname()
    print(f"test: started ex2 server on {addr}")
    async with server:
        # run concurrent uploads
        await asyncio.gather(
            upload_file('sample1.mp3'),
            upload_file('sample2.mp4')
        )
        await asyncio.sleep(0.1)

if __name__ == '__main__':
    asyncio.run(main())
