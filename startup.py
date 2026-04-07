"""
Railway startup script – replaces entrypoint.sh to avoid CRLF issues on Windows.
Runs migrate (best-effort), then exec's daphne.
"""

import os
import subprocess
import sys


def main():
    port = os.environ.get("PORT", "8000")

    print("=== Railway Startup ===", flush=True)
    print(f"PORT={port}", flush=True)
    print(f"DEBUG={os.environ.get('DEBUG', 'not set')}", flush=True)
    print(
        f"DATABASE_URL is {'SET' if os.environ.get('DATABASE_URL') else 'NOT SET'}",
        flush=True,
    )
    print(
        f"REDIS_URL is {'SET' if os.environ.get('REDIS_URL') else 'NOT SET'}",
        flush=True,
    )
    print(
        f"SECRET_KEY is {'SET' if os.environ.get('SECRET_KEY') else 'NOT SET'}",
        flush=True,
    )

    # Run migrations – best-effort, never block startup
    print("--- Running migrations ---", flush=True)
    result = subprocess.run(
        [sys.executable, "manage.py", "migrate", "--noinput"],
        check=False,
    )
    if result.returncode != 0:
        print("WARNING: migrate failed (DB may not be provisioned yet)", flush=True)

    # Collect static files – best-effort
    print("--- Collecting static files ---", flush=True)
    result = subprocess.run(
        [sys.executable, "manage.py", "collectstatic", "--noinput"],
        check=False,
    )
    if result.returncode != 0:
        print("WARNING: collectstatic failed", flush=True)

    # Replace this process with daphne (exec – same PID, proper signal handling)
    print(f"--- Starting Daphne on port {port} ---", flush=True)
    os.execvp(
        "daphne",
        ["daphne", "-b", "0.0.0.0", "-p", port, "config.asgi:application"],
    )


if __name__ == "__main__":
    main()
