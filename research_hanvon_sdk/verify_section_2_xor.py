"""
verify_section_2_xor.py
Kiem chung: Giai thuat ma hoa XOR (Xor64Codec) - Section 2
Tests:
  2.1 - Sinh khoa dong (DerivedKey) tu SecretKey
  2.2 - Hanh vi XOR: ca TX va RX deu reset ve 0 sau moi transaction
"""
import sys; sys.stdout.reconfigure(encoding='utf-8')
import socket, struct, json

DEVICE_IP = "192.168.209.61"
DEVICE_PORT = 9922
SECRET_KEY = "123"
STATIC_KEY = [0, 1, 2, 4, 8, 16, 32, 64]
EXPECTED_DERIVED_KEY = [0x31, 0x33, 0x35, 0x04, 0x08, 0x10, 0x20, 0x40]

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
    return json.loads(xor_from_zero(body, key).decode('utf-8')), body

print("=" * 60)
print("VERIFY SECTION 2: XOR Codec")
print("=" * 60)

# Test 2.1: DerivedKey generation
key = make_key(SECRET_KEY)
assert list(key) == EXPECTED_DERIVED_KEY, f"FAIL: DerivedKey mismatch: {list(key)}"
print(f"[2.1 PASS] DerivedKey correct: {[hex(b) for b in key]}")

# Test 2.2: TX and RX both reset to 0 per transaction
sock = socket.socket(); sock.settimeout(10)
sock.connect((DEVICE_IP, DEVICE_PORT))
cmd = {"RETURN":"GetRequest","PARAM":{"result":"success","reason":"","command":"GetDeviceInfo"}}

resp1, body1 = send_command(sock, cmd, key)
resp2, body2 = send_command(sock, cmd, key)
resp3, body3 = send_command(sock, cmd, key)

# Key assertion: body bytes identical across all 3 responses = RX resets to 0 each time
assert body1[:20] == body2[:20] == body3[:20], f"FAIL: body bytes differ -> RX is NOT resetting"
print(f"[2.2 PASS] RX resets to 0 each transaction. body[:20]={body1[:20].hex()}")
assert resp1['PARAM']['result'] == 'success'
assert resp2['PARAM']['result'] == 'success'
assert resp3['PARAM']['result'] == 'success'
print(f"[2.2 PASS] 3 consecutive commands on same TCP conn all succeeded")

sock.close()
print("\n[SECTION 2] ALL TESTS PASSED")
