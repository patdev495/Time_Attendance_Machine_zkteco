import socket
from connect_hanvon import Xor64Codec, recv_exact, send_encrypted_message, recv_decrypted_message

def test_once(ip, port, password):
    codec = Xor64Codec(password)
    test_cmd = '{"RETURN":"GetRequest","PARAM":{"result":"success","reason":"","command":"GetDeviceInfo"}}'
    
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.settimeout(5)
        s.connect((ip, port))
        
        codec.reset_encoder()
        codec.reset_decoder()
        
        send_encrypted_message(s, codec, test_cmd)
        
        # Read raw header
        header = recv_exact(s, 4)
        length = int.from_bytes(header, "big")
        
        encrypted_body = recv_exact(s, length)
        decrypted_bytes = codec.decode(encrypted_body)
        
        plaintext = decrypted_bytes.decode('utf-8', errors='replace')
        print(f"Length: {length}")
        print("Repr plaintext: ", repr(plaintext))
        print("Raw bytes hex of decrypted: ", decrypted_bytes.hex())

if __name__ == "__main__":
    ip = "192.168.209.61"
    port = 9922
    password = "123"
    
    print("--- Run 1 ---")
    try:
        test_once(ip, port, password)
    except Exception as e:
        print("Run 1 Error:", e)
        
    print("\n--- Run 2 ---")
    try:
        test_once(ip, port, password)
    except Exception as e:
        print("Run 2 Error:", e)
