"""
DataMind AI Agent Launcher
Launches the FastAPI server and automatically opens the user interface in the default browser.
"""
import sys
import time
import webbrowser
import threading
import uvicorn

def open_browser():
    time.sleep(1.8)
    print("\n[DataMind AI Agent] Đang mở giao diện trên trình duyệt tại: http://localhost:8000 ...")
    webbrowser.open("http://localhost:8000")

if __name__ == "__main__":
    print("=" * 65)
    print("       DataMind AI Agent - Hệ Thống Phân Tích Dữ Liệu Thông Minh")
    print("=" * 65)
    print(" [1] Quy trình: Nạp dữ liệu -> Chẩn đoán -> Người dùng duyệt -> EDA -> Báo cáo HTML")
    print(" [2] Giao diện trực tiếp tại: http://localhost:8000")
    print(" [3] Nhấn Ctrl+C để dừng hệ thống bất kỳ lúc nào.\n")

    threading.Thread(target=open_browser, daemon=True).start()
    uvicorn.run("app.main:app", host="127.0.0.1", port=8000, reload=False, log_level="info")
