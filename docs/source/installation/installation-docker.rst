MegaQC Installation: Docker
===========================

Pulling the docker image from dockerhub
---------------------------------------

To run MegaQC with docker, simply use the following command:

.. code:: bash

   docker run -p 80:80 ewels/megaqc

This will pull the latest image from `dockerhub`_ and run MegaQC on port
80.

Note that you will need to publish the port in order to access it from
the host, or other machines. For more information, read
https://docs.docker.com/engine/reference/run/

Note that the default latest tag will typically be a development version
and may not be very stable. You can specify a tagged version to run a
release instead:

.. code:: bash

   docker run -p 80:80 ewels/megaqc:v0.1

Also note that docker will use a local version of the image if it
exists. To pull the latest version of MegaQC use the following command:

.. code:: bash

   docker pull ewels/megaqc

Building your own docker image
------------------------------

If you prefer, you can build your own docker image if you have pulled
the MegaQC code from GitHub. Simply cd to the MegaQC root directory and
run

.. code:: bash

   docker build . -t ewels/megaqc

You can then run MegaQC as described above:

.. code:: bash

   docker run -p 80:80 ewels/megaqc

Using persistent data
---------------------

The Dockerfile has been configured to automatically create persisent
volumes for the data and log directories. This volume will be created
without additional input by the user, but if you want to re-use those
volumes with a new container you must specify them when running the
docker image.

The easiest way to ensure the database persists between container states
is to always specify the same volume for ``/usr/local/lib/postgresql``.
If a volume is found with that name it is used, otherwise it creates a
new volume.

To create or re-use a docker volume named ``pg_data``:

.. code:: bash

   docker run -p 80:80 -v pg_data:/usr/local/lib/postgresql ewels/megaqc

The same can be done for a log directory volume called ``pg_logs``

.. code:: bash

   docker run -p 80:80 -v pg_data:/usr/local/lib/postgresql -v pg_logs:/var/log/postgresql ewels/megaqc

If you did not specify a volume name, docker will have given it a long
hex string as a unique name. If you do not use volumes frequently, you
can check the output from ``docker volume ls`` and
``docker volume inspect $VOLUME_NAME``. However, the easiest way is to
inspect the docker container.

.. code:: bash

   # ugly default docker output
   docker inspect --format '{{json .Mounts}}' example_container

   # use jq for pretty formatting
   docker inspect --format '{{json .Mounts}}' example_container | jq

   # or use python for pretty formatting
   docker inspect --format '{{json .Mounts}}' example_container | python -m json.tool

Example output for the above, nicely formatted:

\```json [ { “Type”: “volume”, “Name”:
“7c8c9dfbcc66874b472676659dde6a5c8e15dea756a620435c83f5980c21d804”,
“Source”:
"/var/lib/docker/volumes/7c8c9dfbcc66874b472676659dde6a5c8e15dea756a620435c83f5980c21d804/_data“,”Destination“:”/usr/local/lib/postgresql“,”Driver“:”loca

.. _dockerhub: https://hub.docker.com/r/ewels/megaqc/