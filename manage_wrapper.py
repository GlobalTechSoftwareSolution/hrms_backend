#!/usr/bin/env python3
import os
import sys
from pathlib import Path
import subprocess

# Read .env file and get environment variables
env_file = Path(__file__).parent / '.env'
env_vars = os.environ.copy()

if env_file.exists():
    with open(env_file, 'r') as f:
        for line in f:
            line = line.strip()
            if line and not line.startswith('#'):
                if '=' in line:
                    key, value = line.split('=', 1)
                    env_vars[key] = value

# Change to hrms directory
hrms_dir = Path(__file__).parent / 'hrms'
os.chdir(hrms_dir)

# Run django manage.py with the environment variables
args = [sys.executable, 'manage.py'] + sys.argv[1:]
result = subprocess.run(args, env=env_vars)
sys.exit(result.returncode)
