#!/bin/bash

# Create Docker images required to run Jianjin.

# This file assumes you have Docker installed and the Docker daemon running,
# and that you have sudo permissions to run docker as the current user.
# For more information, read the documentation at http://www.docker.com/.

TAG=${1:-1}

sudo docker build -t jianjin/base:$TAG -f Dockerfile.base .
# Tag it as latest so that the next step picks it up (not sure if there's a better way)
sudo docker tag jianjin/base:$TAG jianjin/base:latest

sudo docker build -t jianjin/django:$TAG -f Dockerfile.django ..
sudo docker tag jianjin/django:$TAG jianjin/django:latest
