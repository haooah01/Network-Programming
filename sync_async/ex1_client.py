import asyncio

HOST = '127.0.0.1'
PORT = 8888

async def send_number(n: int):
    reader, writer = await asyncio.open_connection(HOST, PORT)
    print(f"Client: sending {n}")
    writer.write(f"{n}\n".encode())
    await writer.drain()
    data = await reader.readline()
    print(f"Client: reply for {n}: {data.decode().strip()}")
    writer.close()
    await writer.wait_closed()

async def main():
    # send two numbers concurrently to demonstrate non-blocking behavior
    tasks = [asyncio.create_task(send_number(10)), asyncio.create_task(send_number(2))]
    await asyncio.gather(*tasks)

if __name__ == '__main__':
    asyncio.run(main())
