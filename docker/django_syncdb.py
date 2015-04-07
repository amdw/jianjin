#!/usr/bin/env python

"""
Script for running syncdb within a container
"""

import discover
import subprocess

def main():
    discover.set_django_env()
    subprocess.check_call(["python", "manage.py", "syncdb"])

if __name__ == '__main__':
    main()
