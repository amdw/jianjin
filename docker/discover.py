"""
Library to facilitate discovery of services from within containers
"""

import os

def get_postgres_url():
    user = os.environ["POSTGRES_ENV_POSTGRES_USER"]
    password = os.environ["POSTGRES_ENV_POSTGRES_PASSWORD"]
    host = os.environ["POSTGRES_PORT_5432_TCP_ADDR"]
    port = os.environ["POSTGRES_PORT_5432_TCP_PORT"]
    return "postgres://{0}:{1}@{2}:{3}/{0}".format(user, password, host, port)

def set_django_env():
    postgres_url = get_postgres_url()
    secret_key = os.environ["DJANGO_SECRET_KEY"]
    debug = os.environ.get("DJANGO_DEBUG", "0")

    os.environ.update({"DATABASE_URL": postgres_url,
                       "DJANGO_SECRET_KEY": secret_key,
                       "DJANGO_DEBUG": debug})
