import socket
import json
import datetime
from connect_hanvon import Xor64Codec, recv_exact, send_encrypted_message, recv_decrypted_message

def query_day(ip, port, codec, target_date):
    start_str = target_date.strftime("%Y-%m-%d 00:00:00")
    end_str = target_date.strftime("%Y-%m-%d 23:59:59")
    
    payload = {
        "RETURN": "GetRequest",
        "PARAM": {
            "command": "GetRecord",
            "start_time": start_str,
            "end_time": end_str
        }
    }
    
    cmd_str = json.dumps(payload)
    
    try:
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            s.settimeout(3.0)
            s.connect((ip, port))
            
            codec.reset_encoder()
            codec.reset_decoder()
            
            send_encrypted_message(s, codec, cmd_str)
            
            response = recv_decrypted_message(s, codec)
            data = json.loads(response)
            param = data.get("PARAM", {})
            result = param.get("result")
            
            if result == "success":
                # Check for records
                records = param.get("record", [])
                count = param.get("count", "0")
                if records or int(count) > 0:
                    print(f"[FOUND] Date {target_date.strftime('%Y-%m-%d')}: {len(records)} records (count={count})")
                    return records
                else:
                    # Success but empty
                    pass
            else:
                reason = param.get("reason", "unknown")
                print(f"[FAIL] Date {target_date.strftime('%Y-%m-%d')}: {reason}")
    except Exception as e:
        # Silently skip connection timeouts/errors to keep console clean
        pass
    return []

def main():
    ip = "192.168.209.61"
    port = 9922
    password = "123"
    codec = Xor64Codec(password)
    
    today = datetime.date(2026, 6, 4)
    print(f"Scanning last 30 days starting from {today}...")
    
    all_found_records = []
    for i in range(30):
        target_date = today - datetime.timedelta(days=i)
        records = query_day(ip, port, codec, target_date)
        if records:
            all_found_records.extend(records)
            
    print(f"\nScan complete. Total records retrieved: {len(all_found_records)}")
    if all_found_records:
        with open("scanned_records.json", "w", encoding="utf-8") as f:
            json.dump(all_found_records, f, indent=2, ensure_ascii=False)
        print("Saved retrieved records to scanned_records.json")

if __name__ == "__main__":
    main()
