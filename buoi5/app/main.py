#!/usr/bin/env python3
"""
SyncAsync Chat & File Transfer Application

A unified entry point for running the chat and file transfer servers and clients.
"""

import argparse
import sys
import os

# Add app to path
sys.path.insert(0, os.path.dirname(__file__))

from sync_server import main as sync_server_main
from sync_client import main as sync_client_main
from sync_file_sender import main as sync_file_sender_main
from sync_file_receiver import main as sync_file_receiver_main
from async_server import main as async_server_main
from async_client import main as async_client_main
from async_file_sender import main as async_file_sender_main
from async_file_receiver import main as async_file_receiver_main

def main():
    parser = argparse.ArgumentParser(
        description="SyncAsync Chat & File Transfer",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python main.py sync-server --port 5050
  python main.py sync-client --host 127.0.0.1 --port 5050 --name alice
  python main.py async-server --port 5050
  python main.py async-client --host 127.0.0.1 --port 5050 --name bob
  python main.py sync-file-send --path ./file.txt --host 127.0.0.1 --port 5050
  python main.py sync-file-recv --port 5050
        """
    )

    subparsers = parser.add_subparsers(dest='command', help='Available commands')

    # Sync Server
    sync_server_parser = subparsers.add_parser('sync-server', help='Start synchronous chat server')
    sync_server_parser.add_argument('--host', default='0.0.0.0', help='Host to bind to')
    sync_server_parser.add_argument('--port', type=int, default=5050, help='Port to listen on')

    # Sync Client
    sync_client_parser = subparsers.add_parser('sync-client', help='Start synchronous chat client')
    sync_client_parser.add_argument('--host', default='127.0.0.1', help='Server host')
    sync_client_parser.add_argument('--port', type=int, default=5050, help='Server port')
    sync_client_parser.add_argument('--name', default='user', help='Your name')
    sync_client_parser.add_argument('--room', default='default', help='Chat room')

    # Sync File Sender
    sync_file_send_parser = subparsers.add_parser('sync-file-send', help='Send file synchronously')
    sync_file_send_parser.add_argument('--path', required=True, help='Path to file to send')
    sync_file_send_parser.add_argument('--host', default='127.0.0.1', help='Receiver host')
    sync_file_send_parser.add_argument('--port', type=int, default=5050, help='Receiver port')
    sync_file_send_parser.add_argument('--name', default='sender', help='Sender name')
    sync_file_send_parser.add_argument('--room', default='default', help='Room')

    # Sync File Receiver
    sync_file_recv_parser = subparsers.add_parser('sync-file-recv', help='Receive files synchronously')
    sync_file_recv_parser.add_argument('--host', default='0.0.0.0', help='Host to bind to')
    sync_file_recv_parser.add_argument('--port', type=int, default=5050, help='Port to listen on')

    # Async Server
    async_server_parser = subparsers.add_parser('async-server', help='Start asynchronous chat server')
    async_server_parser.add_argument('--host', default='0.0.0.0', help='Host to bind to')
    async_server_parser.add_argument('--port', type=int, default=5050, help='Port to listen on')

    # Async Client
    async_client_parser = subparsers.add_parser('async-client', help='Start asynchronous chat client')
    async_client_parser.add_argument('--host', default='127.0.0.1', help='Server host')
    async_client_parser.add_argument('--port', type=int, default=5050, help='Server port')
    async_client_parser.add_argument('--name', default='user', help='Your name')
    async_client_parser.add_argument('--room', default='default', help='Chat room')

    # Async File Sender
    async_file_send_parser = subparsers.add_parser('async-file-send', help='Send file asynchronously')
    async_file_send_parser.add_argument('--path', required=True, help='Path to file to send')
    async_file_send_parser.add_argument('--host', default='127.0.0.1', help='Receiver host')
    async_file_send_parser.add_argument('--port', type=int, default=5050, help='Receiver port')
    async_file_send_parser.add_argument('--name', default='sender', help='Sender name')
    async_file_send_parser.add_argument('--room', default='default', help='Room')

    # Async File Receiver
    async_file_recv_parser = subparsers.add_parser('async-file-recv', help='Receive files asynchronously')
    async_file_recv_parser.add_argument('--host', default='0.0.0.0', help='Host to bind to')
    async_file_recv_parser.add_argument('--port', type=int, default=5050, help='Port to listen on')

    args = parser.parse_args()

    if not args.command:
        parser.print_help()
        return

    # Dispatch to the appropriate main function
    if args.command == 'sync-server':
        sync_server_main(args.host, args.port)
    elif args.command == 'sync-client':
        sync_client_main(args.host, args.port, args.name, args.room)
    elif args.command == 'sync-file-send':
        sync_file_sender_main(args.host, args.port, args.path, args.name, args.room)
    elif args.command == 'sync-file-recv':
        sync_file_receiver_main(args.host, args.port)
    elif args.command == 'async-server':
        import asyncio
        asyncio.run(async_server_main(args.host, args.port))
    elif args.command == 'async-client':
        import asyncio
        asyncio.run(async_client_main(args.host, args.port, args.name, args.room))
    elif args.command == 'async-file-send':
        import asyncio
        asyncio.run(async_file_sender_main(args.host, args.port, args.path, args.name, args.room))
    elif args.command == 'async-file-recv':
        import asyncio
        asyncio.run(async_file_receiver_main(args.host, args.port))
    else:
        parser.print_help()

if __name__ == '__main__':
    main()