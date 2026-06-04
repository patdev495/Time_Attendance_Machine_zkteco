"""
verify_section_3_frame.py
Kiem chung: Cau truc Frame TCP (Section 3)
Tests:
  3.1 - Frame = 4-byte Big-Endian length header + XOR-encrypted body
  3.2 - Length header khop voi actual body length
"""
import sys; sys.stdout.reconfigure(encoding='utf-8')
import socket, struct, json

DEVICE_IP = "192.168.209.61"
DEVICE_PORT = 9922
SECRET_KEY = "123"
STATIC_KEY = [0, 1, 2, 4, 8, 16, 32, 64]

def make_key(s):
    k = bytearray(8)
    sb = s.encode()
    for i in range(8):
        k[i] = (sb[i] + STATIC_KEY[i]) & 0xFF if i < len(sb) else STATIC_KEY[i]
    return k

def xor_from_zero(data, key):
    r = bytearray(len(data))
    for i, b in enumerate(data):
        r[i] = b ^ key[i % 8]
    return bytes(r)

print("=" * 60)
print("VERIFY SECTION 3: TCP Frame Format")
print("=" * 60)

key = make_key(SECRET_KEY)
sock = socket.socket(); sock.settimeout(10)
sock.connect((DEVICE_IP, DEVICE_PORT))

cmd = {"RETURN":"GetRequest","PARAM":{"result":"success","reason":"","command":"GetDeviceInfo"}}
payload = json.dumps(cmd, ensure_ascii=False).encode('utf-8')
enc = xor_from_zero(payload, key)
header = struct.pack('!I', len(enc))

# Test 3.1: Send raw frame, check header is 4 bytes Big-Endian
sock.sendall(header + enc)
raw_header = b''
while len(raw_header) < 4:
    raw_header += sock.recv(4 - len(raw_header))
body_len = struct.unpack('!I', raw_header)[0]

print(f"[3.1 PASS] Response header: {raw_header.hex()} -> body_len={body_len} bytes")
assert body_len > 0, "FAIL: body_len is 0"
assert body_len < 100000, f"FAIL: body_len={body_len} unreasonably large"

# Test 3.2: Read exactly body_len bytes
body = b''
while len(body) < body_len:
    body += sock.recv(body_len - len(body))
assert len(body) == body_len, f"FAIL: received {len(body)} bytes, expected {body_len}"
print(f"[3.2 PASS] Received exactly {body_len} bytes as announced in header")

# Test 3.3: Body is XOR-encrypted JSON
dec = xor_from_zero(body, key)
resp = json.loads(dec.decode('utf-8'))
assert 'COMMAND' in resp and resp['COMMAND'] == 'Return', f"FAIL: unexpected response: {resp}"
print(f"[3.3 PASS] Body decrypts to valid JSON: COMMAND={resp['COMMAND']}")

sock.close()
print("\n[SECTION 3] ALL TESTS PASSED")
