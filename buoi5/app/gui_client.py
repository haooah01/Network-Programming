import tkinter as tk
from tkinter import filedialog, messagebox, scrolledtext, ttk
import socket
import threading
import queue
from common import send_msg, recv_msg, build_chat, build_file_meta, build_file_chunk, build_ack
import os
import hashlib
import base64
import logging
from sync_server import main as sync_server_main

MAX_CHUNK_BYTES = 65536

class CaptureStdout:
    def __init__(self, queue):
        self.queue = queue

    def write(self, text):
        if text.strip():
            self.queue.put(text.strip())

    def flush(self):
        pass

class ChatAppGUI:
    def __init__(self, root):
        self.root = root
        self.root.title("SyncAsync Chat & File Transfer")
        self.root.geometry("1200x600")

        # Paned window for split layout
        self.paned = tk.PanedWindow(self.root, orient=tk.HORIZONTAL)
        self.paned.pack(fill=tk.BOTH, expand=True)

        self.left_frame = tk.Frame(self.paned)
        self.paned.add(self.left_frame, minsize=800)

        self.right_frame = tk.Frame(self.paned)
        self.paned.add(self.right_frame, minsize=400)

        # Variables
        self.sock = None
        self.connected = False
        self.server_thread = None
        self.server_running = False
        self.message_queue = queue.Queue()
        self.log_queue = queue.Queue()
        self.progress_var = tk.DoubleVar()
        self.sock_lock = threading.Lock()
        self.canvas = None
        self.file_icon = None

        # Setup logging for server
        self.setup_logging()

        # GUI Elements
        self.create_widgets()
        self.refresh_files()
        self.root.after(100, self.check_queues)

    def setup_logging(self):
        self.logger = logging.getLogger('server')
        self.logger.setLevel(logging.INFO)
        handler = logging.StreamHandler()
        handler.setLevel(logging.INFO)
        formatter = logging.Formatter('%(asctime)s - %(message)s')
        handler.setFormatter(formatter)
        self.logger.addHandler(handler)

        # Also add queue handler for GUI
        queue_handler = logging.Handler()
        queue_handler.emit = lambda record: self.log_queue.put(self.format_log(record))
        self.logger.addHandler(queue_handler)

    def format_log(self, record):
        return f"{record.levelname}: {record.getMessage()}"

    def create_widgets(self):
        # Server frame
        server_frame = tk.LabelFrame(self.left_frame, text="Server Control", padx=10, pady=10)
        server_frame.pack(fill=tk.X, padx=10, pady=5)

        tk.Label(server_frame, text="Host:").grid(row=0, column=0)
        self.server_host_entry = tk.Entry(server_frame)
        self.server_host_entry.insert(0, "0.0.0.0")
        self.server_host_entry.grid(row=0, column=1)

        tk.Label(server_frame, text="Port:").grid(row=0, column=2)
        self.server_port_entry = tk.Entry(server_frame)
        self.server_port_entry.insert(0, "5050")
        self.server_port_entry.grid(row=0, column=3)

        self.start_server_btn = tk.Button(server_frame, text="Start Server", command=self.start_server)
        self.start_server_btn.grid(row=0, column=4, padx=5)

        self.stop_server_btn = tk.Button(server_frame, text="Stop Server", command=self.stop_server, state=tk.DISABLED)
        self.stop_server_btn.grid(row=0, column=5)

        self.server_log_text = scrolledtext.ScrolledText(server_frame, height=5, state=tk.DISABLED)
        self.server_log_text.grid(row=1, column=0, columnspan=6, pady=5, sticky="ew")

        # Client frame
        client_frame = tk.LabelFrame(self.left_frame, text="Client Chat", padx=10, pady=10)
        client_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=5)

        # Connection
        conn_frame = tk.Frame(client_frame)
        conn_frame.pack(fill=tk.X)

        tk.Label(conn_frame, text="Host:").grid(row=0, column=0)
        self.host_entry = tk.Entry(conn_frame)
        self.host_entry.insert(0, "127.0.0.1")
        self.host_entry.grid(row=0, column=1)

        tk.Label(conn_frame, text="Port:").grid(row=0, column=2)
        self.port_entry = tk.Entry(conn_frame)
        self.port_entry.insert(0, "5050")
        self.port_entry.grid(row=0, column=3)

        tk.Label(conn_frame, text="Name:").grid(row=0, column=4)
        self.name_entry = tk.Entry(conn_frame)
        self.name_entry.insert(0, "user")
        self.name_entry.grid(row=0, column=5)

        self.connect_btn = tk.Button(conn_frame, text="Connect", command=self.connect)
        self.connect_btn.grid(row=0, column=6, padx=10)

        self.disconnect_btn = tk.Button(conn_frame, text="Disconnect", command=self.disconnect, state=tk.DISABLED)
        self.disconnect_btn.grid(row=0, column=7)

        # Chat
        self.chat_text = scrolledtext.ScrolledText(client_frame, height=10, state=tk.DISABLED)
        self.chat_text.pack(fill=tk.BOTH, expand=True, pady=5)

        # Message
        msg_frame = tk.Frame(client_frame)
        msg_frame.pack(fill=tk.X)

        self.msg_entry = tk.Entry(msg_frame)
        self.msg_entry.pack(side=tk.LEFT, fill=tk.X, expand=True)
        self.msg_entry.bind("<Return>", lambda e: self.send_message())

        self.send_btn = tk.Button(msg_frame, text="Send", command=self.send_message, state=tk.DISABLED)
        self.send_btn.pack(side=tk.RIGHT)

        # File
        file_frame = tk.Frame(client_frame)
        file_frame.pack(fill=tk.X, pady=5)

        self.file_btn = tk.Button(file_frame, text="Send File", command=self.send_file, state=tk.DISABLED)
        self.file_btn.pack(side=tk.LEFT)

        self.progress_bar = ttk.Progressbar(file_frame, variable=self.progress_var, maximum=100)
        self.progress_bar.pack(fill=tk.X, pady=5)

        self.quit_btn = tk.Button(file_frame, text="Quit", command=self.quit_app)
        self.quit_btn.pack(side=tk.RIGHT)

        # Received files
        files_frame = tk.LabelFrame(self.left_frame, text="Received Files", padx=10, pady=10)
        files_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=5)

        self.files_listbox = tk.Listbox(files_frame)
        self.files_listbox.pack(fill=tk.BOTH, expand=True)
        self.files_listbox.bind('<Double-1>', self.open_file)

        self.refresh_files_btn = tk.Button(files_frame, text="Refresh Files", command=self.refresh_files)
        self.refresh_files_btn.pack()

        # Animation canvas
        anim_frame = tk.LabelFrame(self.right_frame, text="File Transfer Animation", padx=10, pady=10)
        anim_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=5)

        self.canvas = tk.Canvas(anim_frame, bg='white')
        self.canvas.pack(fill=tk.BOTH, expand=True)
        self.canvas.bind('<Configure>', self.on_canvas_resize)

        self.test_btn = tk.Button(anim_frame, text="Test Animation", command=self.test_animation)
        self.test_btn.pack()

        # Initial draw
        self.cx = 200
        self.h = 600
        self.current_progress = 0
        self.redraw_canvas()

    def start_server(self):
        if self.server_running:
            return
        try:
            host = self.server_host_entry.get()
            port = int(self.server_port_entry.get())
            self.server_thread = threading.Thread(target=self.run_server, args=(host, port), daemon=True)
            self.server_thread.start()
            self.server_running = True
            self.start_server_btn.config(state=tk.DISABLED)
            self.stop_server_btn.config(state=tk.NORMAL)
            self.log_server("Server started")
        except Exception as e:
            messagebox.showerror("Server Error", str(e))

    def run_server(self, host, port):
        # Redirect prints to log
        import sys
        old_stdout = sys.stdout
        sys.stdout = CaptureStdout(self.log_queue)
        try:
            sync_server_main(host, port)
        except Exception as e:
            self.log_queue.put(f"Server error: {e}")
        finally:
            sys.stdout = old_stdout
            self.server_running = False
            self.root.after(0, lambda: self.start_server_btn.config(state=tk.NORMAL))
            self.root.after(0, lambda: self.stop_server_btn.config(state=tk.DISABLED))

    def stop_server(self):
        # Stopping server is tricky, for now just set flag
        self.server_running = False
        self.log_server("Server stop requested")

    def log_server(self, msg):
        self.server_log_text.config(state=tk.NORMAL)
        self.server_log_text.insert(tk.END, msg + "\n")
        self.server_log_text.see(tk.END)
        self.server_log_text.config(state=tk.DISABLED)

    def connect(self):
        try:
            host = self.host_entry.get()
            port = int(self.port_entry.get())
            name = self.name_entry.get()

            self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self.sock.connect((host, port))
            self.connected = True

            self.log_message(f"Connected to {host}:{port} as {name}")

            self.connect_btn.config(state=tk.DISABLED)
            self.disconnect_btn.config(state=tk.NORMAL)
            self.send_btn.config(state=tk.NORMAL)
            self.file_btn.config(state=tk.NORMAL)

            # Start reader thread
            threading.Thread(target=self.reader_thread, args=(name,), daemon=True).start()

        except Exception as e:
            messagebox.showerror("Connection Error", str(e))

    def disconnect(self):
        if self.sock:
            self.sock.close()
        self.connected = False
        self.connect_btn.config(state=tk.NORMAL)
        self.disconnect_btn.config(state=tk.DISABLED)
        self.send_btn.config(state=tk.DISABLED)
        self.file_btn.config(state=tk.DISABLED)
        self.log_message("Disconnected")

    def send_message(self):
        if not self.connected:
            return
        msg_text = self.msg_entry.get().strip()
        if msg_text:
            try:
                name = self.name_entry.get()
                msg = build_chat(msg_text, name)
                with self.sock_lock:
                    send_msg(self.sock, msg)
                self.msg_entry.delete(0, tk.END)
                self.log_message(f"You: {msg_text}")
                self.animate_message()
            except Exception as e:
                self.log_message(f"Send error: {e}")

    def send_file(self):
        if not self.connected:
            return
        filepath = filedialog.askopenfilename()
        if filepath:
            self.progress_var.set(0)
            self.create_file_icon()
            threading.Thread(target=self.send_file_thread, args=(filepath,), daemon=True).start()

    def send_file_thread(self, filepath):
        try:
            filename = os.path.basename(filepath)
            size = os.path.getsize(filepath)
            with open(filepath, 'rb') as f:
                data = f.read()
            sha256 = hashlib.sha256(data).hexdigest()

            name = self.name_entry.get()
            meta = build_file_meta(filename, size, sha256, name)
            with self.sock_lock:
                send_msg(self.sock, meta)

            self.message_queue.put(f"Starting to send {filename} ({size} bytes)")

            # Wait for ACK
            ack = recv_msg(self.sock)
            if not ack.get('ok', False):
                self.message_queue.put(f"File send failed: {ack.get('error', 'Unknown')}")
                return

            # Send chunks
            offset = 0
            while offset < size:
                chunk = data[offset:offset + MAX_CHUNK_BYTES]
                chunk_b64 = base64.b64encode(chunk).decode('ascii')
                chunk_msg = build_file_chunk(offset, chunk_b64, name, 'default', meta['corr_id'])
                with self.sock_lock:
                    send_msg(self.sock, chunk_msg)
                offset += len(chunk)
                progress = (offset / size) * 100
                self.root.after(0, lambda p=progress: (self.progress_var.set(p), self.update_file_icon(p)))
                import time
                time.sleep(0.001)  # Small delay to avoid overwhelming the socket

            # Wait for final ACK
            final_ack = recv_msg(self.sock)
            if final_ack.get('ok', False):
                self.message_queue.put(f"File {filename} sent successfully")
                self.root.after(0, lambda: (self.progress_var.set(100), self.update_file_icon(100)))
                self.root.after(1000, lambda: (self.canvas.itemconfig(self.progress_text, text="Sent successfully"), self.canvas.after(1000, lambda: (self.canvas.delete(self.file_icon), self.canvas.itemconfig(self.progress_text, text="")))))
            else:
                self.message_queue.put(f"File send failed: {final_ack.get('error', 'Unknown')}")
                self.root.after(0, lambda: (self.canvas.itemconfig(self.progress_text, text="Send failed"), self.canvas.after(1000, lambda: (self.canvas.delete(self.file_icon), self.canvas.itemconfig(self.progress_text, text="")))))

        except Exception as e:
            self.message_queue.put(f"File send error: {e}")

    def reader_thread(self, name):
        while self.connected:
            try:
                msg = recv_msg(self.sock)
                if msg['type'] == 'chat':
                    self.message_queue.put(f"[{msg['from']}]: {msg['text']}")
                elif msg['type'] == 'ack':
                    self.message_queue.put(f"ACK: {msg}")
                elif msg['type'] == 'pong':
                    pass  # Heartbeat
                else:
                    self.message_queue.put(f"Received: {msg}")
            except Exception as e:
                if self.connected:
                    self.message_queue.put(f"Read error: {e}")
                break

    def check_queues(self):
        # Check message queue
        try:
            while True:
                msg = self.message_queue.get_nowait()
                self.log_message(msg)
        except queue.Empty:
            pass

        # Check log queue
        try:
            while True:
                log = self.log_queue.get_nowait()
                self.log_server(log)
        except queue.Empty:
            pass

        self.root.after(100, self.check_queues)

    def log_message(self, msg):
        self.chat_text.config(state=tk.NORMAL)
        self.chat_text.insert(tk.END, msg + "\n")
        self.chat_text.see(tk.END)
        self.chat_text.config(state=tk.DISABLED)

    def quit_app(self):
        self.disconnect()
        self.stop_server()
        self.root.quit()

    def refresh_files(self):
        self.files_listbox.delete(0, tk.END)
        try:
            files = [f for f in os.listdir('.') if os.path.isfile(f) and not f.endswith(('.py', '.pyc', '.md', '.txt'))]  # exclude code and text files
            for f in files:
                self.files_listbox.insert(tk.END, f)
        except Exception as e:
            self.log_message(f"Error refreshing files: {e}")

    def open_file(self, event):
        selection = self.files_listbox.curselection()
        if selection:
            filename = self.files_listbox.get(selection[0])
            try:
                os.startfile(filename)
            except Exception as e:
                self.log_message(f"Error opening file: {e}")

    def on_canvas_resize(self, event):
        self.cx = self.canvas.winfo_width() // 2
        self.h = self.canvas.winfo_height()
        self.redraw_canvas()

    def redraw_canvas(self):
        self.canvas.delete("all")
        self.client_text = self.canvas.create_text(self.cx, 20, text="Client", font=("Arial", 12))
        self.server_text = self.canvas.create_text(self.cx, self.h-20, text="Server", font=("Arial", 12))
        self.line = self.canvas.create_line(self.cx, 40, self.cx, self.h-40, arrow=tk.LAST)
        self.progress_text = self.canvas.create_text(self.cx, self.h//2, text="", font=("Arial", 12))
        if self.file_icon:
            y = 50 + (self.current_progress / 100) * (self.h - 100)
            self.file_icon = self.canvas.create_oval(self.cx-10, y-10, self.cx+10, y+10, fill='blue')

    def create_file_icon(self):
        self.current_progress = 0
        self.redraw_canvas()
        self.canvas.itemconfig(self.progress_text, text="Starting send")

    def update_file_icon(self, progress):
        self.current_progress = progress
        self.log_message(f"Updating icon to {progress:.1f}%")
        if self.file_icon:
            y = 50 + (progress / 100) * (self.h - 100)
            self.canvas.coords(self.file_icon, self.cx-10, y-10, self.cx+10, y+10)
            self.canvas.itemconfig(self.progress_text, text=f"Sending: {progress:.1f}%")

    def test_animation(self):
        self.create_file_icon()
        for p in range(0, 101, 10):
            self.root.after(p * 100, lambda p=p: self.update_file_icon(p))
        self.root.after(1100, lambda: self.canvas.itemconfig(self.progress_text, text="Test done"))

    def animate_message(self):
        msg_icon = self.canvas.create_oval(self.cx-5, 60, self.cx+5, 70, fill='red')
        steps = 20
        for i in range(steps + 1):
            y = 60 + (i / steps) * (self.h - 110)
            self.root.after(i * 50, lambda y=y, icon=msg_icon: self.canvas.coords(icon, self.cx-5, y-5, self.cx+5, y+5))
        self.root.after((steps + 1) * 50 + 100, lambda icon=msg_icon: self.canvas.delete(icon))

if __name__ == '__main__':
    root = tk.Tk()
    app = ChatAppGUI(root)
    root.mainloop()