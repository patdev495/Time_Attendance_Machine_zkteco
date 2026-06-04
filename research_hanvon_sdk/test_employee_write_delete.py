import socket
import json
from connect_hanvon import Xor64Codec, send_encrypted_message, recv_decrypted_message

def safe_print(title, text):
    safe_text = text.encode('ascii', errors='backslashreplace').decode('ascii')
    print(f"{title}: {safe_text}")

def test_employee_write_and_delete(ip, port, codec):
    test_id = "999999"
    test_name = "Test Antigravity"
    
    # 0. Test ClientGetEmployee for a non-existent employee
    print("\n--- 0. Testing ClientGetEmployee (Non-existent Employee 888888) ---")
    non_existent_payload = {
        "RETURN": "GetRequest",
        "PARAM": {
            "result": "success",
            "reason": "",
            "command": "ClientGetEmployee",
            "job_num": "888888",
            "userType": "0"
        }
    }
    cmd_str = json.dumps(non_existent_payload, separators=(',', ':'))
    try:
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            s.settimeout(5)
            s.connect((ip, port))
            codec.reset_encoder()
            codec.reset_decoder()
            send_encrypted_message(s, codec, cmd_str)
            response = recv_decrypted_message(s, codec)
            safe_print("Non-existent Employee Response", response)
    except Exception as e:
        print("Error testing non-existent employee:", e)

    # 1. Test SetEmployee (Add virtual employee)
    print("\n--- 1. Testing SetEmployee (Add Virtual Employee) ---")
    set_payload = {
        "RETURN": "GetRequest",
        "PARAM": {
            "result": "success",
            "reason": "",
            "command": "SetEmployee",
            "id": test_id,
            "name": test_name,
            "sex": 2,
            "nation": "Vietnamese",
            "address": "",
            "userType": "1",
            "job_num": test_id,
            "icCard": "",
            "recogPermission": "face",
            "capturejpg": "",
            "face_data": [],
            "finger_data": []
        }
    }
    
    cmd_str = json.dumps(set_payload, separators=(',', ':'))
    try:
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            s.settimeout(5)
            s.connect((ip, port))
            codec.reset_encoder()
            codec.reset_decoder()
            send_encrypted_message(s, codec, cmd_str)
            response = recv_decrypted_message(s, codec)
            safe_print("SetEmployee Response", response)
    except Exception as e:
        print("Error testing SetEmployee:", e)

    # 2. Test ClientGetEmployee (Verify details of virtual employee)
    print("\n--- 2. Testing ClientGetEmployee (Verify Details) ---")
    get_payload = {
        "RETURN": "GetRequest",
        "PARAM": {
            "result": "success",
            "reason": "",
            "command": "ClientGetEmployee",
            "job_num": test_id,
            "userType": "0"
        }
    }
    cmd_str = json.dumps(get_payload, separators=(',', ':'))
    try:
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            s.settimeout(5)
            s.connect((ip, port))
            codec.reset_encoder()
            codec.reset_decoder()
            send_encrypted_message(s, codec, cmd_str)
            response = recv_decrypted_message(s, codec)
            safe_print("ClientGetEmployee Response", response)
    except Exception as e:
        print("Error testing ClientGetEmployee:", e)

    # 3. Test DeleteEmployee (Clean up/Delete virtual employee)
    print("\n--- 3. Testing DeleteEmployee (Clean Up) ---")
    delete_payload = {
        "RETURN": "GetRequest",
        "PARAM": {
            "result": "success",
            "reason": "",
            "command": "DeleteEmployee",
            "id": test_id
        }
    }
    cmd_str = json.dumps(delete_payload, separators=(',', ':'))
    try:
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            s.settimeout(5)
            s.connect((ip, port))
            codec.reset_encoder()
            codec.reset_decoder()
            send_encrypted_message(s, codec, cmd_str)
            response = recv_decrypted_message(s, codec)
            safe_print("DeleteEmployee Response", response)
    except Exception as e:
        print("Error testing DeleteEmployee:", e)

    # 4. Test ClientGetEmployee again (Verify deletion)
    print("\n--- 4. Testing ClientGetEmployee again (Verify Deletion) ---")
    try:
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            s.settimeout(5)
            s.connect((ip, port))
            codec.reset_encoder()
            codec.reset_decoder()
            send_encrypted_message(s, codec, json.dumps(get_payload, separators=(',', ':')))
            response = recv_decrypted_message(s, codec)
            safe_print("ClientGetEmployee (Post-Delete) Response", response)
    except Exception as e:
        print("Error verifying deletion:", e)

def main():
    ip = "192.168.209.61"
    port = 9922
    password = "123"
    codec = Xor64Codec(password)
    
    test_employee_write_and_delete(ip, port, codec)

if __name__ == "__main__":
    main()
