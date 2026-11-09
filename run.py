import sys
import webbrowser
import threading
import time
import uvicorn

def open_browser():
    time.sleep(1.5)
    url = "http://localhost:8000"
    print(f"\n[INFO] Đang mở trình duyệt: {url}\n")
    try:
        webbrowser.open(url)
    except Exception as e:
        print(f"[WARN] Không thể tự động mở trình duyệt: {e}")

if __name__ == "__main__":
    print("=" * 60)
    print("   NHAT KY WEB - NHAT KY AI THUC THOI (MULTIMODAL)")
    print("   Web viet nhat ky bang Chu, Am thanh, Hinh anh & AI")
    print("=" * 60)
    print("-> May chu dang khoi chay tai: http://localhost:8000")
    print("-> Nhan Ctrl+C de dung may chu.\n")
    
    # Launch browser in separate thread
    threading.Thread(target=open_browser, daemon=True).start()
    
    uvicorn.run("app.main:app", host="127.0.0.1", port=8000, reload=False)
