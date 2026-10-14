import subprocess
import sys
import os
import time
import signal

def main():
    root_dir = os.path.dirname(os.path.abspath(__file__))
    backend_dir = os.path.join(root_dir, "backend")
    frontend_dir = os.path.join(root_dir, "frontend")

    print("=" * 60)
    print("🧬 BioLens AI - Protein & Hastalık Araştırma Platformu")
    print("=" * 60)
    print("Backend ve Frontend servisleri başlatılıyor...\n")

    # Start FastAPI backend
    backend_cmd = [sys.executable, "-m", "uvicorn", "main:app", "--host", "127.0.0.1", "--port", "8000", "--reload"]
    backend_proc = subprocess.Popen(backend_cmd, cwd=backend_dir)
    print("✓ Backend başlatıldı: http://127.0.0.1:8000 (API & Docs: /docs)")

    # Start Frontend
    frontend_cmd = ["npm", "run", "dev"]
    frontend_proc = subprocess.Popen(frontend_cmd, cwd=frontend_dir)
    print("✓ Frontend başlatıldı: http://localhost:5173\n")

    def shutdown(sig, frame):
        print("\nBioLens AI servisleri kapatılıyor...")
        backend_proc.terminate()
        frontend_proc.terminate()
        sys.exit(0)

    signal.signal(signal.SIGINT, shutdown)
    signal.signal(signal.SIGTERM, shutdown)

    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        shutdown(None, None)

if __name__ == "__main__":
    main()
