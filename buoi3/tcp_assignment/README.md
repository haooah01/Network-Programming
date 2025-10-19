# TCP Assignment - Network Programming

This folder contains Python implementations for 10 TCP/Socket programming requirements. Each requirement is covered by a dedicated server/client pair. All code and instructions are in English.

## Requirements & Files

1. **Echo TCP**
   - `tcp_echo_server.py`, `tcp_echo_client.py`
   - Client sends "Hello World"; server replies "Received: Hello World" and exits.

2. **Echo TCP (Uppercase)**
   - `tcp_echo_upper_server.py`, `tcp_echo_upper_client.py`
   - Client sends "Hello World"; server replies "RECEIVED HELLO WORLD" (uppercase) and exits.

3. **Chat (Single Message)**
   - `tcp_chat_server.py`, `tcp_chat_client.py`
   - Client sends one message; server replies and exits.

4. **Chat (Multi Message, Quit with 0)**
   - `tcp_chat_multi_server.py`, `tcp_chat_multi_client.py`
   - Client sends multiple messages; server replies; type "0" to quit.

5. **Send Number ≤ 10, Reply in Words, Quit**
   - `tcp_number_server.py`, `tcp_number_client.py`
   - Client sends a number (1–10); server replies with word; type "Quit" to exit.

6. **Chat with IP/Port Input**
   - `tcp_chat_multi_client.py`
   - Client prompts for server IP and port before connecting.

7. **Chat with Encoding/Decoding**
   - `tcp_chat_encode_server.py`, `tcp_chat_encode_client.py`
   - Client encodes message (+1 ASCII); server decodes (-1 ASCII); type "0" to quit.

8. **Chat with Password Authentication**
   - `tcp_chat_auth_server.py`, `tcp_chat_auth_client.py`
   - Client must enter password; server checks before allowing chat; type "0" to quit.

9. **Number Server with Delay**
   - `tcp_number_delay_server.py`, `tcp_number_delay_client.py`
   - Server waits N seconds (N = number sent) before replying; type "Quit" to exit.

10. **Chat with Exception Handling**
    - `tcp_chat_exception_server.py`, `tcp_chat_exception_client.py`
    - Both server and client catch and display errors; type "0" to quit.

## How to Run

1. Open two terminals in this folder (`buoi3/tcp_assignment`).
2. In one terminal, run the server file (e.g., `py tcp_echo_server.py`).
3. In the other terminal, run the client file (e.g., `py tcp_echo_client.py`).
4. Follow the prompts in the client and server windows.

## Notes
- All code is written in Python 3.
- All communication is via TCP sockets.
- Each feature is independent and can be tested separately.
- For encoding/decoding, password, and IP/Port input, follow the client prompts.

---

**Author:** hao
**Course:** Network Programming
**Date:** October 2025
