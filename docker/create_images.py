#!/usr/bin/env python3

"""
Create Docker images required to run Jianjin.

This file assumes you have Docker installed and the Docker daemon running,
and that you have sudo permissions to run docker as the current user.
For more information, read the documentation at http://www.docker.com/.
"""

import subprocess
import sys

def build_base(tag):
    image_name = "jianjin/base:{0}".format(tag)
    subprocess.check_call(["sudo", "docker", "build",
                           "-t", image_name,
                           "-f", "Dockerfile.base", "."])
    # Tag it as latest so that the next step picks it up (not sure if there's a better way)
    subprocess.check_call(["sudo", "docker", "tag", "-f", image_name, "jianjin/base:latest"])

def build_django(tag):
    image_name = "jianjin/django:{0}".format(tag)
    subprocess.check_call(["sudo", "docker", "build", "-t", image_name,
                           "-f", "Dockerfile.django", ".."])
    subprocess.check_call(["sudo", "docker", "tag", "-f", image_name, "jianjin/django:latest"])

def main():
    legal_commands = ['buildbase', 'builddjango']
    tags = [t for t in sys.argv[1:] if t not in legal_commands]
    if len(tags) > 1:
        raise ValueError('Expected at most one tag, found {0}'.format(", ".join(tags)))
    tag = tags[0] if tags else '1'

    did_something = False
    if 'buildbase' in sys.argv:
        build_base(tag)
        did_something = True
    if 'builddjango' in sys.argv:
        build_django(tag)
        did_something = True

    if not did_something:
        print("Must specify at least one of {0}".format(", ".join(legal_commands)), file=sys.stderr)

if __name__ == '__main__':
    main()
