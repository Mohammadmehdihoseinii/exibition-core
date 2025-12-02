import os
import sys
import subprocess
import signal
import psutil
import time
from dotenv import load_dotenv
import logging
import platform
import shutil

# ----------------- Load .env -----------------
load_dotenv()

# ----------------- Logger -----------------
logger = logging.getLogger("run_api")
if not logger.handlers:
    handler = logging.StreamHandler()
    handler.setFormatter(logging.Formatter("[%(levelname)s] %(message)s"))
    logger.addHandler(handler)
logger.setLevel(logging.INFO)

# ----------------- Config -----------------
API_PORT = int(os.getenv("apiPort", 8000))
FASTAPI_APP = os.getenv("FASTAPI_APP", "interface.api.main:app")
USE_RELOAD = os.getenv("USE_RELOAD", "false").lower() == "true"

process = None


# ----------------- Find uvicorn path cross-platform -----------------
def find_uvicorn():
    """
    پیدا کردن uvicorn.exe یا uvicorn.
    اول .venv را چک می‌کند.
    اگر نبود، از PATH پیدا می‌کند.
    """

    if platform.system() == "Windows":
        venv_path = ".\\.venv\\Scripts\\uvicorn.exe"
    else:
        venv_path = "./.venv/bin/uvicorn"

    if os.path.exists(venv_path):
        return venv_path

    uvicorn_in_path = shutil.which("uvicorn")
    if uvicorn_in_path:
        return uvicorn_in_path

    logger.error("❌ uvicorn not found! Install it or set UVICORN_PATH manually.")
    sys.exit(1)

UVICORN_PATH = os.getenv("UVICORN_PATH") or find_uvicorn()


# ----------------- Free Port -----------------
def free_port(port: int):
    logger.info(f"Cleaning port {port}...")

    for proc in psutil.process_iter(["pid", "name"]):
        try:
            for conn in proc.connections(kind="inet"):
                if conn.laddr and conn.laddr.port == port:
                    proc.terminate()
                    time.sleep(0.3)
                    if proc.is_running():
                        proc.kill()
                    break
        except (psutil.NoSuchProcess, psutil.AccessDenied, psutil.ZombieProcess):
            continue


# ----------------- Start FastAPI -----------------
def start_fastapi():
    global process

    free_port(API_PORT)

    cmd = [
        UVICORN_PATH,
        FASTAPI_APP,
        "--host", "0.0.0.0",
        "--port", str(API_PORT)
    ]

    if USE_RELOAD:
        logger.info("🔄 Auto reload mode ENABLED")
        cmd.append("--reload")
    else:
        logger.info("🚀 Auto reload mode DISABLED (production mode)")

    logger.info(f"Starting FastAPI using: {UVICORN_PATH}")

    try:
        process = subprocess.Popen(cmd)
        logger.info(f"FastAPI started (PID: {process.pid})")
    except Exception as e:
        logger.error(f"Failed to start FastAPI: {e}")
        sys.exit(1)


# ----------------- Cleanup -----------------
def cleanup(*_):
    global process

    try:
        free_port(API_PORT)

        if process and process.poll() is None:
            logger.info(f"Terminating PID {process.pid}")
            process.terminate()
            time.sleep(0.5)
            if process.poll() is None:
                process.kill()
    except Exception as e:
        logger.error(f"Cleanup error: {e}")

    logger.info("Shutting down...")
    sys.exit(0)


# ----------------- Main -----------------
def main():
    signal.signal(signal.SIGINT, cleanup)
    signal.signal(signal.SIGTERM, cleanup)

    start_fastapi()

    logger.info(f"Server running at http://localhost:{API_PORT}")
    logger.info("Press CTRL+C to stop.")

    while True:
        time.sleep(1)


if __name__ == "__main__":
    main()
