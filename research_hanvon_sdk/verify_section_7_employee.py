"""
verify_section_7_employee.py
Kiem chung: Giao thuc Quan ly Nhan vien (Section 7)
Tests:
  7.1 - GetEmployeeID tra ve danh sach ID
  7.2 - ClientGetEmployee tra ve du lieu hop le (cac truong bat buoc)
  7.3 - SetEmployee tao moi thanh cong (voi userType=1)
  7.4 - SetEmployee that bai khi userType sai (khong phai "1")
  7.5 - DeleteEmployee xoa thanh cong -> query lai tra userType=2
"""
import sys; sys.stdout.reconfigure(encoding='utf-8')
import socket, struct, json

DEVICE_IP = "192.168.209.61"
DEVICE_PORT = 9922
SECRET_KEY = "123"
STATIC_KEY = [0, 1, 2, 4, 8, 16, 32, 64]
TEST_EMP_ID = "VERIFY_TEST_001"

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

print("=" * 60)
print("VERIFY SECTION 7: Employee Management")
print("=" * 60)

key = make_key(SECRET_KEY)

# Cleanup: remove test employee if exists from previous run
sock = new_conn(key)
send_command(sock, {"RETURN":"GetRequest","PARAM":{"result":"success","reason":"","command":"DeleteEmployee","id":TEST_EMP_ID}}, key)
sock.close()

# Test 7.1: GetEmployeeID returns list
sock = new_conn(key)
resp = send_command(sock, {"RETURN":"GetRequest","PARAM":{"result":"success","reason":"","command":"GetEmployeeID","userType":"0"}}, key)
assert resp['PARAM']['result'] == 'success', f"FAIL: {resp['PARAM']}"
ids = resp['PARAM'].get('ids', [])
fids = resp['PARAM'].get('fids', [])
print(f"[7.1 PASS] GetEmployeeID: {len(ids)} employees, {len(fids)} fids")
print(f"  Sample IDs: {ids[:3]}")
sock.close()

# Test 7.2: ClientGetEmployee returns valid data with correct fields
# CONFIRMED fields from real device: [capturejpg, face_data, id, job_num, name, password, result, userType]
# ABSENT fields: reason, icCard, recogPermission (these do NOT appear in response)
if ids:
    sock = new_conn(key)
    resp = send_command(sock, {"RETURN":"GetRequest","PARAM":{"result":"success","reason":"","command":"ClientGetEmployee","job_num":ids[0],"userType":"0"}}, key)
    assert resp['PARAM']['result'] == 'success', f"FAIL: {resp['PARAM']}"
    emp = resp['PARAM']
    # Verified required fields (actually present in device response)
    required = ['id', 'job_num', 'name', 'userType', 'capturejpg', 'face_data']
    for f in required:
        assert f in emp, f"FAIL: missing field '{f}'. Actual keys: {sorted(emp.keys())}"
    print(f"[7.2 PASS] ClientGetEmployee fields: {sorted(emp.keys())}")
    print(f"  id={emp.get('id')}, name={emp.get('name')}, userType={emp.get('userType')}")
    print(f"  has_photo={bool(emp.get('capturejpg'))}, has_face={bool(emp.get('face_data'))}")
    sock.close()
else:
    print("[7.2 SKIP] No employees on device")

# Test 7.3: SetEmployee with userType='1' succeeds
sock = new_conn(key)
set_cmd = {"RETURN":"GetRequest","PARAM":{"result":"success","reason":"","command":"SetEmployee",
    "id":TEST_EMP_ID, "name":"Verify Test Employee", "sex":2, "nation":"Vietnamese", "address":"",
    "userType":"1", "job_num":TEST_EMP_ID, "icCard":"", "recogPermission":"face",
    "capturejpg":"", "face_data":[], "finger_data":[]}}
resp = send_command(sock, set_cmd, key)
assert resp['PARAM']['result'] == 'success', f"FAIL SetEmployee: reason={resp['PARAM'].get('reason')}"
print(f"[7.3 PASS] SetEmployee with userType='1' -> success")
sock.close()

# Test 7.4: SetEmployee with invalid userType fails (device returns error)
sock = new_conn(key)
set_bad = {"RETURN":"GetRequest","PARAM":{"result":"success","reason":"","command":"SetEmployee",
    "id":"VERIFY_BAD_TYPE", "name":"Bad Type", "sex":2, "nation":"Vietnamese", "address":"",
    "userType":"0", "job_num":"VERIFY_BAD_TYPE", "icCard":"", "recogPermission":"face",
    "capturejpg":"", "face_data":[], "finger_data":[]}}
resp_bad = send_command(sock, set_bad, key)
assert resp_bad['PARAM']['result'] == 'fail', f"FAIL: expected fail for userType='0', got success"
print(f"[7.4 PASS] SetEmployee invalid userType='0' -> fail: reason='{resp_bad['PARAM'].get('reason')}'")
sock.close()

# Test 7.5: DeleteEmployee and verify deletion via tombstone
sock = new_conn(key)
resp = send_command(sock, {"RETURN":"GetRequest","PARAM":{"result":"success","reason":"","command":"DeleteEmployee","id":TEST_EMP_ID}}, key)
assert resp['PARAM']['result'] == 'success', f"FAIL DeleteEmployee: {resp['PARAM']}"
print(f"[7.5 PASS] DeleteEmployee -> success")
sock.close()

sock = new_conn(key)
resp_check = send_command(sock, {"RETURN":"GetRequest","PARAM":{"result":"success","reason":"","command":"ClientGetEmployee","job_num":TEST_EMP_ID,"userType":"0"}}, key)
deleted_type = resp_check['PARAM'].get('userType')
assert deleted_type == '2', f"FAIL: deleted employee should return userType='2', got '{deleted_type}'"
print(f"[7.5 PASS] Deleted employee tombstone: userType='{deleted_type}' (2 = not found/deleted)")
sock.close()

print("\n[SECTION 7] ALL TESTS PASSED")
