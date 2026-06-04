"""
verify_section_4_handshake.py
Kiem chung: Giao thuc Handshake & GetDeviceInfo (Section 4)
Tests:
  4.1 - GetDeviceInfo tra ve result=success
  4.2 - Response co day du cac truong bat buoc
  4.3 - real_facerecord <= max_facerecord
  4.4 - model va sn khong rong
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

def send_command(sock, cmd, key):
    payload = json.dumps(cmd, ensure_ascii=False).encode('utf-8')
    enc = xor_from_zero(payload, key)
    sock.sendall(struct.pack('!I', len(enc)) + enc)
    h = b''
    while len(h) < 4: h += sock.recv(4 - len(h))
    n = struct.unpack('!I', h)[0]
    body = b''
    while len(body) < n: body += sock.recv(n - len(body))
    return json.loads(xor_from_zero(body, key).decode('utf-8'))

print("=" * 60)
print("VERIFY SECTION 4: Handshake & GetDeviceInfo")
print("=" * 60)

key = make_key(SECRET_KEY)
sock = socket.socket(); sock.settimeout(10)
sock.connect((DEVICE_IP, DEVICE_PORT))

cmd = {"RETURN":"GetRequest","PARAM":{"result":"success","reason":"","command":"GetDeviceInfo"}}
resp = send_command(sock, cmd, key)

# Test 4.1
assert resp.get('PARAM', {}).get('result') == 'success', f"FAIL: result={resp.get('PARAM',{}).get('result')}"
print(f"[4.1 PASS] GetDeviceInfo result=success")

info = resp['PARAM']['deviceInfo']

# Test 4.2 - required fields
required = ['model', 'sn', 'time', 'real_facerecord', 'max_facerecord']
for f in required:
    assert f in info, f"FAIL: missing field '{f}' in deviceInfo"
print(f"[4.2 PASS] All required fields present: {required}")

# Test 4.3
assert int(info['real_facerecord']) <= int(info['max_facerecord']), "FAIL: real_facerecord > max_facerecord"
print(f"[4.3 PASS] real_facerecord={info['real_facerecord']} <= max_facerecord={info['max_facerecord']}")

# Test 4.4
assert info['model'], "FAIL: model is empty"
assert info['sn'], "FAIL: sn is empty"
print(f"[4.4 PASS] model='{info['model']}', sn='{info['sn']}'")

sock.close()
print(f"\nDevice info:")
for k, v in info.items():
    if not isinstance(v, (list, dict)):
        print(f"  {k}: {v}")
print("\n[SECTION 4] ALL TESTS PASSED")
