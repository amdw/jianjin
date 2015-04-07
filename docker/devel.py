#!/usr/bin/env python

"""
Start the set of Docker containers necessary for a local development environment using Sqlite.
This assumes you have created the Docker images using create_images.sh and that Docker is set up.
"""

import logging
import os.path
import subprocess
import sys

def run_server(container_name, tag, base_dir):
    # Override the container's /code with the working copy using -v.
    # This way, code changes we make on the host are also reflected in the container.
    # This requires --privileged=true.
    subprocess.check_call(["sudo", "docker", "run", "-d", "-p", "8000", "--name", container_name,
                           "--env-file=devel.env",
                           "-v", "{0}:/code".format(base_dir),
                           "--privileged=true", "jianjin/django:{0}".format(tag),
                           "python", "manage.py", "runserver", "0.0.0.0:8000"])
    url = subprocess.check_output(["sudo", "docker", "port", container_name, "8000"])
    logging.info("You may connect on {0}".format(url))

def run_command(tag, base_dir, command):
    parts = ["sudo", "docker", "run", "--rm", "-ti",
             "--env-file=devel.env",
             "-v", "{0}:/code".format(base_dir),
             "--privileged=true", "jianjin/django:{0}".format(tag)]
    parts.extend(command)
    logging.info("Running {0}".format(" ".join(parts)))
    subprocess.check_call(parts)

def run_tests(tag, base_dir):
    run_command(tag, base_dir, ["python", "manage.py", "test", "words"])

def run_syncdb(tag, base_dir):
    run_command(tag, base_dir, ["python", "manage.py", "syncdb"])
    
def main():
    logging.basicConfig(format='%(asctime)s %(message)s', level=logging.INFO)
    legal_commands = ["run", "syncdb", "test"]
    tags = [arg for arg in sys.argv[1:] if arg not in legal_commands]
    if len(tags) > 1:
        raise ValueError("Expected at most one tag, found {0}".format(tags))
    tag = tags[0] if tags else 'latest'
    base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

    did_something = False
    
    if "run" in sys.argv:
        run_server("jianjin_django_dev", tag, base_dir)
        did_something = True

    if "syncdb" in sys.argv:
        run_syncdb(tag, base_dir)
        did_something = True
        
    if "test" in sys.argv:
        run_tests(tag, base_dir)
        did_something = True

    if not did_something:
        print >>sys.stderr, "Must specify at least one of {0}".format(", ".join(legal_commands))

if __name__ == '__main__':
   main()

