#!/usr/bin/env python

"""
Script to generate and set certain required configuration variables
for a deployment of Jianjin on Heroku. See README.md for further information.
"""

import random
import subprocess 

secret_key_legal_chars = 'abcdefghijklmnopqrstuvwxyz0123456789!@#$%^&*(-_=+)'
r = random.SystemRandom()
secret_key = ''.join((r.choice(secret_key_legal_chars) for i in range(50)))

print("Setting Heroku config variables...")

# Set the secret key, and force the Python build pack, since there are some Node configs
# in the root directory as well and this confuses Heroku
subprocess.check_call(["heroku", "config:set", "DJANGO_SECRET_KEY='{0}'".format(secret_key),
                       "BUILDPACK_URL=https://github.com/heroku/heroku-buildpack-python"])

