import pytest
import hashlib
from app.common import build_chat, build_file_meta, build_file_chunk, build_ack, build_ping, build_pong

def test_build_chat():
    msg = build_chat("hello", "alice", "room1")
    assert msg['type'] == 'chat'
    assert msg['text'] == 'hello'
    assert msg['from'] == 'alice'
    assert msg['room'] == 'room1'
    assert 'ts' in msg
    assert 'corr_id' in msg

def test_build_file_meta():
    msg = build_file_meta("file.txt", 100, "sha256hash", "bob", "room1")
    assert msg['type'] == 'file_meta'
    assert msg['name'] == 'file.txt'
    assert msg['size'] == 100
    assert msg['sha256'] == 'sha256hash'
    assert msg['from'] == 'bob'
    assert msg['room'] == 'room1'

def test_build_file_chunk():
    msg = build_file_chunk(0, "b64data", "charlie", "room1", "corr123")
    assert msg['type'] == 'file_chunk'
    assert msg['offset'] == 0
    assert msg['bytes_b64'] == 'b64data'
    assert msg['from'] == 'charlie'
    assert msg['corr_id'] == 'corr123'

def test_build_ack():
    msg = build_ack(True, "corr123", "error msg", "dave")
    assert msg['type'] == 'ack'
    assert msg['ok'] == True
    assert msg['corr_id'] == 'corr123'
    assert msg['error'] == 'error msg'
    assert msg['from'] == 'dave'

def test_build_ping():
    msg = build_ping("eve", "room1")
    assert msg['type'] == 'ping'
    assert msg['from'] == 'eve'
    assert msg['room'] == 'room1'
    assert 'corr_id' in msg

def test_build_pong():
    msg = build_pong("frank", "room1")
    assert msg['type'] == 'pong'
    assert msg['from'] == 'frank'
    assert msg['room'] == 'room1'
    assert 'corr_id' in msg

def test_sha256():
    data = b"hello world"
    expected = "b94d27b9934d3e08a52e52d7da7dabfac484efe37a5380ee9088f7ace2efcde9"
    assert hashlib.sha256(data).hexdigest() == expected