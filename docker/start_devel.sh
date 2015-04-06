#!/bin/bash

# Start the set of Docker containers necessary for a local development environment using Sqlite.
# This assumes you have created the Docker images using create_images.sh and that Docker is set up.

TAG=${1:-1}

THIS_SCRIPT=`realpath $0`
OURDIR=`dirname $THIS_SCRIPT`
BASEDIR=`dirname $OURDIR`

# Override the container's /code with the working copy using -v.
# This way, code changes we make on the host are also reflected in the container.
# This requires --privileged=true.

sudo docker run -d -p 8000 --name jianjin_django_dev --env-file=devel.env \
     -v $BASEDIR:/code --privileged=true jianjin/django:$TAG \
     python manage.py runserver 0.0.0.0:8000
