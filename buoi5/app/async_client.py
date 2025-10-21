import asyncio
from common import *

async def reader(reader):
    """Async reader coroutine to print incoming messages."""
    while True:
        try:
            msg = await recv_msg_async(reader)
            if msg['type'] == 'chat':
                print(f"[{msg['from']}]: {msg['text']}")
            elif msg['type'] == 'ack':
                print(f"ACK: {msg}")
            elif msg['type'] == 'pong':
                pass  # Heartbeat response
            # Handle other message types
        except Exception as e:
            print(f"Reader error: {e}")
            break

async def writer(writer, name, room):
    """Async writer coroutine to send user input."""
    loop = asyncio.get_event_loop()
    while True:
        try:
            text = await loop.run_in_executor(None, input, "")
            if text.lower() == 'quit':
                break
            msg = build_chat(text, name, room)
            await send_msg_async(writer, msg)
        except Exception as e:
            print(f"Writer error: {e}")
            break

async def main(host='127.0.0.1', port=5050, name='user', room='default'):
    """Main async client."""
    reader_stream, writer_stream = await asyncio.open_connection(host, port)
    print(f"Connected to {host}:{port} as {name} in room {room}")

    await asyncio.gather(
        reader(reader_stream),
        writer(writer_stream, name, room)
    )

    writer_stream.close()
    await writer_stream.wait_closed()

if __name__ == '__main__':
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument('--host', default='127.0.0.1')
    parser.add_argument('--port', type=int, default=5050)
    parser.add_argument('--name', default='user')
    parser.add_argument('--room', default='default')
    args = parser.parse_args()
    asyncio.run(main(args.host, args.port, args.name, args.room))