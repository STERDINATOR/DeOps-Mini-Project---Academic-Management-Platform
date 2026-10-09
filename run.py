"""Application entrypoint for Academic Management Platform."""

import os
import sys
from app import create_app

app = create_app()

if __name__ == "__main__":
    # Default to port 5000 as per specification, or use PORT env var
    port = int(os.environ.get("PORT", 5000))
    host = "0.0.0.0"

    # Support command line arguments such as --port or -p
    args = sys.argv[1:]
    for i, arg in enumerate(args):
        if arg in ("--port", "-p") and i + 1 < len(args):
            try:
                port = int(args[i + 1])
            except ValueError:
                pass
        elif arg.startswith("--port="):
            try:
                port = int(arg.split("=")[1])
            except ValueError:
                pass
        elif arg in ("--host", "-h") and i + 1 < len(args):
            host = args[i + 1]
        elif arg.startswith("--host="):
            host = arg.split("=")[1]

    print(
        f"* Academic Management Platform starting on http://{host}:{port}"
    )
    app.run(host=host, port=port, debug=False)
