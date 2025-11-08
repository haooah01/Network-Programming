import asyncio
import os
import sys

sys.path.insert(0, os.path.dirname(__file__))

from ex2_server import handle, HOST, PORT
from ex2_client_large import create_large_dummy, upload_large_file

async def main():
    # Use the provided sample files under the 'source' subfolder
    base = os.path.join(os.path.dirname(__file__), 'source')
    sample_mp3 = os.path.join(base, 'file_example_MP3_5MG.mp3')
    sample_mp4 = os.path.join(base, 'file_example_MP4_1920_18MG.mp4')

    if not os.path.exists(sample_mp3) or not os.path.exists(sample_mp4):
        print('ERROR: sample files not found under async_exercises/source/.')
        print('Expected files: file_example_MP3_5MG.mp3 and file_example_MP4_1920_18MG.mp4')
        return

    server = await asyncio.start_server(handle, HOST, PORT)
    addr = server.sockets[0].getsockname()
    print(f"test: started ex2 large-server on {addr}")
    async with server:
        # run two uploads concurrently so we can observe streaming/progress
        await asyncio.gather(
            upload_large_file(sample_mp3, slow=0.01),
            upload_large_file(sample_mp4, slow=0.01)
        )
        # wait briefly to let server flush
        await asyncio.sleep(0.1)

if __name__ == '__main__':
    asyncio.run(main())
