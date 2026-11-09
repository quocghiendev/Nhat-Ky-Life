import sys
import socket
import webbrowser
import threading
import time
import uvicorn

def get_local_ip():
    """Lấy địa chỉ IP nội bộ trong mạng LAN / Wi-Fi"""
    try:
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        s.connect(("8.8.8.8", 80))
        ip = s.getsockname()[0]
        s.close()
        return ip
    except Exception:
        return "127.0.0.1"

def open_browser():
    time.sleep(1.5)
    url = "http://localhost:8000"
    print(f"[INFO] Đang mở trình duyệt trên máy này: {url}\n")
    try:
        webbrowser.open(url)
    except Exception as e:
        print(f"[WARN] Không thể tự động mở trình duyệt: {e}")

if __name__ == "__main__":
    local_ip = get_local_ip()
    port = 8000
    
    print("=" * 65)
    print("   NHAT KY WEB - NHAT KY AI THUC THOI (MULTIMODAL)")
    print("   Web viet nhat ky bang Chu, Am thanh, Hinh anh & AI")
    print("=" * 65)
    print(f"-> Truy cap tren may nay:           http://localhost:{port}")
    print(f"-> Truy cap tu may khac / dien thoai: http://{local_ip}:{port}")
    print("=" * 65)
    print("[MEO QUAN TRONG CHO DIEN THOAI / MAY KHAC]:")
    print("Trinh duyet yeu cau HTTPS de cho phep Camera & Ghi am Micro khi dung IP.")
    print("De dien thoai bat duoc Camera/Mic, xem huong dan chi tiet trong README.md")
    print("hoac dung link HTTPS an toan (Cloudflare Tunnel / Ngrok).")
    print("=" * 65)
    print("-> Nhan Ctrl+C de dung may chu.\n")
    
    # Launch browser locally in separate thread
    threading.Thread(target=open_browser, daemon=True).start()
    
    # Bind to 0.0.0.0 so other devices on LAN/Wi-Fi can access
    uvicorn.run("app.main:app", host="0.0.0.0", port=port, reload=False)
