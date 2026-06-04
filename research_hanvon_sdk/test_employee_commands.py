import socket
import json
from connect_hanvon import Xor64Codec, send_encrypted_message, recv_decrypted_message

def test_get_employee_ids(ip, port, codec):
    print("\n--- Testing GetEmployeeID ---")
    payload = {
        "RETURN": "GetRequest",
        "PARAM": {
            "result": "success",
            "reason": "",
            "command": "GetEmployeeID",
            "userType": "0"
        }
    }
    cmd_str = json.dumps(payload, separators=(',', ':'))
    try:
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            s.settimeout(5)
            s.connect((ip, port))
            send_encrypted_message(s, codec, cmd_str)
            response = recv_decrypted_message(s, codec)
            print(f"Response: {response}")
            data = json.loads(response)
            if "PARAM" in data:
                param = data["PARAM"]
                print("Result:", param.get("result"))
                print("IDs count:", len(param.get("ids", [])))
                print("IDs:", param.get("ids"))
    except Exception as e:
        print("Error testing GetEmployeeID:", e)

def main():
    ip = "192.168.209.61"
    port = 9922
    password = "123"
    codec = Xor64Codec(password)
    
    test_get_employee_ids(ip, port, codec)

if __name__ == "__main__":
    main()
