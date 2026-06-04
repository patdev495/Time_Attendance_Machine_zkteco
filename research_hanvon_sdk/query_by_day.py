import socket
import json
from connect_hanvon import Xor64Codec, recv_exact, send_encrypted_message, recv_decrypted_message

def test_command(ip, port, codec, cmd_str, desc):
    print(f"\n--- Testing {desc} ---")
    print("Payload:", repr(cmd_str))
    try:
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            s.settimeout(5)
            s.connect((ip, port))
            
            codec.reset_encoder()
            codec.reset_decoder()
            
            send_encrypted_message(s, codec, cmd_str)
            
            response = recv_decrypted_message(s, codec)
            
            # Save response to a file FIRST
            filename = f"response_{desc.replace(' ', '_').lower()}.json"
            with open(filename, "w", encoding="utf-8") as f:
                f.write(response)
            print(f"Saved response to {filename}")
            
            # Safe print to console using ASCII escaping
            safe_text = response.encode('ascii', errors='backslashreplace').decode('ascii')
            print("Decrypted Response (Safe ASCII):")
            print(safe_text)
            
    except Exception as e:
        print("Error:", e)

def main():
    ip = "192.168.209.61"
    port = 9922
    password = "123"
    codec = Xor64Codec(password)
    
    # 1. Test V2 JSON Format for exactly 1 day (today: 2026-06-04)
    v2_payload = {
        "RETURN": "GetRequest",
        "PARAM": {
            "command": "GetRecord",
            "start_time": "2026-06-04 00:00:00",
            "end_time": "2026-06-04 23:59:59"
        }
    }
    test_command(ip, port, codec, json.dumps(v2_payload), "V2 JSON format 1 day")
    
    # 2. Test V1 Plain text format for exactly 1 day (no comma)
    v1_payload_no_comma = 'GetRecord(start_time="2026-06-04 00:00:00" end_time="2026-06-04 23:59:59")'
    test_command(ip, port, codec, v1_payload_no_comma, "V1 Plain Text no comma")
    
    # 3. Test V1 Plain text format with comma (just in case)
    v1_payload_comma = 'GetRecord(start_time="2026-06-04 00:00:00",end_time="2026-06-04 23:59:59")'
    test_command(ip, port, codec, v1_payload_comma, "V1 Plain Text with comma")

if __name__ == "__main__":
    main()
