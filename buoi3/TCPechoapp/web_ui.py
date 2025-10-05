from flask import Flask, render_template, request, redirect, url_for, jsonify
import subprocess
import threading
from pathlib import Path
import sys
import shlex

ROOT = Path(__file__).parent
PY = sys.executable or 'python'
app = Flask(__name__)

# Track background processes started by the web UI
processes = {}  # port -> Popen

log_lines = []

def append_log(line: str):
    log_lines.append(line)
    # keep log reasonably bounded
    if len(log_lines) > 1000:
        del log_lines[0: len(log_lines) - 1000]

@app.route('/')
def index():
    return render_template('index.html', log='\n'.join(log_lines), processes=processes)

@app.route('/start_server', methods=['POST'])
def start_server():
    port = request.form.get('port', '9093')
    mode = request.form.get('mode', 'line')
    if not port.isdigit():
        append_log(f'Invalid port: {port}')
        return redirect(url_for('index'))
    if port in processes:
        append_log(f'Server already running on port {port}')
        return redirect(url_for('index'))
    args = [PY, str(ROOT / 'server.py'), '--host', '127.0.0.1', '--port', port, '--mode', mode, '--debug']
    append_log(f'Starting server: {" ".join(args)}')
    p = subprocess.Popen(args, cwd=str(ROOT), stdout=subprocess.PIPE, stderr=subprocess.STDOUT, text=True)
    processes[port] = p
    # start reader thread
    def reader(proc, port):
        for line in proc.stdout:
            append_log(f'[server {port}] {line.rstrip()}')
    threading.Thread(target=reader, args=(p, port), daemon=True).start()
    return redirect(url_for('index'))

@app.route('/stop_server', methods=['POST'])
def stop_server():
    port = request.form.get('port', '9093')
    p = processes.get(port)
    if not p:
        append_log(f'No server tracked on port {port}')
        return redirect(url_for('index'))
    append_log(f'Stopping server on port {port} (pid={p.pid})')
    try:
        p.terminate()
        p.wait(timeout=2)
    except Exception:
        try:
            p.kill()
        except Exception:
            pass
    processes.pop(port, None)
    return redirect(url_for('index'))

@app.route('/run_client', methods=['POST'])
def run_client():
    port = request.form.get('port', '9093')
    mode = request.form.get('mode', 'line')
    text = request.form.get('text', 'Hello from web UI')
    args = [PY, str(ROOT / 'client.py'), '--host', '127.0.0.1', '--port', port, '--mode', mode, '--input', 'inline', '--text', text]
    append_log(f'Running: {" ".join(args)}')
    try:
        out = subprocess.check_output(args, cwd=str(ROOT), stderr=subprocess.STDOUT, text=True, timeout=10)
        append_log(f'[client] {out.strip()}')
    except subprocess.CalledProcessError as e:
        append_log(f'[client error] {e.output}')
    except Exception as e:
        append_log(f'[client exception] {e}')
    return redirect(url_for('index'))

@app.route('/run_invalid_utf8', methods=['POST'])
def run_invalid_utf8():
    port = request.form.get('port', '9093')
    code = "import socket; s=socket.create_connection(('127.0.0.1', %s)); s.sendall(b'\\xff\\xfe\\xff\\n'); print(repr(s.recv(1024))); s.close()" % port
    args = [PY, '-c', code]
    append_log(f'Running invalid-utf8 against port {port}')
    try:
        out = subprocess.check_output(args, cwd=str(ROOT), stderr=subprocess.STDOUT, text=True, timeout=10)
        append_log(f'[invalid] {out.strip()}')
    except Exception as e:
        append_log(f'[invalid exception] {e}')
    return redirect(url_for('index'))

@app.route('/run_length_tests', methods=['POST'])
def run_length_tests():
    args = [PY, str(ROOT / 'tests' / 'test_length_prefixed.py')]
    append_log('Running length-prefixed tests')
    try:
        out = subprocess.check_output(args, cwd=str(ROOT), stderr=subprocess.STDOUT, text=True, timeout=20)
        append_log(f'[length tests]\n{out}')
    except Exception as e:
        append_log(f'[length tests exception] {e}')
    return redirect(url_for('index'))

@app.route('/run_invalid_test_script', methods=['POST'])
def run_invalid_test_script():
    args = [PY, str(ROOT / 'tests' / 'test_invalid_utf8.py')]
    append_log('Running invalid-utf8 test script')
    try:
        out = subprocess.check_output(args, cwd=str(ROOT), stderr=subprocess.STDOUT, text=True, timeout=20)
        append_log(f'[invalid test]\n{out}')
    except subprocess.CalledProcessError as e:
        # script exits with code 41 for Unicode issues; capture output
        append_log(f'[invalid test (non-zero)] exit={e.returncode} output=\n{e.output}')
    except Exception as e:
        append_log(f'[invalid test exception] {e}')
    return redirect(url_for('index'))

@app.route('/status')
def status():
    return jsonify({ 'processes': list(processes.keys()), 'log_tail': log_lines[-200:] })

if __name__ == '__main__':
    app.run(debug=False, host='127.0.0.1', port=5000)
