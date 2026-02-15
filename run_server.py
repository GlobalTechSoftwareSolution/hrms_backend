#!/usr/bin/env python3
import os
import sys
from pathlib import Path

# Add the hrms directory to the path
hrms_dir = Path(__file__).parent / 'hrms'
sys.path.insert(0, str(hrms_dir))

# Load environment variables from .env file
from dotenv import load_dotenv
env_path = Path(__file__).parent / '.env'
load_dotenv(dotenv_path=env_path)

# Change to hrms directory
os.chdir(hrms_dir)

# Run Django management command
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'hrms.settings')

from django.core.management import execute_from_command_line

if __name__ == '__main__':
    execute_from_command_line(sys.argv)
