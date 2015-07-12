#!/usr/bin/env python3

"""
Start Docker containers for a PostgreSQL instance of Django.
This is designed to be more suitable for a production deployment.
"""

import logging
import random
import re
import subprocess
import sys
import time

secret_key_legal_chars = 'abcdefghijklmnopqrstuvwxyz0123456789!@#$%^&*(-_=+)'

def create_pg_container(pg_container_name):
    """
    Create a new PostgreSQL container
    """
    pg_user = 'jianjin'
    r = random.SystemRandom()
    pg_password = ''.join((r.choice([chr(x) for x in list(range(48,58)) + list(range(65, 91)) + list(range(97, 123))])
                           for i in range(20)))
    logging.info("Starting PostgreSQL container...")
    subprocess.check_call(["sudo", "docker", "run", "--name", pg_container_name,
                           "-e", "POSTGRES_USER={0}".format(pg_user),
                           "-e", "POSTGRES_PASSWORD={0}".format(pg_password),
                           "-d", "postgres"])
    logging.info("Sleeping to allow PostgreSQL time to start up...")
    time.sleep(5)
    logging.info("Done")

def django_command(command_to_run, pg_container_name, allowed_hosts,
                   secret_key=None, name=None, daemon=False, django_debug=False):
    """
    Run command in a Django container
    """
    command = ["sudo", "docker", "run"]

    if daemon:
        command.extend(["-p", "8000", "-d"])
    else:
        command.extend(["--rm", "-t", "-i"])

    if name:
        command.extend(["--name", name])

    command.extend(["-e", "DJANGO_DEBUG={0}".format('1' if django_debug else '0')])
#    command.extend(["-e", "GUNICORN_DEBUG=1"])

    if not secret_key:
        r = random.SystemRandom()
        secret_key = ''.join((r.choice(secret_key_legal_chars) for i in range(50)))

    command.extend(["-e", "DJANGO_SECRET_KEY={0}".format(secret_key)])
    command.extend(["-e", "ALLOWED_HOSTS={0}".format(allowed_hosts)])

    command.extend(["--link", "{0}:postgres".format(pg_container_name)])

    command.append("jianjin/django")
    command.extend(command_to_run)

    logging.info("Starting {0}".format(" ".join(command)))
    subprocess.check_call(command)

def pg_initial_migration(pg_container_name):
    """
    Perform initial setup of the database
    """
    logging.info("Starting container to perform migrations")
    django_command(["docker/django_initial_migration.py"], pg_container_name, "")

def create_django_container(pg_container_name, allowed_hosts, debug):
    logging.info("Starting Django container")
    if not allowed_hosts:
        raise ValueError("--allowedhosts is required")
    container_name = "jianjin_django"
    django_command(["docker/django_start.py"], pg_container_name, allowed_hosts,
                   name=container_name, daemon=True, django_debug=debug)
    url = subprocess.check_output(["sudo", "docker", "port", container_name, "8000"])
    logging.info("You may connect at {0}".format(url))

def main(create_pg=True, init_migration=True, create_django=True, debug=False, allowed_hosts=""):
    logging.basicConfig(format='%(asctime)s %(message)s', level=logging.INFO)
    pg_container_name = 'jianjin_postgres'

    did_something = False

    if create_pg:
        create_pg_container(pg_container_name)
        did_something = True

    if init_migration:
        pg_initial_migration(pg_container_name)
        did_something = True

    if create_django:
        create_django_container(pg_container_name, allowed_hosts, debug)
        did_something = True

    if not did_something:
        print("Must specify at least one of createpostgres, initmigration, createdjango", file=sys.stderr)

if __name__ == '__main__':
    allowed_hosts = [m.group(1) for m in (re.match("--allowedhosts=(.*)", arg) for arg in sys.argv) if m]
    allowed_hosts = allowed_hosts[0] if len(allowed_hosts) > 0 else None
    main(create_pg='createpostgres' in sys.argv,
         init_migration='initmigration' in sys.argv,
         create_django='createdjango' in sys.argv,
         debug='--debug' in sys.argv,
         allowed_hosts=allowed_hosts)
