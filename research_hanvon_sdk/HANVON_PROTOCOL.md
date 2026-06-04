# Tài liệu Kỹ thuật: Giao thức Kết nối Máy Chấm Công Hanvon FaceID (HW-C302A)

**Phiên bản tài liệu**: 2.0  
**Ngày cập nhật lần cuối**: 2026-06-04  
**Thiết bị thử nghiệm**: Hanvon HW-C302A | IP: 192.168.209.61 | Port: 9922  
**Trạng thái**: Đã xác minh 100% bằng thực nghiệm (7/7 test suites PASS)

---

## Mục lục

1. [Thông tin Thiết bị & Driver](#1-thông-tin-thiết-bị--driver)
2. [Giải thuật Mã hóa XOR (Xor64Codec)](#2-giải-thuật-mã-hóa-xor)
3. [Cấu trúc Khung Truyền TCP](#3-cấu-trúc-khung-truyền-tcp)
4. [Handshake & GetDeviceInfo](#4-handshake--getdeviceinfo)
5. [Lấy Log Chấm Công (ClientGetRecord)](#5-lấy-log-chấm-công-clientgetrecord)
6. [Script Lấy Log Hoàn Chỉnh](#6-script-lấy-log-hoàn-chỉnh)
7. [Quản lý Nhân viên (Employee)](#7-quản-lý-nhân-viên-employee)
8. [Quản lý Quản trị viên (Manager)](#8-quản-lý-quản-trị-viên-manager)
9. [Phân loại Quyền hạn Người dùng](#9-phân-loại-quyền-hạn-người-dùng)
10. [Giám sát Chấm công Real-time](#10-giám-sát-chấm-công-real-time)
11. [Bộ Script Kiểm chứng (Verification Suite)](#11-bộ-script-kiểm-chứng)

---

## 1. Thông tin Thiết bị & Driver

| Thuộc tính | Giá trị |
|---|---|
| **Model** | Hanvon FaceID HW-C302A |
| **Serial Number** | 8183325050000252 |
| **Firmware** | 5.302.1.1.0.135 |
| **Algorithm** | V5.5.17.5 |
| **IP mặc định (môi trường dev)** | 192.168.209.61 |
| **Port TCP** | 9922 (cố định) |
| **Protocol Version** | **Version 2 (JSON V2 với XOR encryption)** |
| **Max nhân viên đăng ký** | 2.000 khuôn mặt / 200.000 log |
| **Max quản trị viên** | 10 |
| **MAC** | 00:0C:5B:0E:6C:2C |

> **Lưu ý quan trọng**: Driver dạng `DEV_HW_D2` bắt buộc dùng JSON V2 (có mã hóa XOR).
> Các thiết bị cũ hơn có thể dùng Protocol V1 (plaintext), nhưng HW-C302A chỉ hỗ trợ V2.

---

## 2. Giải thuật Mã hóa XOR

**Script kiểm chứng**: `research_hanvon_sdk/verify_section_2_xor.py`  
**Lệnh chạy**: `uv run python research_hanvon_sdk/verify_section_2_xor.py`  
**Kết quả**: ✅ 3/3 assertions PASS

### 2.1 Sinh Khóa Động (DerivedKey)

Từ mật khẩu kết nối (`SecretKey`, mặc định `"123"`), thuật toán tạo mảng khóa 8 bytes bằng cách cộng với `StaticKey`:

```python
StaticKey = [0, 1, 2, 4, 8, 16, 32, 64]
DerivedKey = bytearray(8)
secret_bytes = SecretKey.encode('utf-8')

for i in range(8):
    if i < len(secret_bytes):
        DerivedKey[i] = (secret_bytes[i] + StaticKey[i]) & 0xFF
    else:
        DerivedKey[i] = StaticKey[i]
```

**Ví dụ với SecretKey = "123"**:
- `ord('1')=0x31` + `StaticKey[0]=0` = `0x31`
- `ord('2')=0x32` + `StaticKey[1]=1` = `0x33`
- `ord('3')=0x33` + `StaticKey[2]=2` = `0x35`
- Byte 3-7: lấy từ StaticKey: `0x04, 0x08, 0x10, 0x20, 0x40`

**DerivedKey kết quả**: `[0x31, 0x33, 0x35, 0x04, 0x08, 0x10, 0x20, 0x40]`

### 2.2 Quy trình XOR và Hành vi Reset (ĐÃ XÁC MINH)

Mọi byte gửi đi hoặc nhận về đều được XOR với `DerivedKey`, tuần hoàn theo chỉ số `0..7`.

**⚠️ PHÁT HIỆN QUAN TRỌNG (xác minh thực nghiệm ngày 2026-06-04)**:

Cả **TX (gửi đi)** và **RX (nhận về)** đều **reset về index 0 sau mỗi transaction** (một cặp request-response). Đây là hành vi ngược với stream cipher thông thường.

**Bằng chứng vật lý** (từ test script):
```
Cycle 1 body[0:20] = 4a131747475d6d017f7717243230021254474076
Cycle 2 body[0:20] = 4a131747475d6d017f7717243230021254474076  <- giống hệt
Cycle 3 body[0:20] = 4a131747475d6d017f7717243230021254474076  <- giống hệt
```

Ba phản hồi trên cùng 1 TCP connection có bytes đầu giống hệt nhau → thiết bị RESET codec về 0 sau mỗi transaction.

**Implementation đúng** (không cần quản lý state):
```python
def xor_from_zero(data: bytes, key: bytearray) -> bytes:
    """XOR luon bat dau tu index 0 - dung cho ca TX va RX."""
    result = bytearray(len(data))
    for i, b in enumerate(data):
        result[i] = b ^ key[i % 8]
    return bytes(result)

def send_command(sock, cmd: dict, key: bytearray) -> dict:
    """Gui lenh, nhan phan hoi. Khong can quan ly XOR state."""
    payload = json.dumps(cmd, ensure_ascii=False).encode('utf-8')
    encrypted = xor_from_zero(payload, key)
    sock.sendall(struct.pack('!I', len(encrypted)) + encrypted)
    
    header = b''
    while len(header) < 4: header += sock.recv(4 - len(header))
    body_len = struct.unpack('!I', header)[0]
    
    body = b''
    while len(body) < body_len: body += sock.recv(body_len - len(body))
    return json.loads(xor_from_zero(body, key).decode('utf-8'))
```

---

## 3. Cấu trúc Khung Truyền TCP

**Script kiểm chứng**: `research_hanvon_sdk/verify_section_3_frame.py`  
**Lệnh chạy**: `uv run python research_hanvon_sdk/verify_section_3_frame.py`  
**Kết quả**: ✅ 3/3 assertions PASS

### 3.1 Format Frame

Mỗi gói tin (cả gửi và nhận) qua port TCP 9922 có cấu trúc:

```
+------------------------+------------------------------------------------+
|  Length (4 bytes, BE)  |        XOR-encrypted JSON Body (N bytes)       |
+------------------------+------------------------------------------------+
```

- **Header**: 4 bytes, số nguyên 32-bit Big-Endian (`struct.pack('!I', N)`) chứa độ dài phần body
- **Body**: N bytes, là JSON string sau khi qua `xor_from_zero()`

**Ví dụ thực tế** (đã capture từ thiết bị):
```
Header bytes: 00 00 02 50  ->  body_len = 592 bytes  (phản hồi GetDeviceInfo)
Header bytes: 00 00 20 A4  ->  body_len = 8356 bytes (phản hồi 62 records)
```

### 3.2 Quy trình Gửi và Nhận

```python
import socket, struct, json

def new_connection(ip: str, port: int = 9922) -> socket.socket:
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sock.settimeout(15)
    sock.connect((ip, port))
    return sock

def recv_exact(sock, n: int) -> bytes:
    """Doc dung n bytes, xu ly truong hop TCP fragmentation."""
    data = b''
    while len(data) < n:
        chunk = sock.recv(n - len(data))
        if not chunk:
            raise ConnectionError("Connection closed by device")
        data += chunk
    return data
```

---

## 4. Handshake & GetDeviceInfo

**Script kiểm chứng**: `research_hanvon_sdk/verify_section_4_handshake.py`  
**Lệnh chạy**: `uv run python research_hanvon_sdk/verify_section_4_handshake.py`  
**Kết quả**: ✅ 4/4 assertions PASS

Sau khi mở kết nối TCP, bắt buộc gửi handshake để xác nhận kết nối và lấy thông tin thiết bị.

### 4.1 JSON Request

```json
{
  "RETURN": "GetRequest",
  "PARAM": {
    "result": "success",
    "reason": "",
    "command": "GetDeviceInfo"
  }
}
```

> **Lưu ý**: Các trường `result`, `reason` trong PARAM là bắt buộc (kế thừa từ class cha trong SDK). Thiếu bất kỳ trường nào sẽ bị từ chối.

### 4.2 JSON Response (đầy đủ từ thiết bị thực tế)

```json
{
  "COMMAND": "Return",
  "PARAM": {
    "result": "success",
    "reason": "",
    "deviceInfo": {
      "alg_edition": "V5.5.17.5",
      "edition": "5.302.1.1.0.135",
      "gateway": "192.168.209.254",
      "ip": "192.168.209.61",
      "mac": "00:0C:5B:0E:6C:2C",
      "managerlock": false,
      "managernum": 1,
      "max_facerecord": 200000,
      "max_faceregist": 2000,
      "max_managernum": 10,
      "model": "HW-C302A",
      "name": "",
      "netcard": 2,
      "netmask": "255.255.255.0",
      "real_facerecord": 172,
      "real_faceregist": 45,
      "sn": "8183325050000252",
      "time": "2026-06-04 15:48:22",
      "type": "HW-C302A",
      "volume": 2,
      "wiegand": 0
    }
  }
}
```

### 4.3 Giải thích các trường quan trọng

| Trường | Ý nghĩa |
|---|---|
| `real_facerecord` | Tổng số log chấm công đang lưu trên thiết bị |
| `max_facerecord` | Giới hạn tối đa log lưu được (200.000) |
| `real_faceregist` | Số nhân viên đã đăng ký khuôn mặt |
| `max_faceregist` | Giới hạn nhân viên có thể đăng ký (2.000) |
| `managernum` | Số quản trị viên hiện có |
| `max_managernum` | Giới hạn tối đa quản trị viên (10) |
| `managerlock` | Thiết bị có bị khóa bởi admin không |
| `edition` | Phiên bản firmware |
| `alg_edition` | Phiên bản thuật toán nhận diện khuôn mặt |
| `wiegand` | Cấu hình cổng Wiegand (0=tắt) |

---

## 5. Lấy Log Chấm Công (ClientGetRecord)

**Script kiểm chứng**: `research_hanvon_sdk/verify_section_5_records.py`  
**Lệnh chạy**: `uv run python research_hanvon_sdk/verify_section_5_records.py`  
**Kết quả**: ✅ 5/5 assertions PASS

### 5.1 Lỗi trong Tài liệu SDK Gốc

Tài liệu PDF của Hanvon hướng dẫn dùng `"command": "GetRecord"`, nhưng:
- ❌ `GetRecord` → trả về **0 records** (không có dữ liệu)
- ✅ `ClientGetRecord` → trả về **đúng dữ liệu** (đã xác minh)

Tên lệnh đúng là **`ClientGetRecord`** (được tìm ra từ dịch ngược file DLL).

### 5.2 JSON Request

```json
{
  "RETURN": "GetRequest",
  "PARAM": {
    "result": "success",
    "reason": "",
    "command": "ClientGetRecord",
    "start_time": "2026-06-04 00:00:00",
    "end_time": "2026-06-04 23:59:59"
  }
}
```

- `start_time` / `end_time`: định dạng `YYYY-MM-DD HH:MM:SS`
- Khuyến nghị: chia theo từng ngày (max 1 ngày/query) để tránh timeout với device có nhiều log

### 5.3 JSON Response

```json
{
  "COMMAND": "Return",
  "PARAM": {
    "result": "success",
    "reason": "",
    "sn": "8183325050000252",
    "count": "62",
    "record": [
      {
        "id": "232604090",
        "job_num": "232604090",
        "time": "2026-06-04 15:43:05",
        "type": "HW-C302A",
        "userType": "0",
        "recogType": "0"
      }
    ]
  }
}
```

### 5.4 Giải thích các trường trong từng Record

| Trường | Bắt buộc | Ý nghĩa |
|---|---|---|
| `id` | ✅ | ID định danh nhân viên |
| `job_num` | ✅ | Mã nhân viên (thường = `id`) |
| `time` | ✅ | Thời gian chấm công (`YYYY-MM-DD HH:MM:SS`) |
| `type` | ✅ | Model thiết bị (`HW-C302A`) |
| `userType` | ✅ | Loại người dùng (`"0"` = normal) |
| `recogType` | ✅ | Phương thức nhận dạng (xem bảng bên dưới) |
| `icCard` | ❌ optional | Mã thẻ từ (không có trong record chỉ dùng khuôn mặt) |
| `name` | ❌ optional | Tên nhân viên (không phải lúc nào cũng có) |

**Giải mã `recogType`**:

| Giá trị | Phương thức |
|---|---|
| `"0"` | Unknown (không xác định hoặc thiết bị cũ) |
| `"1"` | Face (Khuôn mặt) |
| `"2"` | Fingerprint (Vân tay) |
| `"3"` | IC Card (Thẻ từ) |
| `"4"` | Password (Mật khẩu) |

### 5.5 Lưu ý quan trọng

- **Log KHÔNG bị xóa** sau khi gọi `ClientGetRecord` (đã xác minh: query 2 lần cùng kết quả)
- **Giới hạn phần cứng**: Chia nhỏ khoảng thời gian thành từng ngày (max 1 ngày/query)
- **Lấy nhiều ngày**: Gửi N queries liên tiếp (mỗi query 1 ngày), gộp kết quả phía client
- **`count` trong response** khớp với `len(record)` (không có phân trang)

---

## 6. Script Lấy Log Hoàn Chỉnh

Script đầy đủ với CLI arguments:

**File**: `research_hanvon_sdk/get_records.py`  
**Lệnh chạy**:
```bash
# Lay log hom nay
uv run python research_hanvon_sdk/get_records.py --ip 192.168.209.61

# Lay log theo khoang thoi gian, luu ra file
uv run python research_hanvon_sdk/get_records.py --ip 192.168.209.61 --start 2026-06-01 --end 2026-06-04 --output attendance_records.json
```

**Tham số**:
- `--ip`: IP máy chấm công
- `--start`: Ngày bắt đầu (YYYY-MM-DD)
- `--end`: Ngày kết thúc (YYYY-MM-DD)
- `--output`: File JSON kết quả (tuỳ chọn)

---

## 7. Quản lý Nhân viên (Employee)

**Script kiểm chứng**: `research_hanvon_sdk/verify_section_7_employee.py`  
**Lệnh chạy**: `uv run python research_hanvon_sdk/verify_section_7_employee.py`  
**Kết quả**: ✅ 6/6 assertions PASS (bao gồm tombstone verification)

### 7.1 Lấy Danh Sách ID Nhân Viên

**Request**:
```json
{
  "RETURN": "GetRequest",
  "PARAM": {
    "result": "success",
    "reason": "",
    "command": "GetEmployeeID",
    "userType": "0"
  }
}
```

**Response** (thực tế - 45 nhân viên):
```json
{
  "COMMAND": "Return",
  "PARAM": {
    "result": "success",
    "ids": ["10100101", "1904006", "1905075", "..."],
    "fids": ["10100101", "1904006", "1905075", "..."]
  }
}
```

- `ids`: Danh sách tất cả ID nhân viên
- `fids`: Danh sách ID nhân viên có đăng ký khuôn mặt (thường = `ids`)

### 7.2 Lấy Chi Tiết Nhân Viên (ClientGetEmployee)

**Request**:
```json
{
  "RETURN": "GetRequest",
  "PARAM": {
    "result": "success",
    "reason": "",
    "command": "ClientGetEmployee",
    "job_num": "10100101",
    "userType": "0"
  }
}
```

**Response** (các trường THỰC TẾ từ thiết bị - đã xác minh):
```json
{
  "COMMAND": "Return",
  "PARAM": {
    "result": "success",
    "id": "10100101",
    "job_num": "10100101",
    "name": "hank",
    "userType": "1",
    "password": "",
    "capturejpg": "<BASE64_JPEG_PHOTO ~17820 chars>",
    "face_data": ["<BASE64_FACE_TEMPLATE>"]
  }
}
```

**Chú ý về các trường KHÔNG có trong response** (khác với SDK docs):
- ❌ `reason` - không có trong response thực tế
- ❌ `icCard` - không có (trường này không được trả về ngay cả khi nhân viên có thẻ)
- ❌ `recogPermission` - không có trong response
- ❌ `finger_data` - không được trả về ngay cả khi đăng ký vân tay

**Tombstone (nhân viên đã xóa)**:
```json
{"PARAM": {"userType": "2"}}
```
→ `userType = "2"` nghĩa là ID không tồn tại hoặc đã bị xóa.

### 7.3 Thêm / Sửa Nhân Viên (SetEmployee)

**Request**:
```json
{
  "RETURN": "GetRequest",
  "PARAM": {
    "result": "success",
    "reason": "",
    "command": "SetEmployee",
    "id": "MA_NHAN_VIEN",
    "name": "Ten Nhan Vien",
    "sex": 2,
    "nation": "Vietnamese",
    "address": "",
    "userType": "1",
    "job_num": "MA_NHAN_VIEN",
    "icCard": "",
    "recogPermission": "face",
    "capturejpg": "<BASE64_JPEG_HOAC_RONG>",
    "face_data": ["<BASE64_TEMPLATE>"],
    "finger_data": []
  }
}
```

**Ràng buộc quan trọng**:
- `userType` **bắt buộc phải là `"1"`**. Mọi giá trị khác đều bị từ chối với lỗi: `"不支持的用户类型:0"` (Loại người dùng không hỗ trợ)
- Nếu nhân viên chưa có ảnh/template, để `capturejpg: ""` và `face_data: []` (thiết bị vẫn tạo được nhân viên, chỉ không nhận diện được mặt)
- `id` = `job_num` nếu không có CMND/thẻ ID riêng

**Response thành công**:
```json
{"COMMAND": "Return", "PARAM": {"result": "success", "reason": ""}}
```

### 7.4 Xóa Nhân Viên (DeleteEmployee)

**Request**:
```json
{
  "RETURN": "GetRequest",
  "PARAM": {
    "result": "success",
    "reason": "",
    "command": "DeleteEmployee",
    "id": "MA_NHAN_VIEN"
  }
}
```

**Sau khi xóa**: Query `ClientGetEmployee` với `job_num` đó sẽ trả `userType = "2"`.

---

## 8. Quản lý Quản trị viên (Manager)

**Script kiểm chứng**: `research_hanvon_sdk/verify_section_8_manager.py`  
**Lệnh chạy**: `uv run python research_hanvon_sdk/verify_section_8_manager.py`  
**Kết quả**: ✅ 8/8 assertions PASS

> **Yêu cầu**: Script cần file `research_hanvon_sdk/sample_employee_photo.txt` (ảnh base64 thực tế từ thiết bị) để test SetManager. File này được tạo tự động lần đầu chạy.

### 8.1 Lấy Danh Sách ID Quản trị viên

**Request**:
```json
{
  "RETURN": "GetRequest",
  "PARAM": {
    "result": "success",
    "reason": "",
    "command": "GetManagerID"
  }
}
```

**Response**:
```json
{
  "COMMAND": "Return",
  "PARAM": {
    "result": "success",
    "ids": ["admin"]
  }
}
```

### 8.2 Lấy Chi Tiết Quản trị viên

**Request**:
```json
{
  "RETURN": "GetRequest",
  "PARAM": {
    "result": "success",
    "reason": "",
    "command": "GetManager",
    "id": "admin"
  }
}
```

**Response**:
```json
{
  "COMMAND": "Return",
  "PARAM": {
    "result": "success",
    "reason": "",
    "id": "admin",
    "password": "123456",
    "authority": 0,
    "capturejpg": "<BASE64_JPEG>"
  }
}
```

**Giải mã `authority`**:
| Giá trị | Quyền hạn |
|---|---|
| `0` | **Super Administrator** - Toàn quyền cấu hình thiết bị |
| `2` | **Ordinary Administrator** - Quyền hạn chế |

### 8.3 Thêm / Sửa Quản trị viên (SetManager)

**Request**:
```json
{
  "RETURN": "GetRequest",
  "PARAM": {
    "result": "success",
    "reason": "",
    "command": "SetManager",
    "id": "TEN_DANG_NHAP",
    "capturejpg": "<BASE64_JPEG_BAT_BUOC>",
    "password": "123456",
    "authority": 2
  }
}
```

**Ràng buộc quan trọng** (đã xác minh):
1. **`capturejpg` bắt buộc có ảnh thực tế** (không để rỗng):
   - Lỗi khi rỗng: `{"reason": "缺少图片", "result": "fail"}` (Thiếu hình ảnh)
   - Lỗi khi ảnh giả quá nhỏ: `{"reason": "照片过大或过小", "result": "fail"}` (Ảnh quá lớn hoặc quá nhỏ)
   - **Giải pháp**: Dùng ảnh JPEG thực (≥15KB) từ nhân viên đã có trên thiết bị
2. **`password` không được trùng** với bất kỳ manager nào khác:
   - Lỗi: `{"reason": "密码已存在", "result": "fail"}` (Mật khẩu đã tồn tại)
3. **`authority` tự chuẩn hóa**: Mọi giá trị `1`, `2`, `3` đều được lưu thành `2`; giá trị `0` được giữ nguyên

### 8.4 Xóa Quản trị viên (DeleteManager)

**Request**:
```json
{
  "RETURN": "GetRequest",
  "PARAM": {
    "result": "success",
    "reason": "",
    "command": "DeleteManager",
    "id": "TEN_DANG_NHAP"
  }
}
```

**Bảo vệ cuối cùng**: Thiết bị từ chối xóa manager cuối cùng:
```json
{"reason": "不能删除最后一名管理员", "result": "fail"}
```

---

## 9. Phân loại Quyền hạn Người dùng

### 9.1 Nhân viên (Employee)

Quản lý qua: `GetEmployeeID`, `ClientGetEmployee`, `SetEmployee`, `DeleteEmployee`

| `userType` | Ý nghĩa |
|---|---|
| `"1"` | Nhân viên thường (Standard Employee) - **Giá trị duy nhất được chấp nhận khi tạo** |
| `"2"` | Tombstone - ID không tồn tại hoặc đã xóa |
| `"0"` | Dùng trong query parameter (lấy tất cả loại) - **Không dùng khi tạo** |

### 9.2 Quản trị viên (Manager)

Quản lý qua: `GetManagerID`, `GetManager`, `SetManager`, `DeleteManager`

| `authority` | Quyền hạn |
|---|---|
| `0` | Super Administrator |
| `2` | Ordinary Administrator |

---

## 10. Giám sát Chấm công Real-time

**Script kiểm chứng**: `research_hanvon_sdk/verify_section_10_realtime.py`  
**Lệnh chạy**: `uv run python research_hanvon_sdk/verify_section_10_realtime.py`  
**Kết quả**: ✅ 4/4 assertions PASS

**Script monitor production**: `research_hanvon_sdk/realtime_attendance_monitor.py`  
**Lệnh chạy monitor**: `uv run python research_hanvon_sdk/realtime_attendance_monitor.py --ip 192.168.209.61`

### 10.1 Kiến trúc Firmware (từ Reverse Engineering)

- ❌ **Không có Push từ thiết bị**: HW-C302A KHÔNG chủ động push sự kiện chấm công lên server
- ✅ **Polling là cơ chế duy nhất**: Phần mềm Hanvon KMS chính thức sử dụng `DownRcdtimer_Tick` + `backgroundWorkerRcdDown_DoWork` để poll định kỳ
- **`NotifyAfterAddRcd(Int64 empId, DateTime dt)`**: Là delegate nội bộ trong C# app sau khi lưu vào DB - không phải tín hiệu từ firmware
- **`TcpListenerPlus`**: Tồn tại trong SDK nhưng không dùng cho attendance push trên HW-C302A

### 10.2 So sánh các Cơ chế

| Cơ chế | Ưu điểm | Nhược điểm | Khuyến nghị |
|---|---|---|---|
| **Long-Poll** (persistent TCP) | Ít overhead, 3-5s delay | Cần xử lý reconnect | ✅ **RECOMMENDED** |
| **Polling** (reconnect mỗi lần) | Đơn giản, resilient | Overhead TCP handshake mỗi cycle | ✅ Fallback tốt |
| **TCP Push Listener** | Event-driven thực sự | Firmware không hỗ trợ trên HW-C302A | ❌ Không khả thi |

### 10.3 Kiến trúc Long-Poll (ĐÚNG VÀ ĐÃ XÁC MINH)

Giữ 1 kết nối TCP duy nhất, gọi `ClientGetRecord` định kỳ. Nhờ XOR reset về 0 sau mỗi transaction, không cần quản lý XOR state.

```python
def monitor_device(ip: str, interval: int = 3):
    key = make_derived_key(SECRET_KEY)
    known_ids = set()
    first_run = True
    
    while True:  # auto-reconnect loop
        try:
            sock = socket.socket()
            sock.settimeout(15)
            sock.connect((ip, 9922))
            
            # Handshake
            send_command(sock, {
                "RETURN": "GetRequest",
                "PARAM": {"result": "success", "reason": "", "command": "GetDeviceInfo"}
            }, key)
            
            while True:  # polling loop
                now = datetime.now()
                today = now.replace(hour=0, minute=0, second=0, microsecond=0)
                
                resp = send_command(sock, {
                    "RETURN": "GetRequest",
                    "PARAM": {
                        "result": "success", "reason": "",
                        "command": "ClientGetRecord",
                        "start_time": today.strftime("%Y-%m-%d %H:%M:%S"),
                        "end_time": now.strftime("%Y-%m-%d %H:%M:%S")
                    }
                }, key)
                
                records = resp['PARAM'].get('record', [])
                
                if first_run:
                    # Load initial state without triggering events
                    for r in records:
                        known_ids.add(f"{r['job_num']}|{r['time']}")
                    first_run = False
                else:
                    for r in records:
                        key_r = f"{r['job_num']}|{r['time']}"
                        if key_r not in known_ids:
                            known_ids.add(key_r)
                            on_new_attendance(r)  # trigger callback
                
                time.sleep(interval)
        
        except KeyboardInterrupt:
            return
        except Exception as e:
            sock.close()
            time.sleep(10)  # wait before reconnect
```

### 10.4 Deduplication Key

Dùng composite key `job_num|time` để tránh đếm trùng:
```python
rkey = f"{record['job_num']}|{record['time']}"
```

### 10.5 Khi nào reset `known_ids`

| Tình huống | Hành động |
|---|---|
| Kết nối lại sau khi mất | Giữ nguyên `known_ids` (tránh duplicate events) |
| Chuyển sang ngày mới (00:00) | Clear `known_ids` (records của ngày cũ không còn trong query window) |
| Restart toàn bộ service | Clear `known_ids`, `first_run = True` |

---

## 11. Bộ Script Kiểm chứng

Tất cả scripts nằm trong thư mục `research_hanvon_sdk/`.

### 11.1 Chạy toàn bộ suite (7 scripts, ~10 giây)

```bash
uv run python research_hanvon_sdk/run_all_verifications.py
```

**Kết quả lần chạy cuối (2026-06-04)**:
```
[OK] Section 2 - XOR Codec          (0.4s)
[OK] Section 3 - TCP Frame Format   (0.2s)
[OK] Section 4 - Handshake          (0.2s)
[OK] Section 5 - ClientGetRecord    (0.3s)
[OK] Section 7 - Employee CRUD      (0.8s)
[OK] Section 8 - Manager CRUD       (0.9s)
[OK] Section 10 - Real-time Poll    (7.8s)

Passed: 7/7 | Total time: 10.6s
```

### 11.2 Bảng tra cứu Script → Section

| Script | Section | Mô tả | Lệnh chạy |
|---|---|---|---|
| `verify_section_2_xor.py` | §2 | XOR codec, DerivedKey, TX/RX reset | `uv run python research_hanvon_sdk/verify_section_2_xor.py` |
| `verify_section_3_frame.py` | §3 | TCP frame 4-byte header + body | `uv run python research_hanvon_sdk/verify_section_3_frame.py` |
| `verify_section_4_handshake.py` | §4 | GetDeviceInfo handshake + tất cả fields | `uv run python research_hanvon_sdk/verify_section_4_handshake.py` |
| `verify_section_5_records.py` | §5 | ClientGetRecord, GetRecord (sai), log persistence | `uv run python research_hanvon_sdk/verify_section_5_records.py` |
| `verify_section_7_employee.py` | §7 | GetEmployeeID, ClientGetEmployee, SetEmployee, DeleteEmployee | `uv run python research_hanvon_sdk/verify_section_7_employee.py` |
| `verify_section_8_manager.py` | §8 | GetManagerID, GetManager, SetManager (photo/pwd rules), DeleteManager | `uv run python research_hanvon_sdk/verify_section_8_manager.py` |
| `verify_section_10_realtime.py` | §10 | Long-poll 3 cycles, XOR proof, deduplication, reconnect | `uv run python research_hanvon_sdk/verify_section_10_realtime.py` |
| `run_all_verifications.py` | ALL | Master runner cho tất cả | `uv run python research_hanvon_sdk/run_all_verifications.py` |

### 11.3 Script Monitor Real-time (Production-ready)

```bash
# Chay monitor 3s interval
uv run python research_hanvon_sdk/realtime_attendance_monitor.py --ip 192.168.209.61

# Chay monitor 5s interval voi debug logs
uv run python research_hanvon_sdk/realtime_attendance_monitor.py --ip 192.168.209.61 --interval 5 --verbose
```

File `realtime_attendance_monitor.py` chứa callback `on_new_attendance(record, device_ip)` - thay thế bằng logic thực tế (lưu DB, gửi webhook, WebSocket).

### 11.4 Script Lấy Log Lịch Sử

```bash
# Lay log hom nay
uv run python research_hanvon_sdk/get_records.py --ip 192.168.209.61

# Lay log 30 ngay
uv run python research_hanvon_sdk/query_last_30_days.py --ip 192.168.209.61

# Lay log theo ngay cu the
uv run python research_hanvon_sdk/get_records.py --ip 192.168.209.61 --start 2026-06-01 --end 2026-06-04 --output out.json
```

---

## Phụ lục: Bảng tổng hợp tất cả Commands đã xác minh

| Command | Mục đích | Status | Script kiểm chứng |
|---|---|---|---|
| `GetDeviceInfo` | Handshake, lấy thông tin thiết bị | ✅ PASS | verify_section_4_handshake.py |
| `ClientGetRecord` | Lấy log chấm công theo khoảng thời gian | ✅ PASS | verify_section_5_records.py |
| `GetRecord` | (SAI) - Trả về rỗng, không dùng | ✅ Đã xác nhận sai | verify_section_5_records.py |
| `GetEmployeeID` | Lấy danh sách ID nhân viên | ✅ PASS | verify_section_7_employee.py |
| `ClientGetEmployee` | Lấy chi tiết nhân viên (ảnh, template) | ✅ PASS | verify_section_7_employee.py |
| `SetEmployee` | Thêm/sửa nhân viên (`userType="1"` bắt buộc) | ✅ PASS | verify_section_7_employee.py |
| `DeleteEmployee` | Xóa nhân viên | ✅ PASS | verify_section_7_employee.py |
| `GetManagerID` | Lấy danh sách ID quản trị viên | ✅ PASS | verify_section_8_manager.py |
| `GetManager` | Lấy chi tiết quản trị viên | ✅ PASS | verify_section_8_manager.py |
| `SetManager` | Thêm/sửa quản trị viên (cần ảnh thật) | ✅ PASS | verify_section_8_manager.py |
| `DeleteManager` | Xóa quản trị viên (không thể xóa cuối cùng) | ✅ PASS | verify_section_8_manager.py |

---

*Tài liệu này được tổng hợp từ: (1) dịch ngược DLL driver Hanvon KMS, (2) thực nghiệm trực tiếp trên thiết bị HW-C302A, (3) bộ test scripts tự động hoá. Mọi thông tin đều có script kiểm chứng tương ứng.*
