# MegaQC Installation: Docker

## Warning - data persistence
Whilst running a production instance of MegaQC using docker
is very easy, note that the database is stored _within_ the
docker container by default. This means that if the container
is lost, all data is lost with it.

More instructions about how to set up docker in such a way that
this doesn't happen hopefully coming soon.

## Pulling the docker image from dockerhub
To run MegaQC with docker, simply use the following command:

```bash
docker run -p 80:80 ewels/megaqc
```

This will pull the latest image from
[dockerhub](https://hub.docker.com/r/ewels/megaqc/) and run MegaQC
on port 80.

Note that you will need to publish the port in order to access it
from the host, or other machines. For more information, read https://docs.docker.com/engine/reference/run/

Note that the default latest tag will typically be a development
version and may not be very stable. You can specify a tagged version
to run a release instead:

```bash
docker run -p 80:80 ewels/megaqc:v0.1
```

Also note that docker will use a local version of the image if it
exists. To pull the latest version of MegaQC use the following command:

```bash
docker pull ewels/megaqc
```

## Building your own docker image
If you prefer, you can build your own docker image if you have pulled
the MegaQC code from GitHub. Simply cd to the MegaQC root directory and run

```bash
docker build . -t ewels/megaqc
```

You can then run MegaQC as described above:

```bash
docker run -p 80:80 ewels/megaqc
```
