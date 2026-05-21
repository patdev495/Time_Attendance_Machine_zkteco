# 🕒 Hệ Thống Giám Sát Chấm Công & Kiosk Canteen Real-time (Time Attendance System)

[![FastAPI](https://img.shields.io/badge/Backend-FastAPI-009688?style=for-the-badge&logo=fastapi&logoColor=white)](https://fastapi.tiangolo.com/)
[![Vue 3](https://img.shields.io/badge/Frontend-Vue%203-4FC08D?style=for-the-badge&logo=vuedotjs&logoColor=white)](https://vuejs.org/)
[![Python 3.12](https://img.shields.io/badge/Python-3.12%2B-3776AB?style=for-the-badge&logo=python&logoColor=white)](https://www.python.org/)
[![SQL Server](https://img.shields.io/badge/Database-MS%20SQL%20Server-CC292B?style=for-the-badge&logo=microsoftsqlserver&logoColor=white)](https://www.microsoft.com/sql-server)
[![License](https://img.shields.io/badge/License-MIT-yellow.svg?style=for-the-badge)](LICENSE)

Hệ thống quản lý và giám sát chấm công thời gian thực (Real-time), tích hợp kiểm soát suất ăn canteen dành cho các nhà máy, văn phòng sử dụng dòng máy chấm công ZKTeco (giao thức ZK). 

Dự án được xây dựng tối ưu hiệu năng với kiến trúc **FastAPI (Python)** kết hợp **Vue 3 (Vite + Composition API)** và quản lý gói siêu tốc bằng **uv**.

---

## ✨ Tính Năng Nổi Bật

* 🖥️ **Live Dashboard Real-time**: Giám sát trạng thái hoạt động của các máy chấm công trực quan và nhận sự kiện quẹt vân tay/thẻ ngay lập tức qua kết nối WebSockets.
* 🍔 **Kiosk Canteen & Meal Tracking**: Chế độ kiosk tự động hiển thị thông tin suất ăn đăng ký của nhân viên khi quẹt thẻ, đi kèm công cụ chống quẹt trùng lặp thông minh.
* 📡 **Watchdog Tự Động Kết Nối**: Luồng giám sát chạy ngầm (LiveMonitor) tự động phát hiện và kết nối lại máy chấm công khi gặp sự cố ngắt kết nối vật lý hoặc lag mạng.
* 🔄 **Đồng Bộ Dữ Liệu Roster**: Đồng bộ thông tin nhân viên nhanh chóng từ file Excel cấu trúc ca làm việc (`employee_work_shift.xlsx`).
* 📊 **Bảng Tính Công Chi Tiết (Daily Summary)**: Tự động tính toán giờ công làm việc, đi muộn, về sớm, tăng ca ngày thường/ngày nghỉ chi tiết theo từng ca làm việc định nghĩa trước.
* 🌎 **Hỗ Trợ Đa Ngôn Ngữ**: Bản địa hóa toàn bộ giao diện với 3 ngôn ngữ chính: Tiếng Việt, Tiếng Anh (English), và Tiếng Trung (中文).
* 📦 **Standalone EXE & Demo Mode (SQLite)**: Cho phép đóng gói hệ thống thành duy nhất 1 file `.exe` chạy không cần cài đặt hoặc deploy demo portfolio lên Render.com.

---

## 📂 Cấu Trúc Dự Án

```text
Time_Attendance_Machine/
├── backend/
│   ├── src/                 # 🚀 Mã nguồn FastAPI backend (APIs, Websockets, Core Logic)
│   │   ├── features/        # Phân chia logic theo domain dọc (machines, logs, meal_tracking,...)
│   │   ├── shared/          # Module dùng chung (database, socket connections)
│   │   └── main.py          # Entry point khởi động ứng dụng
│   ├── scripts/             # 🛠️ Script khởi tạo cơ sở dữ liệu & di chuyển (migrate) data
│   ├── config/              # Quản lý file cấu hình & biến môi trường
│   ├── static/              # 📦 Thư mục chứa giao diện Vue 3 đã được build tĩnh
│   └── logs/                # Thư mục lưu nhật ký hoạt động hệ thống
├── frontend/                # 💻 Mã nguồn ứng dụng Client SPA (Vue 3, Vite, Pinia, Vanilla CSS)
│   ├── src/
│   │   ├── components/      # Các component tái sử dụng (Layout, Modals)
│   │   ├── features/        # Các trang tính năng (Live Monitor, Logs, Meal)
│   │   ├── i18n/            # Hệ thống đa ngôn ngữ (vi, en, zh)
│   │   └── stores/          # Quản lý state toàn cục qua Pinia
├── machines.txt             # 📝 File khai báo danh sách IP máy chấm công và URL webhook suất ăn
├── employee_work_shift.xlsx # 📊 Roster ca làm việc chính thức của nhân viên
├── dev.bat                  # ⚡ File chạy nhanh môi trường phát triển (Local Dev)
└── build_standalone.bat     # 📦 Script đóng gói ứng dụng Standalone Windows .exe
```

---

## 🛠️ Yêu Cầu Hệ Thống

Để chạy hoặc đóng gói dự án tại local, bạn cần chuẩn bị sẵn:
1. **Python 3.12+** cùng công cụ quản lý gói **uv** (Khuyên dùng - Xem hướng dẫn cài đặt `uv` tại [astral.sh/uv](https://github.com/astral-sh/uv)).
2. **Node.js** (Phiên bản v18 trở lên) và **npm**.
3. **Microsoft SQL Server 2008+** (Chạy chính thức) hoặc dùng chế độ **Demo Mode (SQLite)** chạy không cần cài đặt DB bên thứ ba.
4. **Microsoft ODBC Driver 17/18 for SQL Server** (Chạy trên Windows phục vụ kết nối DB).

---

## ⚡ Hướng Dẫn Cài Đặt & Chạy Môi Trường Phát Triển (Local Dev)

### 1. Chuẩn bị file cấu hình
Tại thư mục `backend/`, copy file mẫu để tạo file `.env` chứa cấu hình kết nối DB:
```bash
cp backend/.env.template backend/.env
```
Mở file `backend/.env` lên và chỉnh sửa thông tin kết nối SQL Server của bạn.

> [!NOTE]
> Bạn có thể bật chế độ demo nhanh không cần DB bằng cách đổi `DEMO_MODE=true` trong `.env`. Hệ thống sẽ tự động dùng sqlite và giả lập sự kiện quẹt thẻ.

### 2. Khai báo danh sách Máy Chấm Công
Khai báo danh sách IP máy chấm công của bạn vào file `machines.txt` ở thư mục gốc theo cấu trúc:
```text
# IP_Address       [Canteen_URL (optional)]       # Tags (nolive để tắt chế độ realtime)
192.168.209.20     http://localhost:8000/api/meal-ticket
192.168.209.21     # nolive
```

### 3. Cài đặt các thư viện phụ thuộc
Dùng `uv` để cài đặt cực nhanh toàn bộ môi trường ảo Python và NPM cho frontend:

**Backend (Python):**
```bash
# Tạo virtual environment và đồng bộ dependencies
uv sync
```

**Frontend (Vue 3):**
```bash
cd frontend
npm install
cd ..
```

### 4. Khởi tạo Cơ sở Dữ liệu
Chạy lệnh khởi tạo bảng và dữ liệu cơ sở cho SQL Server:
```bash
uv run python backend/scripts/db_init.py
```

### 5. Chạy dự án ở chế độ Development
Nếu bạn dùng Windows, hãy nhấp đúp (hoặc chạy qua console) file tiện ích cực nhanh:
```cmd
.\dev.bat
```
*Script tự động mở 2 cửa sổ cmd chạy song song:*
* **Backend FastAPI** khởi chạy tại: `http://localhost:8000`
* **Frontend Vite Dev** khởi chạy tại: `http://localhost:5173`

---

## 📦 Cách Đóng Gói Ứng Dụng Standalone (.EXE trên Windows)

Hệ thống cung cấp sẵn script đóng gói toàn bộ backend FastAPI và frontend Vue thành duy nhất 1 thư mục chạy độc lập cực kỳ gọn nhẹ để cắm thẳng tại nhà máy mà không cần cài đặt node, python hay docker:

1. Chạy file bat đóng gói ở thư mục gốc:
   ```cmd
   .\build_standalone.bat
   ```
2. Sau khi chạy hoàn tất, hãy truy cập thư mục:
   ```text
   dist/TimeAttendance/
   ```
3. Chạy file chính `TimeAttendance.exe` để vận hành toàn bộ hệ thống! Bạn có thể tùy chọn chỉ định Port chạy qua tham số:
   ```cmd
   .\TimeAttendance.exe --port 9000 --host 0.0.0.0
   ```

---

## ☁️ Triển Khai Demo Danh Mục Đầu Tư Lên Render.com (Miễn Phí)

Nếu muốn đưa sản phẩm lên web portfolio cá nhân để giới thiệu mà không lo tốn phí hạ tầng MSSQL, dự án hỗ trợ triệt để chạy demo qua SQLite và có cơ chế tự giả lập sự kiện live quẹt thẻ:

1. Đưa toàn bộ code lên repository GitHub cá nhân.
2. Tạo bản sao snapshot cơ sở dữ liệu sang SQLite:
   ```bash
   uv run python backend/scripts/migrate_to_sqlite.py
   ```
3. Commit file `demo_data/attendance.db` mới tạo lên GitHub.
4. Đăng nhập [Render.com](https://render.com/), tạo **New Web Service**, kết nối repo của bạn.
5. Cài đặt các biến môi trường sau trên Render:
   * `DEMO_MODE` = `true`
   * `PYTHON_VERSION` = `3.12.0`
6. Chọn **Create Web Service**. File cấu hình `render.yaml` đi kèm sẽ tự động tối ưu quá trình build và chạy mượt mà bản demo của bạn!

---

## 🛡️ Bản Quyền (License)

Dự án này được phát hành dưới giấy phép MIT. Chi tiết vui lòng xem tại file [LICENSE](LICENSE).
