import socket
import json
from connect_hanvon import Xor64Codec, recv_exact, send_encrypted_message, recv_decrypted_message

def main():
    ip = "192.168.209.61"
    port = 9922
    password = "123"

    codec = Xor64Codec(password)
    
    # Correct format according to the SDK guide:
    payload = {
        "RETURN": "GetRequest",
        "PARAM": {
            "command": "GetRecord",
            "start_time": "2026-06-01 00:00:00",
            "end_time": "2026-06-04 23:59:59"
        }
    }
    
    cmd_str = json.dumps(payload)
    print("Payload to send:", cmd_str)
    
    print(f"Connecting to {ip}:{port} to fetch logs...")
    try:
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            s.settimeout(15)
            s.connect((ip, port))
            print("Connected. Sending GetRecord command...")
            
            codec.reset_encoder()
            codec.reset_decoder()
            
            send_encrypted_message(s, codec, cmd_str)
            
            print("Waiting for response...")
            response = recv_decrypted_message(s, codec)
            print(f"Received decrypted response of length {len(response)} characters.")
            
            # Save response to a file with UTF-8 encoding
            output_file = "records_response_correct.json"
            with open(output_file, "w", encoding="utf-8") as f:
                f.write(response)
            print(f"Decrypted JSON saved to {output_file}")
            
            try:
                data = json.loads(response)
                print("Response data keys:", list(data.keys()))
                param = data.get("PARAM", {})
                print("PARAM keys:", list(param.keys()))
                print("Result status:", param.get("result"))
                print("Reason:", param.get("reason"))
            except Exception as pe:
                print("JSON parse error, raw response:", repr(response))
                
    except Exception as e:
        print("Error:", e)

if __name__ == "__main__":
    main()
