import socket
import json
import datetime
import sys
import argparse
from connect_hanvon import Xor64Codec, send_encrypted_message, recv_decrypted_message

def query_day(ip, port, codec, day_str):
    """
    Queries a single day of logs from the Hanvon device using Protocol V2 JSON
    """
    payload = {
        "RETURN": "GetRequest",
        "PARAM": {
            "result": "success",
            "reason": "",
            "command": "ClientGetRecord",
            "start_time": f"{day_str} 00:00:00",
            "end_time": f"{day_str} 23:59:59"
        }
    }
    
    cmd_str = json.dumps(payload, separators=(',', ':'))
    
    try:
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            s.settimeout(10)
            s.connect((ip, port))
            
            codec.reset_encoder()
            codec.reset_decoder()
            
            send_encrypted_message(s, codec, cmd_str)
            response = recv_decrypted_message(s, codec)
            
            data = json.loads(response)
            if "PARAM" in data:
                param = data["PARAM"]
                result = param.get("result")
                if result == "success":
                    records = param.get("record", [])
                    return records
                else:
                    print(f"[{day_str}] Device returned fail: {param.get('reason')}")
            else:
                print(f"[{day_str}] Invalid response structure.")
    except Exception as e:
        print(f"[{day_str}] Connection or protocol error: {e}")
    return []

def main():
    parser = argparse.ArgumentParser(description="Fetch logs from Hanvon FaceID Time Attendance Machine")
    parser.add_argument("--ip", default="192.168.209.61", help="Device IP Address")
    parser.add_argument("--port", type=int, default=9922, help="Device Port (default: 9922)")
    parser.add_argument("--password", default="123", help="Device connection password")
    parser.add_argument("--start", help="Start date (YYYY-MM-DD), default is 7 days ago")
    parser.add_argument("--end", help="End date (YYYY-MM-DD), default is today")
    parser.add_argument("--output", default="attendance_records.json", help="Output JSON file name")
    
    args = parser.parse_args()
    
    # Parse dates
    today = datetime.date.today()
    if args.start:
        start_date = datetime.datetime.strptime(args.start, "%Y-%m-%d").date()
    else:
        start_date = today - datetime.timedelta(days=7)
        
    if args.end:
        end_date = datetime.datetime.strptime(args.end, "%Y-%m-%d").date()
    else:
        end_date = today
        
    if start_date > end_date:
        print("Error: Start date cannot be after end date.")
        sys.exit(1)
        
    print(f"=== Hanvon FaceID Log Downloader ===")
    print(f"Target Device : {args.ip}:{args.port}")
    print(f"Query Period  : {start_date} to {end_date}")
    print(f"Output File   : {args.output}")
    print(f"Encryption    : Xor64Codec")
    print(f"=====================================")
    
    codec = Xor64Codec(args.password)
    all_records = []
    
    current_date = start_date
    while current_date <= end_date:
        day_str = current_date.strftime("%Y-%m-%d")
        print(f"Fetching logs for {day_str}...", end="", flush=True)
        records = query_day(args.ip, args.port, codec, day_str)
        if records:
            all_records.extend(records)
            print(f" Success ({len(records)} logs found)")
        else:
            print(" Success (0 logs found)")
        current_date += datetime.timedelta(days=1)
        
    print(f"\nAll logs downloaded. Total: {len(all_records)} logs.")
    
    # Save output
    try:
        with open(args.output, "w", encoding="utf-8") as f:
            json.dump(all_records, f, indent=4, ensure_ascii=False)
        print(f"Logs successfully written to {args.output}")
    except Exception as e:
        print(f"Failed to write output file: {e}")

if __name__ == "__main__":
    main()
