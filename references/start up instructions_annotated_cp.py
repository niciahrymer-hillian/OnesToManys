"""[FILE] start up instructions_annotated_cp.py

[WHY] One-file launcher for backend + React local development.
[EFFECT] Running this script starts both servers and opens the app URL.
"""

from __future__ import annotations

# [IMPORT] Graceful process cleanup on interpreter exit.
import atexit
# [IMPORT] Process-group signal handling.
import os
import signal
import subprocess
# [IMPORT] Reuse current Python interpreter for backend launch.
import sys
# [IMPORT] Polling/wait loops.
import time
# [IMPORT] Open browser automatically.
import webbrowser
# [IMPORT] Filesystem path management.
from pathlib import Path
# [IMPORT] Lightweight HTTP probe to detect active React URL.
from urllib.request import Request, urlopen

# [CONSTANT] Project root inferred from this file location.
ROOT = Path(__file__).resolve().parent.parent
# [CONSTANT] Backend execution directory.
BACKEND_CWD = ROOT
# [CONSTANT] Frontend execution directory.
FRONTEND_CWD = ROOT / "frontend-react"

# [CONSTANT] Candidate React URLs; Vite can use 5174 if 5173 is occupied.
REACT_URLS = [
    "https://127.0.0.1:5173/",
    "https://127.0.0.1:5174/",
]


def is_url_ready(url: str, timeout: float = 1.5) -> bool:
    """[FUNCTION] Check whether a URL is responsive.

    [WHY] Browser should open only after dev server is ready.
    [EFFECT] Reduces blank/error first load on startup.
    """
    try:
        request = Request(url, method="GET")
        with urlopen(request, timeout=timeout, context=None) as response:  # nosec B310
            return 200 <= response.status < 500
    except Exception:
        return False


def spawn_process(command: list[str], cwd: Path, env: dict[str, str]) -> subprocess.Popen:
    """[FUNCTION] Start child process in a dedicated process group.

    [WHY] Grouped processes can be stopped cleanly with one signal.
    [EFFECT] Ctrl+C reliably shuts down backend/frontend and child workers.
    """
    return subprocess.Popen(  # noqa: S603
        command,
        cwd=str(cwd),
        env=env,
        start_new_session=True,
    )


def terminate_process_tree(proc: subprocess.Popen | None) -> None:
    """[FUNCTION] Terminate a process group with TERM then KILL fallback."""
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
    """[FUNCTION] Return first reachable React URL within timeout window."""
    deadline = time.time() + max_wait_seconds
    while time.time() < deadline:
        for url in REACT_URLS:
            if is_url_ready(url):
                return url
        time.sleep(0.5)
    return None


def main() -> int:
    """[FUNCTION] Launch servers, open browser, then keep session alive."""
    if not FRONTEND_CWD.exists():
        print(f"Missing frontend folder: {FRONTEND_CWD}")
        return 1

    env = os.environ.copy()

    backend_proc: subprocess.Popen | None = None
    frontend_proc: subprocess.Popen | None = None

    def cleanup() -> None:
        """[DELEGATE] Ensure both spawned servers are stopped on exit."""
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
            # [WHY] If one process exits, stop launcher to avoid half-broken state.
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
    # [ENTRYPOINT] Run launcher as a CLI script.
    raise SystemExit(main())
