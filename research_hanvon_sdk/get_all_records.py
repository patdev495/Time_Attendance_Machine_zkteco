import socket
import json
from connect_hanvon import Xor64Codec, recv_exact, send_encrypted_message, recv_decrypted_message

def main():
    ip = "192.168.209.61"
    port = 9922
    password = "123"

    codec = Xor64Codec(password)
    
    # Query with a very wide range to fetch all stored records
    payload = {
        "RETURN": "GetRequest",
        "PARAM": {
            "command": "GetRecord",
            "start_time": "2010-01-01 00:00:00",
            "end_time": "2030-12-31 23:59:59"
        }
    }
    
    cmd_str = json.dumps(payload)
    print("Payload to send:", cmd_str)
    
    print(f"Connecting to {ip}:{port} to fetch ALL logs...")
    try:
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            s.settimeout(30)  # Larger timeout in case there are many logs
            s.connect((ip, port))
            print("Connected. Sending GetRecord command...")
            
            codec.reset_encoder()
            codec.reset_decoder()
            
            send_encrypted_message(s, codec, cmd_str)
            
            print("Waiting for response...")
            response = recv_decrypted_message(s, codec)
            print(f"Received decrypted response of length {len(response)} characters.")
            
            # Save response to a file with UTF-8 encoding
            output_file = "all_records_response.json"
            with open(output_file, "w", encoding="utf-8") as f:
                f.write(response)
            print(f"Decrypted JSON saved to {output_file}")
            
            try:
                data = json.loads(response)
                param = data.get("PARAM", {})
                print("Result status:", param.get("result"))
                print("Reason:", param.get("reason"))
                print("Serial Number:", param.get("sn"))
                
                # Check for records
                count = param.get("count")
                print("Record count reported in header:", count)
                
                records = param.get("record", [])
                print(f"Actual parsed records in list: {len(records)}")
                
                if records:
                    print("First record:", json.dumps(records[0], ensure_ascii=True))
                    print("Last record:", json.dumps(records[-1], ensure_ascii=True))
            except Exception as pe:
                print("JSON parse error, raw response start:", repr(response[:500]))
                
    except Exception as e:
        print("Error:", e)

if __name__ == "__main__":
    main()
