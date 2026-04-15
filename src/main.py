import sys

from cli import run as run_cli
from server import run_server


if __name__ == "__main__":
    if "--cli" in sys.argv:
        run_cli()
    else:
        run_server()
