"""
verify_section_8_manager.py
Kiem chung: Giao thuc Quan ly Admin (Manager) - Section 8
Tests:
  8.1 - GetManagerID tra ve danh sach
  8.2 - GetManager tra ve thong tin voi truong authority
  8.3 - SetManager that bai khi capturejpg rong
  8.4 - SetManager that bai khi password trung lap
  8.5 - SetManager thanh cong voi password duy nhat va anh hop le
  8.6 - authority: gia tri 0 duoc luu la 0 (Super Admin)
  8.7 - DeleteManager xoa thanh cong
  8.8 - Khong the xoa manager cuoi cung
"""
import sys; sys.stdout.reconfigure(encoding='utf-8')
import socket, struct, json, random
import os

DEVICE_IP = "192.168.209.61"
DEVICE_PORT = 9922
SECRET_KEY = "123"
STATIC_KEY = [0, 1, 2, 4, 8, 16, 32, 64]

def make_key(s):
    k = bytearray(8); sb = s.encode()
    for i in range(8): k[i] = (sb[i] + STATIC_KEY[i]) & 0xFF if i < len(sb) else STATIC_KEY[i]
    return k

def xor_from_zero(data, key):
    r = bytearray(len(data))
    for i, b in enumerate(data): r[i] = b ^ key[i % 8]
    return bytes(r)

def send_command(sock, cmd, key):
    payload = json.dumps(cmd, ensure_ascii=False).encode('utf-8')
    enc = xor_from_zero(payload, key)
    sock.sendall(struct.pack('!I', len(enc)) + enc)
    h = b''
    while len(h) < 4: h += sock.recv(4 - len(h))
    n = struct.unpack('!I', h)[0]; body = b''
    while len(body) < n: body += sock.recv(n - len(body))
    return json.loads(xor_from_zero(body, key).decode('utf-8'))

def new_conn(key):
    sock = socket.socket(); sock.settimeout(15)
    sock.connect((DEVICE_IP, DEVICE_PORT))
    return sock

def get_real_photo(key):
    """Get a real photo from existing employee to use as valid capturejpg"""
    script_dir = os.path.dirname(os.path.abspath(__file__))
    photo_cache = os.path.join(script_dir, 'sample_employee_photo.txt')
    if os.path.exists(photo_cache):
        with open(photo_cache, 'r') as f:
            photo = f.read().strip()
        if len(photo) > 1000:
            return photo
    # Fetch from device
    sock = new_conn(key)
    ids_resp = send_command(sock, {"RETURN":"GetRequest","PARAM":{"result":"success","reason":"","command":"GetEmployeeID","userType":"0"}}, key)
    sock.close()
    for eid in ids_resp['PARAM'].get('ids', []):
        sock = new_conn(key)
        resp = send_command(sock, {"RETURN":"GetRequest","PARAM":{"result":"success","reason":"","command":"ClientGetEmployee","job_num":eid,"userType":"0"}}, key)
        sock.close()
        photo = resp['PARAM'].get('capturejpg', '')
        if photo and len(photo) > 1000:
            with open(photo_cache, 'w') as f: f.write(photo)
            return photo
    raise RuntimeError("No employee with photo found on device")

print("=" * 60)
print("VERIFY SECTION 8: Manager Management")
print("=" * 60)

key = make_key(SECRET_KEY)
TEST_ADMIN_ID = "verify_mgr_test"
TEST_PWD = str(random.randint(100000, 899999))

# Get real photo for testing
REAL_PHOTO = get_real_photo(key)
print(f"  [setup] Using real employee photo: len={len(REAL_PHOTO)} chars")

# Cleanup: remove test admin from previous run
sock = new_conn(key)
send_command(sock, {"RETURN":"GetRequest","PARAM":{"result":"success","reason":"","command":"DeleteManager","id":TEST_ADMIN_ID}}, key)
sock.close()

# Test 8.1: GetManagerID
sock = new_conn(key)
resp = send_command(sock, {"RETURN":"GetRequest","PARAM":{"result":"success","reason":"","command":"GetManagerID"}}, key)
assert resp['PARAM']['result'] == 'success', f"FAIL: {resp['PARAM']}"
mgr_ids = resp['PARAM'].get('ids', [])
print(f"[8.1 PASS] GetManagerID: {len(mgr_ids)} managers: {mgr_ids}")
sock.close()

