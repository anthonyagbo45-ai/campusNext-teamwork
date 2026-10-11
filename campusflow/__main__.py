import sys

from campusflow.cli import run

run(sys.argv[1] if len(sys.argv) > 1 else "tickets.json")
