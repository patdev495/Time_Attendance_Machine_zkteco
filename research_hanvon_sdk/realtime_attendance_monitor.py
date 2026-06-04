"""
realtime_attendance_monitor.py - Hanvon Long-Poll Monitor
DA XAC MINH: CA TX VA RX XOR deu reset ve 0 sau moi transaction (request-response pair).
Moi giao dich la doc lap - khong co tich luy state qua cac lenh.
"""
import sys; sys.stdout.reconfigure(encoding='utf-8')
import socket, struct, json, time, argparse, logging
from datetime import datetime

logging.basicConfig(level=logging.INFO, format='%(asctime)s [%(levelname)s] %(message)s', datefmt='%H:%M:%S')
log = logging.getLogger(__name__)

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
    """XOR bat dau tu index 0 - dung cho ca TX va RX."""
    r = bytearray(len(data))
    for i, b in enumerate(data):
        r[i] = b ^ key[i % 8]
    return bytes(r)


def send_command(sock, cmd, key):
    """
    Gui lenh va nhan phan hoi.
    XOR BEHAVIOR (xac minh bang thuc nghiem):
      - TX: reset ve 0 moi request
      - RX: reset ve 0 moi response
    => Moi transaction la doc lap, khong tich luy state.
    """
    payload = json.dumps(cmd, ensure_ascii=False).encode('utf-8')
    enc = xor_from_zero(payload, key)
    sock.sendall(struct.pack('!I', len(enc)) + enc)

    h = b''
    while len(h) < 4: h += sock.recv(4 - len(h))
    n = struct.unpack('!I', h)[0]
    body = b''
    while len(body) < n: body += sock.recv(n - len(body))
    dec = xor_from_zero(body, key)
    return json.loads(dec.decode('utf-8'))


def connect_device(ip, key):
    sock = socket.socket()
    sock.settimeout(15)
    sock.connect((ip, DEVICE_PORT))
    hs = {"RETURN":"GetRequest","PARAM":{"result":"success","reason":"","command":"GetDeviceInfo"}}
    resp = send_command(sock, hs, key)
    info = resp['PARAM'].get('deviceInfo', {})
    log.info(f"Connected: model={info.get('model')}, sn={info.get('sn')}, records={info.get('real_facerecord','?')}/{info.get('max_facerecord','?')}")
    return sock


def on_new_attendance(record, device_ip):
    """Callback xu ly su kien moi - thay the bang logic thuc te (DB, webhook, WebSocket...)."""
    ts = datetime.now().strftime("%H:%M:%S")
    recog = {'0':'Unknown','1':'Face','2':'Fingerprint','3':'IC Card','4':'Password'}.get(record.get('recogType',''), '?')
    print(f"\n[{ts}] NEW ATTENDANCE at {device_ip}:")
    print(f"  Ma NV: {record.get('job_num')} | Ten: {record.get('name','N/A')}")
    print(f"  Time: {record.get('time')} | Method: {recog}")


def monitor_device(ip, interval=3, reconnect_delay=10):
    """Long-Poll monitor: giu 1 ket noi TCP, poll dinh ky, auto-reconnect."""
    key = make_key(SECRET_KEY)
    known_ids = set()
    first_run = True

    log.info(f"=== Hanvon Long-Poll Monitor | {ip}:{DEVICE_PORT} | interval={interval}s ===")

    while True:
        try:
            sock = connect_device(ip, key)
            while True:
                now = datetime.now()
                today = now.replace(hour=0, minute=0, second=0, microsecond=0)
                cmd = {
                    "RETURN": "GetRequest",
                    "PARAM": {
                        "result": "success", "reason": "",
                        "command": "ClientGetRecord",
                        "start_time": today.strftime("%Y-%m-%d %H:%M:%S"),
                        "end_time": now.strftime("%Y-%m-%d %H:%M:%S")
                    }
                }
                resp = send_command(sock, cmd, key)
                records = resp.get('PARAM', {}).get('record', [])

                new_events = []
                for r in records:
                    rkey = f"{r.get('job_num','')}|{r.get('time','')}"
                    if rkey not in known_ids:
                        known_ids.add(rkey)
                        new_events.append(r)

                if first_run:
                    log.info(f"Initial load: {len(known_ids)} records today (all marked known)")
                    first_run = False
                elif new_events:
                    for r in new_events: on_new_attendance(r, ip)
                else:
                    log.debug(f"Poll OK: total_known={len(known_ids)}")

                time.sleep(interval)

        except KeyboardInterrupt:
            log.info("Stopped."); return
        except Exception as e:
            log.warning(f"Error: {e}. Reconnecting in {reconnect_delay}s...")
            try: sock.close()
            except: pass
            time.sleep(reconnect_delay)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Hanvon Real-time Attendance Monitor (Long-Poll)")
    parser.add_argument("--ip", default="192.168.209.61")
    parser.add_argument("--interval", type=int, default=3)
    parser.add_argument("--verbose", action="store_true")
    args = parser.parse_args()
    if args.verbose: logging.getLogger().setLevel(logging.DEBUG)
    monitor_device(args.ip, args.interval)
