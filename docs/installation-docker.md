# MegaQC Installation: Docker

## Building your own docker image

Run `docker build . -t megaqc` while being located in the folder that contains the DockerFile


## Running the docker image

Run `docker run -p 80:80 megaqc`

The docker container runs an apache proxy on port 80, you need to publish the port in order to access it from the host, or other machines. 
For more information, read https://docs.docker.com/engine/reference/run/
