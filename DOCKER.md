# Introduction

This file describes the infrastructure present in the ```docker```
directory to help facilitate running Jianjin under Docker.

The only real reason I did this was as a Docker learning exercise and
proof of concept, though there's no reason this couldn't be used as an
alternative development workflow to ```virtualenv```, or that it
couldn't be used in production in principle (though this would require
a bit more work).

# Prerequisites

All steps here assume you are running under Linux, that you have
Docker installed and the daemon running, and that you have
entitlements to run the docker client via ```sudo``` as the current
user.

For more information, read the documentation at [the Docker
website](http://www.docker.com/). I would recommend you work through
some of the tutorials there to build your understanding of Docker
before trying any of this.

# Basic architecture

I have tested running Jianjin under Docker in two ways:

* In a single container, reading the code from the host operating
  system, and using a Sqlite database.
* One container for a PostgreSQL database, and another for the Django
  server running Gunicorn. This is designed to be more suitable for
  production (though again, this was done as a proof of concept rather
  than a serious attempt to run the application this way in
  production).

# Creating the images

The first step is to create the necessary Docker images. From the
```docker``` directory in this repository, run ```./create_images.py
buildbase builddjango``` (building the base image takes a while, as it
performs an update from the Fedora base image - once this is done you
can specify ```builddjango``` alone in future runs).

This will give you a ```jianjin/django``` image suitable for running
the Jianjin Django server.

# Running a single dev container

Run ```./devel.py run``` to start [the Django development
server](https://docs.djangoproject.com/en/1.11/ref/django-admin/#runserver-port-or-address-port). If
you don't already have a ```db.sqlite3``` file present, you can run
```./devel.py initmigration``` to run the initial migration process to
bootstrap it.

Note that this is a privileged container with access to the code in
the containing repository on the host. This means that when you change
the code on the host, the changes will be seen by the container
immediately, so you don't have to restart the container in order for
the changes to take effect in most cases.

You can also run ```./devel.py test``` to run the Python tests inside
the container.

# Running with a separate PostgreSQL container

* Run ```./start_prod.py createpostgres initmigration``` to create a
  PostgreSQL container and perform the initial migrations
* Run ```./start_prod.py createdjango``` to create the Django
  container.
* You need to specify ```--allowedhosts=localhost``` to be able to
  connect on the localhost (in production you would specify your
  actual set of allowed hosts - [see
  docs](https://docs.djangoproject.com/en/1.11/ref/settings/#allowed-hosts)).
* This is also a bit impractical in a testing environment without
  ```--debug``` as well, which enables [Django's DEBUG
  setting](https://docs.djangoproject.com/en/1.11/ref/settings/#debug),
  because without it, the [SECURE_SSL_REDIRECT](https://docs.djangoproject.com/en/1.11/ref/settings/#std:setting-SECURE_SSL_REDIRECT)
  will kick in and try to redirect you to the HTTPS URLs, which won't
  work. However, in production you would of course not do this: you
  would instead have a proper HTTPS setup.

Note that when you run this way, the ```/code``` directory in the
container is not linked to the hosting OS, so any changes you make in
the hosting OS will have no effect on the Django container until you
recreate the image again using ```./create_images.py builddjango```.

In particular, this means you need to ensure that any Django
migrations required to set up the database exist in the Django image
(similar to the requirement that they be checked into Git for the
benefit of Heroku).

Note also that if you delete the PostgreSQL container, any data you
had stored in it will disappear.