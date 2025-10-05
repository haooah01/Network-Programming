"""
Simple Tkinter control panel for the TCP echo app.

Features:
- Start/Stop servers (line or len) on a chosen port.
- Run client with inline text and show output.
- Run provided tests (invalid UTF-8 and length-prefixed tests) and show output.

Usage:
    python gui.py

This is intentionally lightweight and uses subprocesses to control the existing scripts in the repo.
"""

import sys
import os
import threading
import subprocess
import shlex
import time
from pathlib import Path
import tkinter as tk
from tkinter import ttk, scrolledtext, messagebox

ROOT = Path(__file__).parent
PY = sys.executable or "python"

class ProcessEntry:
    def __init__(self, popen: subprocess.Popen, desc: str):
        self.popen = popen
        self.desc = desc
        self.output_thread = None

class App(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("TCP Echo Control Panel")
        self.geometry("900x600")
        self.processes = {}  # port -> ProcessEntry
        self._build()

    def _build(self):
        frm = ttk.Frame(self)
        frm.pack(fill=tk.BOTH, expand=True, padx=8, pady=8)

        # Controls frame
        ctl = ttk.LabelFrame(frm, text="Controls")
        ctl.pack(fill=tk.X, pady=4)

        ttk.Label(ctl, text="Port:").grid(row=0, column=0, sticky=tk.W)
        self.port_var = tk.StringVar(value="9093")
        self.port_entry = ttk.Entry(ctl, width=8, textvariable=self.port_var)
        self.port_entry.grid(row=0, column=1, sticky=tk.W, padx=4)

        ttk.Label(ctl, text="Mode:").grid(row=0, column=2, sticky=tk.W, padx=(8,0))
        self.mode_var = tk.StringVar(value="line")
        mode_menu = ttk.OptionMenu(ctl, self.mode_var, "line", "line", "len")
        mode_menu.grid(row=0, column=3, sticky=tk.W)

        start_btn = ttk.Button(ctl, text="Start Server", command=self.start_server)
        start_btn.grid(row=0, column=4, padx=8)
        stop_btn = ttk.Button(ctl, text="Stop Server", command=self.stop_server)
        stop_btn.grid(row=0, column=5, padx=4)
        stop_all_btn = ttk.Button(ctl, text="Stop All Servers", command=self.stop_all)
        stop_all_btn.grid(row=0, column=6, padx=4)

        # Client controls
        client_fr = ttk.LabelFrame(frm, text="Client")
        client_fr.pack(fill=tk.X, pady=4)
        ttk.Label(client_fr, text="Text:").grid(row=0, column=0, sticky=tk.W)
        self.client_text = tk.StringVar(value="Hello from GUI")
        ttk.Entry(client_fr, width=60, textvariable=self.client_text).grid(row=0, column=1, sticky=tk.W, padx=4)
        send_btn = ttk.Button(client_fr, text="Run Client", command=self.run_client)
        send_btn.grid(row=0, column=2, padx=8)
        send_invalid_btn = ttk.Button(client_fr, text="Send Invalid UTF-8 (line)", command=self.run_invalid_utf8)
        send_invalid_btn.grid(row=0, column=3, padx=4)

        # Tests
        test_fr = ttk.LabelFrame(frm, text="Tests")
        test_fr.pack(fill=tk.X, pady=4)
        test1_btn = ttk.Button(test_fr, text="Run length-prefixed tests", command=self.run_length_tests)
        test1_btn.grid(row=0, column=0, padx=4)
        test2_btn = ttk.Button(test_fr, text="Run invalid-utf8 test", command=self.run_invalid_test_script)
        test2_btn.grid(row=0, column=1, padx=4)

        # Status / logs
        log_fr = ttk.LabelFrame(frm, text="Log")
        log_fr.pack(fill=tk.BOTH, expand=True, pady=4)
        self.log = scrolledtext.ScrolledText(log_fr, wrap=tk.NONE)
        self.log.pack(fill=tk.BOTH, expand=True)

        # Footer
        footer = ttk.Frame(frm)
        footer.pack(fill=tk.X, pady=(4,0))
        self.status_var = tk.StringVar(value="Idle")
        ttk.Label(footer, textvariable=self.status_var).pack(side=tk.LEFT)

    def append_log(self, text: str):
        def _append():
            self.log.insert(tk.END, text + "\n")
            self.log.see(tk.END)
        self.after(0, _append)

    def _start_process(self, args, port=None, desc=None):
        self.append_log(f"Starting: {' '.join(args)}")
        try:
            p = subprocess.Popen(args, cwd=str(ROOT), stdout=subprocess.PIPE, stderr=subprocess.STDOUT, bufsize=1, text=True)
        except Exception as exc:
            messagebox.showerror("Start failed", str(exc))
            return None
        entry = ProcessEntry(popen=p, desc=desc or ' '.join(args))
        if port:
            self.processes[str(port)] = entry
        # start thread to read stdout
        def reader():
            try:
                for line in p.stdout:
                    self.append_log(f"[{desc or 'proc'} {p.pid}] {line.rstrip()}")
            except Exception:
                pass
        t = threading.Thread(target=reader, daemon=True)
        entry.output_thread = t
        t.start()
        return entry

    def start_server(self):
        port = self.port_var.get().strip()
        mode = self.mode_var.get().strip()
        if not port.isdigit():
            messagebox.showwarning("Invalid port", "Port must be numeric")
            return
        args = [PY, str(ROOT / 'server.py'), '--host', '127.0.0.1', '--port', port, '--mode', mode, '--debug']
        desc = f"server:{mode}:{port}"
        entry = self._start_process(args, port=port, desc=desc)
        if entry:
            self.status_var.set(f"Started server PID={entry.popen.pid} on {port} ({mode})")

    def stop_server(self):
        port = self.port_var.get().strip()
        entry = self.processes.get(port)
        if not entry:
            messagebox.showinfo("Not found", f"No server tracked on port {port}")
            return
        p = entry.popen
        self.append_log(f"Stopping PID={p.pid}")
        try:
            p.terminate()
            try:
                p.wait(timeout=2)
            except subprocess.TimeoutExpired:
                p.kill()
        except Exception as exc:
            self.append_log(f"Error stopping: {exc}")
        finally:
            self.processes.pop(port, None)
            self.status_var.set("Idle")

    def stop_all(self):
        for port, entry in list(self.processes.items()):
            try:
                self.append_log(f"Stopping PID={entry.popen.pid} (port {port})")
                entry.popen.terminate()
                entry.popen.wait(timeout=1)
            except Exception:
                try:
                    entry.popen.kill()
                except Exception:
                    pass
            self.processes.pop(port, None)
        self.status_var.set('Idle')

    def run_client(self):
        port = self.port_var.get().strip()
        text = self.client_text.get()
        args = [PY, str(ROOT / 'client.py'), '--host', '127.0.0.1', '--port', port, '--mode', self.mode_var.get(), '--input', 'inline', '--text', text]
        self._run_short_process(args, label='client')

    def run_invalid_utf8(self):
        # send invalid UTF-8 using a short inline script to avoid adding files
        port = self.port_var.get().strip()
        code = (
            "import socket; s=socket.create_connection(('127.0.0.1', %s)); s.sendall(b'\\xff\\xfe\\xff\\n'); "
            "data=s.recv(1024); print(repr(data)); s.close()" % port
        )
        args = [PY, '-c', code]
        self._run_short_process(args, label='invalid-utf8')

    def run_invalid_test_script(self):
        args = [PY, str(ROOT / 'tests' / 'test_invalid_utf8.py')]
        self._run_short_process(args, label='test-invalid-script')

    def run_length_tests(self):
        args = [PY, str(ROOT / 'tests' / 'test_length_prefixed.py')]
        self._run_short_process(args, label='length-tests')

    def _run_short_process(self, args, label=None):
        self.append_log(f"Running: {' '.join(args)}")
        try:
            proc = subprocess.Popen(args, cwd=str(ROOT), stdout=subprocess.PIPE, stderr=subprocess.STDOUT, text=True)
        except Exception as exc:
            messagebox.showerror('Run failed', str(exc))
            return
        def reader():
            try:
                for line in proc.stdout:
                    self.append_log(f"[{label or 'proc'} {proc.pid}] {line.rstrip()}")
                proc.wait()
                self.append_log(f"[{label or 'proc'} {proc.pid}] exited {proc.returncode}")
            except Exception as exc:
                self.append_log(f"Reader error: {exc}")
        threading.Thread(target=reader, daemon=True).start()

if __name__ == '__main__':
    app = App()
    app.mainloop()
