Async exercises for the network programming assignment (converted from the slide exercises to asynchronous implementations).

Files:
- ex1_server.py: asyncio TCP server that receives a number N and replies after N seconds.
- ex1_client.py: asyncio client that concurrently sends numbers (e.g., 10 and 2) and prints replies as they arrive (shorter tasks finish first).
- ex2_server.py: asyncio TCP server that accepts simple "UPLOAD filename size\n" headers followed by raw bytes, and saves files with a timestamp prefix.
- ex2_client.py: asyncio client that creates sample files (mp3/mp4-like) and uploads them concurrently to demonstrate non-blocking uploads.

How to run (PowerShell):
1) Start server for exercise 1 (in a terminal):
   python -u "d:\Documents-D\VS Code\network programming\async_exercises\ex1_server.py"

2) In another terminal run client:
   python "d:\Documents-D\VS Code\network programming\async_exercises\ex1_client.py"

3) For exercise 2 start server:
   python -u "d:\Documents-D\VS Code\network programming\async_exercises\ex2_server.py"

4) In another terminal run client to upload sample files:
   python "d:\Documents-D\VS Code\network programming\async_exercises\ex2_client.py"

Notes: these examples use only the Python standard library (asyncio). Files uploaded by `ex2_client.py` are small dummy files created at runtime.

Explanation of results (what you saw when running the tests)
---------------------------------------------------------

1) Exercise 1 (numbers — `ex1_test.py` or `ex1_client.py` against `ex1_server.py`)

    - What the test does: the client(s) send integer values N to the server. The server
       simulates work by awaiting asyncio.sleep(N) and then replies with a line
       "RESULT N after Ns".

    - Example output observed (from `ex1_test.py`):

          test: started server on ('127.0.0.1', 8888)
          Client: sending 10
          Client: sending 2
          [2025-11-08T15:51:03.241877] Received 2 from ('127.0.0.1', 30866), sleeping 2s
          [2025-11-08T15:51:03.241877] Received 10 from ('127.0.0.1', 30865), sleeping 10s
          Client: reply for 2: RESULT 2 after 2s
          [2025-11-08T15:51:05.251583] Replied for 2 to ('127.0.0.1', 30866)
          Client: reply for 10: RESULT 10 after 10s
          [2025-11-08T15:51:13.245187] Replied for 10 to ('127.0.0.1', 30865)

    - Interpretation: even though the client sent 10 and 2 almost at the same time,
       the server handled both requests concurrently (each connection has its own
       coroutine). The 2-second job finished and returned a reply before the 10-second
       job, demonstrating non-blocking (asynchronous) server behavior.

2) Exercise 2 (file upload — `ex2_test.py` or `ex2_client.py` against `ex2_server.py`)

    - Protocol summary: the client first sends a single-line header
       "UPLOAD <filename> <size>\n" then sends exactly <size> bytes of raw file data.
       The server reads the header, reads the specified byte count, saves the file
       (prefixing the filename with a timestamp) and replies "OK <saved_name>\n".

    - Example output observed (from `ex2_test.py`):

          Creating dummy file sample1.mp3 (10240 bytes)
          Creating dummy file sample2.mp4 (20480 bytes)
          test: started ex2 server on ('127.0.0.1', 8889)
          Receiving upload from ('127.0.0.1', 31477): sample2.mp4 (20480 bytes) -> d:\...\uploads\20251108-155128_sample2.mp4
          Receiving upload from ('127.0.0.1', 31476): sample1.mp3 (10240 bytes) -> d:\...\uploads\20251108-155128_sample1.mp3
          Upload sample2.mp4 -> server reply: OK 20251108-155128_sample2.mp4
          Upload sample1.mp3 -> server reply: OK 20251108-155128_sample1.mp3
          Saved d:\...\uploads\20251108-155128_sample2.mp4 (20480 bytes)
          Saved d:\...\uploads\20251108-155128_sample1.mp3 (10240 bytes)

    - Interpretation: the client created two dummy files locally and uploaded them
       concurrently. The server accepted both connections at the same time and wrote
       both files into the `async_exercises/uploads/` folder with timestamped names.
       The server replies indicate the saved filenames. The order in which the server
       begins receiving each file may differ from the order in which the uploads
       complete, depending on scheduling and file sizes.

Where to look for results
--------------------------

- For exercise 1: the replies are printed to the client STDOUT when each connection
   receives the server response.
- For exercise 2: uploaded files are saved under `async_exercises/uploads/`.
   Example saved filename format: `YYYYMMDD-HHMMSS_originalname.ext`.

Reproducible steps (quick)
--------------------------

1) Exercise 1, in one terminal run server:

    python -u "d:\Documents-D\VS Code\network programming\async_exercises\ex1_server.py"

    then in another terminal run client:

    python "d:\Documents-D\VS Code\network programming\async_exercises\ex1_client.py"

    Or run the single test runner which starts server and clients in-process:

    python "d:\Documents-D\VS Code\network programming\async_exercises\ex1_test.py"

2) Exercise 2, in one terminal run server:

    python -u "d:\Documents-D\VS Code\network programming\async_exercises\ex2_server.py"

    then in another terminal run client:

    python "d:\Documents-D\VS Code\network programming\async_exercises\ex2_client.py"

    Or run the combined test:

    python "d:\Documents-D\VS Code\network programming\async_exercises\ex2_test.py"

Troubleshooting
---------------

- "Address already in use" / port conflicts: another process may be using ports 8888
   (ex1) or 8889 (ex2). Stop the other process or change the PORT constants at the
   top of the corresponding files.
- Firewall / Windows permissions: allow Python through the firewall or run from
   an elevated shell if you see connection refusals.
- File paths with spaces: the test runners handle paths; if you run servers from
   a different CWD make sure `uploads/` is writable in that directory.
- Python version: examples use asyncio features available on Python 3.8+. Use
   a modern CPython (3.8, 3.9, 3.10, etc.).

Next steps / improvements
-------------------------

- Add streaming upload support and progress reporting for large files (currently
   the client reads and sends the file in chunks but the server buffers the whole
   file in memory via `read_exact` — for very large files this should be
   rewritten to stream to disk while receiving).
- Add retries and checksum verification for uploads.
- Add simple authentication (shared secret or TLS) if you plan to test over
   untrusted networks.

