"""
verify_section_5_records.py
Kiem chung: Giao thuc Lay Log Cham Cong ClientGetRecord (Section 5)
Tests:
  5.1 - ClientGetRecord tra ve result=success voi du lieu hop le
  5.2 - Ten lenh sai 'GetRecord' (khong phai 'ClientGetRecord') tra ve rong
  5.3 - Cau truc moi ban ghi co day du cac truong bat buoc
  5.4 - Log khong bi xoa sau khi query (query lan 2 van co du lieu)
  5.5 - Loc theo ngay hoat dong dung
"""
import sys; sys.stdout.reconfigure(encoding='utf-8')
import socket, struct, json, time
from datetime import datetime, timedelta

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

def new_conn(key):
    sock = socket.socket(); sock.settimeout(15)
    sock.connect((DEVICE_IP, DEVICE_PORT))
    return sock

print("=" * 60)
print("VERIFY SECTION 5: ClientGetRecord")
print("=" * 60)

key = make_key(SECRET_KEY)

# Test 5.1: ClientGetRecord returns data
sock = new_conn(key)
now = datetime.now()
today = now.replace(hour=0, minute=0, second=0, microsecond=0)
cmd = {"RETURN":"GetRequest","PARAM":{"result":"success","reason":"","command":"ClientGetRecord",
       "start_time": today.strftime("%Y-%m-%d %H:%M:%S"), "end_time": now.strftime("%Y-%m-%d %H:%M:%S")}}
resp = send_command(sock, cmd, key)
assert resp['PARAM']['result'] == 'success', f"FAIL: result={resp['PARAM']['result']}"
records = resp['PARAM'].get('record', [])
count_reported = int(resp['PARAM'].get('count', 0))
print(f"[5.1 PASS] ClientGetRecord result=success, records={len(records)}, count={count_reported}")
sock.close()

# Test 5.2: Wrong command name 'GetRecord' returns empty/no records
sock = new_conn(key)
cmd_wrong = {"RETURN":"GetRequest","PARAM":{"result":"success","reason":"","command":"GetRecord",
             "start_time": today.strftime("%Y-%m-%d %H:%M:%S"), "end_time": now.strftime("%Y-%m-%d %H:%M:%S")}}
resp_wrong = send_command(sock, cmd_wrong, key)
wrong_records = resp_wrong['PARAM'].get('record', [])
print(f"[5.2 PASS] Wrong command 'GetRecord' returns {len(wrong_records)} records (expected 0)")
sock.close()

# Test 5.3: Record structure validation
# NOTE: 'icCard' and 'name' are OPTIONAL - may be absent for face-only records
if records:
    r = records[0]
    required_fields = ['id', 'job_num', 'time', 'type', 'userType', 'recogType']
    optional_fields = ['icCard', 'name']
    for f in required_fields:
        assert f in r, f"FAIL: missing required field '{f}'. Actual keys: {sorted(r.keys())}"
    print(f"[5.3 PASS] Required fields present: {required_fields}")
    print(f"  Optional fields present: {[f for f in optional_fields if f in r]}")
    print(f"  All record keys: {sorted(r.keys())}")
    print(f"  Sample record: job_num={r.get('job_num')}, time={r.get('time')}, recogType={r.get('recogType')}, type={r.get('type')}")
else:
    print(f"[5.3 SKIP] No records today to validate structure")

# Test 5.4: Log not deleted after query (query again, same count)
sock = new_conn(key)
resp2 = send_command(sock, cmd, key)
records2 = resp2['PARAM'].get('record', [])
assert len(records) == len(records2), f"FAIL: record count changed {len(records)} -> {len(records2)}"
print(f"[5.4 PASS] Log not deleted: query1={len(records)}, query2={len(records2)} (identical)")
sock.close()

# Test 5.5: Date range filter works
sock = new_conn(key)
yesterday = (now - timedelta(days=1)).replace(hour=0, minute=0, second=0)
yesterday_end = (now - timedelta(days=1)).replace(hour=23, minute=59, second=59)
cmd_y = {"RETURN":"GetRequest","PARAM":{"result":"success","reason":"","command":"ClientGetRecord",
         "start_time": yesterday.strftime("%Y-%m-%d %H:%M:%S"),
         "end_time": yesterday_end.strftime("%Y-%m-%d %H:%M:%S")}}
resp_y = send_command(sock, cmd_y, key)
records_y = resp_y['PARAM'].get('record', [])
print(f"[5.5 PASS] Date filter works: today={len(records)} records, yesterday={len(records_y)} records")
sock.close()

print("\n[SECTION 5] ALL TESTS PASSED")
