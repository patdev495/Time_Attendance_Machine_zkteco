import socket
import json

class Xor64Codec:
    def __init__(self, secret_key: str):
        self.secret_key = secret_key
        self.encoder_index = 0
        self.decoder_index = 0
        
        # Derive the 8-byte key
        self.derived_key = bytearray(8)
        static_key = [0, 1, 2, 4, 8, 16, 32, 64]
        key_bytes = secret_key.encode('utf-8')
        for i in range(8):
            if i < len(key_bytes):
                self.derived_key[i] = (key_bytes[i] + static_key[i]) & 0xFF
            else:
                self.derived_key[i] = static_key[i]
                
    def reset_encoder(self):
        self.encoder_index = 0
        
    def reset_decoder(self):
        self.decoder_index = 0
        
    def encode(self, data: bytes) -> bytes:
        result = bytearray(len(data))
        for i in range(len(data)):
            result[i] = data[i] ^ self.derived_key[self.encoder_index]
            self.encoder_index = (self.encoder_index + 1) % 8
        return bytes(result)
        
    def decode(self, data: bytes) -> bytes:
        result = bytearray(len(data))
        for i in range(len(data)):
            result[i] = data[i] ^ self.derived_key[self.decoder_index]
            self.decoder_index = (self.decoder_index + 1) % 8
        return bytes(result)


def recv_exact(sock, n):
    data = b""
    while len(data) < n:
        chunk = sock.recv(n - len(data))
        if not chunk:
            raise ConnectionError("Socket closed prematurely")
        data += chunk
    return data


def send_encrypted_message(sock, codec, message_str):
    message_bytes = message_str.encode('utf-8')
    encrypted_bytes = codec.encode(message_bytes)
    
    # 4-byte big-endian length header
    length_header = len(encrypted_bytes).to_bytes(4, byteorder='big')
    
    sock.sendall(length_header + encrypted_bytes)
    print(f"Sent {len(message_bytes)} bytes of plaintext (encoded to {len(encrypted_bytes)} bytes)")


def recv_decrypted_message(sock, codec):
    header = recv_exact(sock, 4)
    length = int.from_bytes(header, "big")
    print(f"Receiving packet with length header: {length} bytes")
    
    encrypted_body = recv_exact(sock, length)
    decrypted_bytes = codec.decode(encrypted_body)
    
    return decrypted_bytes.decode('utf-8', errors='replace')


def main():
    ip = "192.168.209.61"
    port = 9922
    password = "123"

    print("Initializing Xor64Codec with password:", password)
    codec = Xor64Codec(password)
    
    # Test encryption locally to verify with Wireshark packet 1145
    test_cmd = '{"RETURN":"GetRequest","PARAM":{"result":"success","reason":"","command":"GetDeviceInfo"}}'
    codec.reset_encoder()
    enc_test = codec.encode(test_cmd.encode('utf-8'))
    expected_hex = "4a1167415c45720e130917436d647225404650777c320c626172674545321a3b134150777d7c54620b1146716b734533421119267a7541335e5d173e2a320c62525c5869697e44620b1172617c5445365850504d66764f624c4e"
    
    if enc_test.hex() == expected_hex:
        print("[OK] Local Xor64Codec verification SUCCESS. Matches Wireshark packet 1145 hex exactly.")
    else:
        print("[FAIL] Local Xor64Codec verification FAILED.")
        print("Expected:", expected_hex)
        print("Got:     ", enc_test.hex())
        
    print(f"\nConnecting to {ip}:{port}...")
    try:
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            s.settimeout(5)
            s.connect((ip, port))
            print("Connected. Initiating handshake...")
            
            # Send connection command
            # Note: We must reset codec indices when starting a new session/message stream
            codec.reset_encoder()
            codec.reset_decoder()
            
            send_encrypted_message(s, codec, test_cmd)
            
            # Receive response
            response = recv_decrypted_message(s, codec)
            print("\nDecrypted Response from Hanvon:")
            print(response)
            
    except Exception as e:
        print("Error connecting/communicating with Hanvon device:", e)

if __name__ == "__main__":
    main()
