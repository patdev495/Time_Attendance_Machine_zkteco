import socket
import json
import time
from connect_hanvon import Xor64Codec, recv_exact

def recv_decrypted_frame(sock, codec):
    try:
        header = recv_exact(sock, 4)
        length = int.from_bytes(header, "big")
        print(f"--> Received frame header indicating {length} bytes")
        
        encrypted_body = recv_exact(sock, length)
        decrypted_bytes = codec.decode(encrypted_body)
        
        return decrypted_bytes.decode('utf-8', errors='replace')
    except socket.timeout:
        print("--> Timeout waiting for next frame")
        return None
    except ConnectionError:
        print("--> Connection closed by remote host")
        return None

def main():
    ip = "192.168.209.61"
    port = 9922
    password = "123"

    codec = Xor64Codec(password)
    
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
    
    print(f"Connecting to {ip}:{port}...")
    try:
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            s.settimeout(5.0)  # 5 seconds timeout for reads
            s.connect((ip, port))
            print("Connected. Sending GetRecord command...")
            
            codec.reset_encoder()
            codec.reset_decoder()
            
            # Send command
            message_bytes = cmd_str.encode('utf-8')
            encrypted_bytes = codec.encode(message_bytes)
            length_header = len(encrypted_bytes).to_bytes(4, byteorder='big')
            s.sendall(length_header + encrypted_bytes)
            
            print("Entering read loop. Waiting for frames...")
            frame_num = 1
            all_frames = []
            
            while True:
                response = recv_decrypted_frame(s, codec)
                if response is None:
                    break
                
                print(f"Frame {frame_num} decrypted content: {response[:300]}")
                if len(response) > 300:
                    print(f"... (truncated {len(response) - 300} chars)")
                
                all_frames.append(response)
                frame_num += 1
                
                # Check if we should stop (e.g. if the response has some end marker or if we parse result success)
                # Let's keep receiving until connection closes or times out.
            
            print(f"\nRead loop finished. Received {len(all_frames)} frames.")
            
            # Save all frames to a file
            with open("all_received_frames.json", "w", encoding="utf-8") as f:
                json.dump(all_frames, f, indent=2, ensure_ascii=False)
            print("Saved all received frames to all_received_frames.json")
            
    except Exception as e:
        print("Error:", e)

if __name__ == "__main__":
    main()
