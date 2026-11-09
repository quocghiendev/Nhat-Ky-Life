# 📔 Nhật Ký AI Thực Thời (Multimodal AI Journal)

Ứng dụng web viết nhật ký hiện đại bằng **Chữ viết**, **Âm thanh** và **Hình ảnh**, kết hợp sức mạnh của **Trí tuệ Nhân tạo (Multimodal AI)** để tự động quan sát ảnh chụp từ camera, lắng nghe giọng nói voice, và tổng hợp lại thành các trang nhật ký sống động, giàu cảm xúc theo từng ngày thời gian thực.

Toàn bộ mã nguồn, tài nguyên và cơ sở dữ liệu đều được lưu trữ hoàn toàn nội bộ trong thư mục `D:\Users\NhatKyWeb`.

---

## 🌟 Tính Năng Nổi Bật

1. **Đa phương thức (Multimodal Input)**:
   - **Camera / Hình ảnh**: Bật trực tiếp camera (hỗ trợ chuyển đổi camera trước/sau trên điện thoại/laptop) để chụp khoảnh khắc thực tế, hoặc tải ảnh từ máy tính.
   - **Voice / Âm thanh**: Thu âm giọng nói thời gian thực với hiệu ứng sóng âm (Waveform Canvas Visualizer), bộ đếm thời gian, gỡ băng giọng nói trực tiếp (Web Speech API tiếng Việt), hoặc tải file âm thanh (.mp3, .wav, .m4a, .webm).
   - **Chữ viết**: Ghi chép nhanh suy nghĩ hoặc viết nhật ký thủ công bất kỳ lúc nào.

