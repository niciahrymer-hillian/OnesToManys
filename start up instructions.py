#!/usr/bin/env python3
"""Launch backend + React frontend, then open the app in a browser.

WHY: One command startup for daily local development.
EFFECT: Starts required dev servers and opens the first reachable React URL.
"""

from __future__ import annotations

import atexit
import os
import signal
import subprocess
import sys
import time
import webbrowser
from pathlib import Path
from urllib.request import Request, urlopen

ROOT = Path(__file__).resolve().parent
BACKEND_CWD = ROOT
FRONTEND_CWD = ROOT / "frontend-react"

REACT_URLS = [
    "https://127.0.0.1:5173/",
    "https://127.0.0.1:5174/",
]


def is_url_ready(url: str, timeout: float = 1.5) -> bool:
    """Return True when a URL responds with an HTTP status code."""
    try:
        request = Request(url, method="GET")
        with urlopen(request, timeout=timeout, context=None) as response:  # nosec B310
            return 200 <= response.status < 500
    except Exception:
        return False


def spawn_process(command: list[str], cwd: Path, env: dict[str, str]) -> subprocess.Popen:
    """Start a child process in a new process group for clean shutdown."""
    return subprocess.Popen(  # noqa: S603
        command,
        cwd=str(cwd),
        env=env,
        start_new_session=True,
    )


def terminate_process_tree(proc: subprocess.Popen | None) -> None:
    """Terminate a launched process and its subprocesses."""
    if not proc or proc.poll() is not None:
        return

    try:
        os.killpg(proc.pid, signal.SIGTERM)
        proc.wait(timeout=5)
    except Exception:
        try:
            os.killpg(proc.pid, signal.SIGKILL)
        except Exception:
            pass


def wait_for_react_url(max_wait_seconds: int = 60) -> str | None:
    """Return the first reachable React URL within the wait window."""
    deadline = time.time() + max_wait_seconds
    while time.time() < deadline:
        for url in REACT_URLS:
            if is_url_ready(url):
                return url
        time.sleep(0.5)
    return None


def main() -> int:
    if not FRONTEND_CWD.exists():
        print(f"Missing frontend folder: {FRONTEND_CWD}")
        return 1

    env = os.environ.copy()

    backend_proc: subprocess.Popen | None = None
    frontend_proc: subprocess.Popen | None = None

    def cleanup() -> None:
        terminate_process_tree(frontend_proc)
        terminate_process_tree(backend_proc)

    atexit.register(cleanup)

    try:
        print("Starting backend (app.py)...")
        backend_proc = spawn_process([sys.executable, "app.py"], BACKEND_CWD, env)

        print("Starting frontend (npm run dev)...")
        frontend_proc = spawn_process(["npm", "run", "dev"], FRONTEND_CWD, env)

        print("Waiting for React dev server...")
        react_url = wait_for_react_url()
        if react_url:
            print(f"Opening {react_url}")
            webbrowser.open(react_url)
        else:
            print("React URL was not reachable in time. Check terminal output.")

        print("\nServers are running. Press Ctrl+C to stop both.")
        while True:
            # Exit if either process dies unexpectedly.
            if backend_proc.poll() is not None:
                print("Backend exited. Stopping launcher.")
                return backend_proc.returncode or 1
            if frontend_proc.poll() is not None:
                print("Frontend exited. Stopping launcher.")
                return frontend_proc.returncode or 1
            time.sleep(1)

    except KeyboardInterrupt:
        print("\nShutting down...")
        return 0


if __name__ == "__main__":
    raise SystemExit(main())
