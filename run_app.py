#!/usr/bin/env python3
import subprocess
import sys
import os
import time
import signal
import shutil
import webbrowser


def ensure_path():
    """Finder üzerinden çift tıklayarak çalıştırıldığında Homebrew yollarını PATH'e ekler."""
    extra_paths = ["/opt/homebrew/bin", "/usr/local/bin"]
    current_path = os.environ.get("PATH", "")
    for p in extra_paths:
        if os.path.exists(p) and p not in current_path:
            current_path = f"{p}:{current_path}"
    os.environ["PATH"] = current_path


def get_venv_python(venv_dir: str) -> str:
    if os.name == "nt":
        return os.path.join(venv_dir, "Scripts", "python.exe")
    python3_path = os.path.join(venv_dir, "bin", "python3")
    if os.path.exists(python3_path):
        return python3_path
    return os.path.join(venv_dir, "bin", "python")


def ensure_backend_env(root_dir: str, backend_dir: str) -> str:
    venv_dir = os.path.join(root_dir, ".venv")
    venv_python = get_venv_python(venv_dir)

    if not os.path.exists(venv_python):
        print("⚙️  Python sanal ortamı (.venv) oluşturuluyor...")
        subprocess.check_call([sys.executable, "-m", "venv", venv_dir])
        venv_python = get_venv_python(venv_dir)

    check_cmd = [venv_python, "-c", "import fastapi, uvicorn, requests, pydantic"]
    res = subprocess.run(check_cmd, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    if res.returncode != 0:
        print("📦 Backend Python bağımlılıkları kuruluyor (requirements.txt)...")
        req_file = os.path.join(backend_dir, "requirements.txt")
        subprocess.check_call([venv_python, "-m", "pip", "install", "-r", req_file])

    return venv_python


def ensure_frontend_env(frontend_dir: str) -> str:
    npm_cmd = shutil.which("npm") or ("npm.cmd" if os.name == "nt" else "/opt/homebrew/bin/npm")
    node_modules = os.path.join(frontend_dir, "node_modules")
    if not os.path.exists(node_modules):
        print("📦 Frontend bağımlılıkları kuruluyor (npm install)...")
        subprocess.check_call([npm_cmd, "install"], cwd=frontend_dir)
    return npm_cmd


def main():
    ensure_path()
    root_dir = os.path.dirname(os.path.abspath(__file__))
    backend_dir = os.path.join(root_dir, "backend")
    frontend_dir = os.path.join(root_dir, "frontend")

    print("=" * 60)
    print("🧬 BioLens AI - Protein & Hastalık Araştırma Platformu")
    print("=" * 60)

    try:
        venv_python = ensure_backend_env(root_dir, backend_dir)
        npm_cmd = ensure_frontend_env(frontend_dir)
    except Exception as e:
        print(f"\n❌ Ortam hazırlanırken hata oluştu: {e}")
        sys.exit(1)

    print("Backend ve Frontend servisleri başlatılıyor...\n")

    env = os.environ.copy()
    env["PYTHONWARNINGS"] = "ignore"

    # Start FastAPI backend
    backend_cmd = [
        venv_python, "-m", "uvicorn", "main:app",
        "--host", "127.0.0.1", "--port", "8000", "--reload"
    ]
    backend_proc = subprocess.Popen(backend_cmd, cwd=backend_dir, env=env)
    print("✓ Backend başlatıldı:  http://127.0.0.1:8000 (API Docs: /docs)")

    # Start Frontend on port 3000
    frontend_cmd = [npm_cmd, "run", "dev", "--", "--port", "3000"]
    frontend_proc = subprocess.Popen(frontend_cmd, cwd=frontend_dir, env=env)
    frontend_url = "http://localhost:3000"
    print(f"✓ Frontend başlatıldı: {frontend_url}\n")

    # Open browser automatically after a short delay
    time.sleep(1.0)
    try:
        if sys.platform == "darwin":
            subprocess.Popen(["open", frontend_url], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        else:
            webbrowser.open(frontend_url)
    except Exception:
        pass

    def shutdown(sig, frame):
        print("\nBioLens AI servisleri kapatılıyor...")
        for proc in (backend_proc, frontend_proc):
            if proc.poll() is None:
                proc.terminate()
        sys.exit(0)

    signal.signal(signal.SIGINT, shutdown)
    signal.signal(signal.SIGTERM, shutdown)

    try:
        while True:
            if backend_proc.poll() is not None:
                print("\n⚠️ Backend servisi beklenmedik şekilde durdu.")
                shutdown(None, None)
            if frontend_proc.poll() is not None:
                print("\n⚠️ Frontend servisi beklenmedik şekilde durdu.")
                shutdown(None, None)
            time.sleep(1)
    except KeyboardInterrupt:
        shutdown(None, None)


if __name__ == "__main__":
    main()
