import socket
import json
from connect_hanvon import Xor64Codec, recv_exact, send_encrypted_message, recv_decrypted_message

def test_shape(ip, port, codec, payload, desc):
    print(f"\n--- Testing Shape: {desc} ---")
    cmd_str = json.dumps(payload)
    print("Payload:", cmd_str)
    try:
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            s.settimeout(5)
            s.connect((ip, port))
            
            codec.reset_encoder()
            codec.reset_decoder()
            
            send_encrypted_message(s, codec, cmd_str)
            
            response = recv_decrypted_message(s, codec)
            safe_text = response.encode('ascii', errors='backslashreplace').decode('ascii')
            print("Decrypted Response:")
            print(safe_text)
    except Exception as e:
        print("Error:", e)

def main():
    ip = "192.168.209.61"
    port = 9922
    password = "123"
    codec = Xor64Codec(password)
    
    # Shape 1: No dates, just command GetRecord
    test_shape(ip, port, codec, {
        "RETURN": "GetRequest",
        "PARAM": {
            "command": "GetRecord"
        }
    }, "No dates")
    
    # Shape 2: Empty dates
    test_shape(ip, port, codec, {
        "RETURN": "GetRequest",
        "PARAM": {
            "command": "GetRecord",
            "start_time": "",
            "end_time": ""
        }
    }, "Empty dates")
    
    # Shape 3: Single 'time' field with tilde (from test_conn.ps1 V1 test)
    test_shape(ip, port, codec, {
        "RETURN": "GetRequest",
        "PARAM": {
            "command": "GetRecord",
            "time": "2026-06-01 00:00:00~2026-06-04 23:59:59"
        }
    }, "Time tilde range")

    # Shape 4: start_date / end_date instead of start_time / end_time
    test_shape(ip, port, codec, {
        "RETURN": "GetRequest",
        "PARAM": {
            "command": "GetRecord",
            "start_date": "2026-06-01",
            "end_date": "2026-06-04"
        }
    }, "start_date/end_date")

if __name__ == "__main__":
    main()
