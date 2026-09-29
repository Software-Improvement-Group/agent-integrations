import os
import subprocess
import sys

# Sigrid CI only reads SIGRID_CI_TOKEN; this lets users who export SIGRID_TOKEN run it too.
env = dict(os.environ)
if not env.get("SIGRID_CI_TOKEN") and env.get("SIGRID_TOKEN"):
    env["SIGRID_CI_TOKEN"] = env["SIGRID_TOKEN"]

agents_py = sys.argv[1]
sys.exit(subprocess.run([sys.executable, agents_py] + sys.argv[2:], env=env).returncode)