2. **AI Tự Động Tóm Tắt & Soạn Nhật Ký**:
   - Sử dụng mô hình **Google Gemini (Gemini 2.5 Flash / 1.5 Flash)** hoặc **OpenAI (Whisper + GPT-4o)** có khả năng hiểu đồng thời cả **Hình ảnh + Giọng nói** trong cùng một khoảnh khắc.
   - Tự động trích xuất:
     - **Tiêu đề gợi cảm xúc**.
     - **Tâm trạng & Biểu tượng cảm xúc (Mood & Emoji)**: Vui vẻ 😊, Bình yên 🌿, Chiêm nghiệm ☕, Hào hứng ✨...
     - **Nội dung nhật ký trau chuốt**: Kết hợp chi tiết trong ảnh với lời tâm sự của giọng nói.
     - **Thẻ phân loại (#tags)**.
     - **Gỡ băng lời nói gốc (Transcript)**.
   - Hỗ trợ chọn **Văn phong AI**: Chân thật & Gần gũi, Sâu sắc & Chiêm nghiệm, Thơ mộng & Lãng mạn, Vui vẻ & Năng động, Tối giản.
   - Chế độ **"Tự động điền & lưu vào nhật ký ngày hôm nay"**: Chỉ cần 1 click là nhật ký được tạo và hiển thị ngay trên dòng thời gian.

3. **Dòng Thời Gian Theo Từng Ngày Thực Thời**:
   - Tự động phân loại theo ngày (Hôm nay, Hôm qua, hoặc lọc theo Lịch).
   - Hiển thị mốc thời gian chi tiết (ví dụ: `15:42 • Chiều`).
   - Tích hợp trình phát âm thanh trực tiếp trong mỗi thẻ nhật ký để nghe lại giọng nói kỷ niệm.
   - Nhấp vào ảnh để xem chế độ phóng to (Lightbox).
   - Tính năng **"AI Tổng Kết Ngày"**: AI đọc toàn bộ các sự kiện trong ngày và viết một đoạn đúc kết, chiêm nghiệm trọn vẹn cho ngày hôm đó.

4. **Giao Diện Hiện Đại, Tiện Lợi**:
   - Chế độ **Sáng / Tối (Light / Dark Mode)** tùy chỉnh.
   - Đồng hồ thời gian thực.
   - Tìm kiếm từ khóa, đánh dấu ⭐ yêu thích, chỉnh sửa hoặc xóa mục nhật ký.
   - Lưu trữ dữ liệu an toàn trên SQLite (`data/database.sqlite3`) và thư mục `data/uploads/`.

---

## 🚀 Hướng Dẫn Khởi Chạy

### Cách 1: Chạy bằng file `start.bat` (Tiện lợi nhất trên Windows)
- Nhấp đúp chuột vào file **`start.bat`**.
- Hệ thống sẽ tự động khởi động máy chủ và mở trình duyệt web tại địa chỉ: `http://localhost:8000`.

### Cách 2: Chạy bằng dòng lệnh (Terminal / PowerShell)
1. Mở PowerShell tại thư mục `D:\Users\NhatKyWeb`:
```powershell
.\venv\Scripts\python.exe run.py
```
2. Mở trình duyệt web và truy cập: **`http://localhost:8000`**.

---

## 📱 Cách Truy Cập Từ Điện Thoại Hoặc Máy Khác

Khi bạn khởi động máy chủ (bằng `start.bat` hoặc `run.py`), hệ thống sẽ hiển thị 2 đường link:
- `http://localhost:8000` (dành cho máy tính hiện tại).
- `http://192.168.1.x:8000` (dành cho điện thoại hoặc máy khác trong cùng mạng Wi-Fi).

### Trường hợp A: Dùng trong cùng mạng Wi-Fi (Nội bộ LAN)
1. Kết nối điện thoại hoặc máy tính thứ hai vào **cùng mạng Wi-Fi** với máy chủ này.
2. Mở trình duyệt trên máy đó và nhập địa chỉ: `http://<IP_MÁY_BẠN>:8000` (ví dụ: `http://192.168.1.13:8000`).
3. **Mẹo về Camera & Micro**:
   - Do chính sách bảo mật trình duyệt, Camera và Mic trực tiếp (`getUserMedia`) chỉ mở khi có `HTTPS` hoặc `localhost`.
   - Vì vậy khi truy cập qua IP trên điện thoại, bạn chỉ cần bấm nút **"Tải ảnh lên"** &rarr; Điện thoại sẽ tự động mở Camera để chụp ảnh trực tiếp và gửi lên AI bình thường!
   - Tương tự, bạn có thể tải bản ghi âm có sẵn từ máy.

### Trường hợp B: Truy cập từ bất kỳ đâu (Bằng đường link HTTPS có đầy đủ Camera & Mic trực tiếp)
Nếu bạn muốn dùng điện thoại ngoài đường (kết nối 4G/5G) bật Camera trực tiếp và thu âm giọng nói:
1. Bạn có thể sử dụng **Cloudflare Quick Tunnel** (hoàn toàn miễn phí, không cần đăng ký tài khoản):
   - Mở PowerShell và chạy:
   ```powershell
   winget install --id Cloudflare.cloudflared
   cloudflared tunnel --url http://localhost:8000
   ```
2. Cloudflare sẽ tạo cho bạn 1 đường link HTTPS (ví dụ: `https://xxx.trycloudflare.com`).
3. Mở link này trên điện thoại ở bất cứ đâu: Camera và Microphone trực tiếp sẽ hoạt động 100%!

### Trường hợp C: Sao chép sang một máy tính khác để chạy độc lập
1. Copy toàn bộ thư mục `NhatKyWeb` sang máy tính mới.
2. Đảm bảo máy tính mới đã cài Python (khuyên dùng Python 3.11).
3. Nhấp đúp chuột vào file `start.bat`. Hệ thống sẽ tự động tạo môi trường và cài đặt các thư viện cần thiết.

---

## 🔑 Cấu Hình AI (Gemini / OpenAI)

Ngay trên giao diện web, nhấn vào nút **"⚙️ Cài đặt AI"** ở góc trên bên phải:
- **Google Gemini (Khuyên Dùng)**:
  - Gemini hỗ trợ đa phương thức tiếp nhận ảnh và âm thanh trực tiếp, phản hồi cực nhanh và hoàn toàn miễn phí.
  - Lấy API Key miễn phí tại: [Google AI Studio](https://aistudio.google.com/app/apikey).
  - Dán API Key vào ô và nhấn **"Kiểm tra kết nối"** &rarr; **"Lưu Cài Đặt"**.
- Nếu bạn chưa nhập API Key, ứng dụng vẫn hoạt động bình thường với cơ chế **Mô phỏng thông minh (Smart Mock)** để bạn trải nghiệm toàn bộ quy trình ngay lập tức.

---

## 📁 Cấu Trúc Thư Mục

```text
D:\Users\NhatKyWeb\
├── app/
│   ├── config.py           # Cấu hình đường dẫn và biến môi trường
│   ├── database.py         # Cơ sở dữ liệu SQLite (Entries, Daily Summaries, Settings)
│   ├── ai_service.py       # Xử lý AI đa phương thức (Gemini, OpenAI, Mock, Daily Summary)
│   ├── main.py             # FastAPI App, định tuyến và phục vụ tĩnh
│   ├── routers/
│   │   ├── entries.py      # CRUD nhật ký, tải ảnh/audio, thống kê
│   │   ├── ai.py           # Endpoint xử lý sự kiện ảnh/voice và tổng kết ngày
│   │   └── settings.py    # Quản lý cài đặt API Key và model
│   └── utils/
│       └── file_storage.py # Lưu trữ và quản lý tệp hình ảnh, tệp âm thanh
├── static/
│   ├── css/style.css       # Giao diện responsive, Dark/Light mode, hiệu ứng timeline
│   └── js/
│       ├── camera.js       # Quản lý bật camera, đổi cam trước/sau, chụp ảnh
│       ├── audio.js        # Ghi âm voice, vẽ sóng âm thanh Canvas, gỡ băng trực tiếp
│       ├── ai.js           # Điều phối gửi ảnh + audio tới AI và nhận kết quả
│       └── app.js          # Khởi tạo, timeline, tìm kiếm, lọc, sửa, xóa, lightbox
├── templates/
│   └── index.html          # Giao diện chính Single Page Application
├── data/
│   ├── database.sqlite3    # Dữ liệu SQLite
│   └── uploads/
│       ├── images/         # Ảnh chụp từ camera hoặc tải lên
│       └── audio/          # Voice ghi âm hoặc tải lên
├── run.py                  # Script chạy máy chủ và tự mở trình duyệt
├── start.bat               # File khởi động nhanh 1 click trên Windows
├── requirements.txt        # Danh sách thư viện Python
└── README.md               # Tài liệu hướng dẫn sử dụng
```
