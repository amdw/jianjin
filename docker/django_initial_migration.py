#!/usr/bin/env python3

"""
Script for running initial database setup within a container
"""

import subprocess
import discover

def main():
    discover.set_django_env()
    subprocess.check_call(["python3", "manage.py", "migrate"])
    subprocess.check_call(["python3", "manage.py", "createsuperuser"])

if __name__ == '__main__':
    main()
