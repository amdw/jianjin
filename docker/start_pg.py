#!/usr/bin/env python

"""
Start Docker containers for a PostgreSQL instance of Django.
This is designed to be more suitable for a production deployment.
"""

import random
import subprocess
import time

secret_key_legal_chars = 'abcdefghijklmnopqrstuvwxyz0123456789!@#$%^&*(-_=+)'

def make_pg_url(user, password, hostname, port):
    return "postgres://{0}:{1}@{2}:{3}/{0}".format(user, password, hostname, port)

def discover_pg_url(container_name, user, password):
    ip_address = subprocess.check_output(["sudo", "docker", "inspect",
                                          "-f", "{{ .NetworkSettings.IPAddress }}",
                                          container_name]).strip()
    return make_pg_url(user, password, ip_address, "5432")

def create_pg_container(pg_container_name, pg_user, pg_password):
    """
    Create a new PostgreSQL container
    """
    subprocess.check_call(["sudo", "docker", "run", "--name", pg_container_name,
                           "-e", "POSTGRES_USER={0}".format(pg_user),
                           "-e", "POSTGRES_PASSWORD={0}".format(pg_password),
                           "-d", "postgres"])
    # Annoying, but need to give Postgres some time to start up...
    time.sleep(10)

def django_command(command_to_run, pg_container_name, pg_user, pg_password,
                   secret_key=None, name=None, daemon=False, django_debug=False):
    """
    Run command in a Django container
    """
    command = ["sudo", "docker", "run"]
    if name:
        command.extend(["--name", name])

    command.extend(["-e", "DJANGO_DEBUG={0}".format('1' if django_debug else '0')])

    if not secret_key:
        r = random.SystemRandom()
        secret_key = ''.join((r.choice(secret_key_legal_chars) for i in range(50)))

    command.extend(["-e", "DJANGO_SECRET_KEY={0}".format(secret_key)])

    pg_url = discover_pg_url(pg_container_name, pg_user, pg_password)
    print "Discovered PG URL {0} from {1}".format(pg_url, pg_container_name)
    command.extend(["-e", "DATABASE_URL={0}".format(pg_url)])

    if daemon:
        command.extend(["-p", "8000", "-d"])
    else:
        command.extend(["--rm", "-t", "-i"])

    command.append("jianjin/django")
    command.extend(command_to_run)

    subprocess.check_call(command)

def pg_syncdb(pg_container_name, pg_user, pg_password):
    """
    Call syncdb to perform initial setup of the database
    """
    pg_url = discover_pg_url(pg_container_name, pg_user, pg_password)
    django_command(["python", "manage.py", "syncdb"], pg_container_name, pg_user, pg_password)

def main(debug=False):
    pg_container_name = 'jianjin_postgres'
    pg_user = 'jianjin'
    r = random.SystemRandom()
    pg_password = ''.join((r.choice([chr(x) for x in range(48,58) + range(65, 91) + range(97, 123)])
                           for i in range(20)))
    # TODO This should really be optional as it might already exist
    create_pg_container(pg_container_name, pg_user, pg_password)
    # TODO This should be optional too
    pg_syncdb(pg_container_name, pg_user, pg_password)
    # TODO Parameterise some of these pieces especially django_debug
    django_command(["python", "manage.py", "runserver", "0.0.0.0:8000"],
                   pg_container_name, pg_user, pg_password,
                   name="jianjin_django", daemon=True, django_debug=True)

if __name__ == '__main__':
    main()
