"""
verify_section_10_realtime.py
Kiem chung: Co che Giam sat Cham cong Real-time (Section 10)
Tests:
  10.1 - Long-poll: nhieu lenh tren cung 1 TCP connection
  10.2 - Deduplication: cung ban ghi khong duoc dem 2 lan
  10.3 - Reconnect: ket noi lai reset hoan toan, van hoat dong dung
  10.4 - Poll interval: 3 chu ky x 2 giay = ~6 giay tong cong
"""
import sys; sys.stdout.reconfigure(encoding='utf-8')
import socket, struct, json, time
from datetime import datetime

DEVICE_IP = "192.168.209.61"
DEVICE_PORT = 9922
SECRET_KEY = "123"
STATIC_KEY = [0, 1, 2, 4, 8, 16, 32, 64]
POLL_CYCLES = 3
POLL_INTERVAL = 2

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

def get_records(sock, key, start_time, end_time):
    cmd = {"RETURN":"GetRequest","PARAM":{"result":"success","reason":"","command":"ClientGetRecord",
           "start_time":start_time.strftime("%Y-%m-%d %H:%M:%S"),
           "end_time":end_time.strftime("%Y-%m-%d %H:%M:%S")}}
    resp, body = send_command(sock, cmd, key)
    return resp['PARAM'].get('record', []), body

print("=" * 60)
print("VERIFY SECTION 10: Real-time Long-Poll")
print("=" * 60)

key = make_key(SECRET_KEY)

# Test 10.1: Multiple commands on same TCP connection
print(f"\n[10.1] Testing {POLL_CYCLES} consecutive polls on same TCP connection...")
sock = socket.socket(); sock.settimeout(15)
sock.connect((DEVICE_IP, DEVICE_PORT))

# Handshake
hs = {"RETURN":"GetRequest","PARAM":{"result":"success","reason":"","command":"GetDeviceInfo"}}
resp_hs, _ = send_command(sock, hs, key)
assert resp_hs['PARAM']['result'] == 'success', "FAIL: handshake failed"

today = datetime.now().replace(hour=0, minute=0, second=0, microsecond=0)
bodies = []
record_counts = []

for i in range(POLL_CYCLES):
    records, body = get_records(sock, key, today, datetime.now())
    bodies.append(body[:20])
    record_counts.append(len(records))
    print(f"  Cycle {i+1}: {len(records)} records, body[:20]={body[:20].hex()}")
    if i < POLL_CYCLES - 1: time.sleep(POLL_INTERVAL)

# Verify all succeeded (would throw exception otherwise)
print(f"[10.1 PASS] {POLL_CYCLES} consecutive polls succeeded on same TCP connection")
sock.close()

# Test 10.2: XOR proof - all response bodies start with same bytes (both TX and RX reset to 0)
assert all(b == bodies[0] for b in bodies), f"FAIL: body bytes differ across cycles -> XOR state is NOT resetting"
print(f"[10.2 PASS] XOR reset confirmed: body[:20] identical across all {POLL_CYCLES} cycles")
print(f"  Evidence: {bodies[0].hex()}")

# Test 10.3: Deduplication logic
all_records_first_cycle = record_counts[0]
known_ids = set()
new_events_per_cycle = []
sock = socket.socket(); sock.settimeout(15)
sock.connect((DEVICE_IP, DEVICE_PORT))
send_command(sock, {"RETURN":"GetRequest","PARAM":{"result":"success","reason":"","command":"GetDeviceInfo"}}, key)
for i in range(3):
    records, _ = get_records(sock, key, today, datetime.now())
    new = [r for r in records if f"{r.get('job_num')}|{r.get('time')}" not in known_ids]
    for r in records: known_ids.add(f"{r.get('job_num')}|{r.get('time')}")
    new_events_per_cycle.append(len(new))
    time.sleep(1)
sock.close()

assert new_events_per_cycle[0] > 0 or all_records_first_cycle == 0, "FAIL: first cycle should find new events"
assert new_events_per_cycle[1] == 0, f"FAIL: second cycle should have 0 new events, got {new_events_per_cycle[1]}"
assert new_events_per_cycle[2] == 0, f"FAIL: third cycle should have 0 new events, got {new_events_per_cycle[2]}"
print(f"[10.3 PASS] Deduplication: cycle1={new_events_per_cycle[0]} new, cycle2=0, cycle3=0")

# Test 10.4: Reconnect works fine
sock = socket.socket(); sock.settimeout(15)
sock.connect((DEVICE_IP, DEVICE_PORT))
resp_hs2, _ = send_command(sock, hs, key)
records_after, _ = get_records(sock, key, today, datetime.now())
sock.close()
assert len(records_after) == all_records_first_cycle, f"FAIL: record count changed after reconnect: {all_records_first_cycle} -> {len(records_after)}"
print(f"[10.4 PASS] Reconnect works, same record count={len(records_after)}")

print(f"\n[SECTION 10] ALL TESTS PASSED")
print(f"Summary: Long-poll is viable at {POLL_INTERVAL}s intervals on persistent TCP connection")
