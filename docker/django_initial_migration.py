#!/usr/bin/env python

"""
Script for running initial database setup within a container
"""

import discover
import subprocess

def main():
    discover.set_django_env()
    subprocess.check_call(["python", "manage.py", "migrate"])
    subprocess.check_call(["python", "manage.py", "createsuperuser"])

if __name__ == '__main__':
    main()