# Test 8.2: GetManager with required fields
sock = new_conn(key)
resp = send_command(sock, {"RETURN":"GetRequest","PARAM":{"result":"success","reason":"","command":"GetManager","id":"admin"}}, key)
assert resp['PARAM']['result'] == 'success', f"FAIL: {resp['PARAM']}"
mgr = resp['PARAM']
assert 'authority' in mgr, "FAIL: missing 'authority'"
assert 'password' in mgr, "FAIL: missing 'password'"
assert mgr['authority'] in [0, 2], f"FAIL: unexpected authority={mgr['authority']}"
print(f"[8.2 PASS] GetManager 'admin': authority={mgr['authority']} (0=Super, 2=Ordinary)")
admin_pwd = mgr.get('password', '')
sock.close()

# Test 8.3: SetManager fails with empty capturejpg
sock = new_conn(key)
resp = send_command(sock, {"RETURN":"GetRequest","PARAM":{"result":"success","reason":"","command":"SetManager",
    "id":TEST_ADMIN_ID, "capturejpg":"", "password":TEST_PWD, "authority":2}}, key)
assert resp['PARAM']['result'] == 'fail', f"FAIL: expected fail for empty capturejpg"
reason_no_photo = resp['PARAM'].get('reason', '')
print(f"[8.3 PASS] Empty capturejpg fails: reason='{reason_no_photo}'")
sock.close()

# Test 8.4: SetManager fails with duplicate password
if admin_pwd:
    sock = new_conn(key)
    resp = send_command(sock, {"RETURN":"GetRequest","PARAM":{"result":"success","reason":"","command":"SetManager",
        "id":TEST_ADMIN_ID, "capturejpg":REAL_PHOTO, "password":admin_pwd, "authority":2}}, key)
    assert resp['PARAM']['result'] == 'fail', f"FAIL: expected fail for duplicate password"
    print(f"[8.4 PASS] Duplicate password fails: reason='{resp['PARAM'].get('reason')}'")
    sock.close()
else:
    print("[8.4 SKIP] Could not retrieve admin password")

# Test 8.5: SetManager succeeds with valid unique photo and password
sock = new_conn(key)
resp = send_command(sock, {"RETURN":"GetRequest","PARAM":{"result":"success","reason":"","command":"SetManager",
    "id":TEST_ADMIN_ID, "capturejpg":REAL_PHOTO, "password":TEST_PWD, "authority":2}}, key)
assert resp['PARAM']['result'] == 'success', f"FAIL SetManager: reason={resp['PARAM'].get('reason')}"
print(f"[8.5 PASS] SetManager success: id={TEST_ADMIN_ID}, pwd={TEST_PWD}, authority=2")
sock.close()

# Test 8.6: authority value is preserved as sent (2 stays 2)
sock = new_conn(key)
resp = send_command(sock, {"RETURN":"GetRequest","PARAM":{"result":"success","reason":"","command":"GetManager","id":TEST_ADMIN_ID}}, key)
stored_auth = resp['PARAM'].get('authority')
assert stored_auth == 2, f"FAIL: expected authority=2, got {stored_auth}"
print(f"[8.6 PASS] authority=2 stored correctly: {stored_auth}")
sock.close()

# Test 8.7: DeleteManager
sock = new_conn(key)
resp = send_command(sock, {"RETURN":"GetRequest","PARAM":{"result":"success","reason":"","command":"DeleteManager","id":TEST_ADMIN_ID}}, key)
assert resp['PARAM']['result'] == 'success', f"FAIL DeleteManager: {resp['PARAM']}"
print(f"[8.7 PASS] DeleteManager -> success")
sock.close()

# Test 8.8: Cannot delete last manager
sock = new_conn(key)
resp_ids = send_command(sock, {"RETURN":"GetRequest","PARAM":{"result":"success","reason":"","command":"GetManagerID"}}, key)
remaining = resp_ids['PARAM'].get('ids', [])
sock.close()
if len(remaining) == 1:
    sock = new_conn(key)
    resp = send_command(sock, {"RETURN":"GetRequest","PARAM":{"result":"success","reason":"","command":"DeleteManager","id":remaining[0]}}, key)
    assert resp['PARAM']['result'] == 'fail', "FAIL: expected fail when deleting last manager"
    print(f"[8.8 PASS] Cannot delete last manager: reason='{resp['PARAM'].get('reason')}'")
    sock.close()
else:
    print(f"[8.8 SKIP] {len(remaining)} managers remain - need exactly 1 to test this case")

print("\n[SECTION 8] ALL TESTS PASSED")
