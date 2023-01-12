# Installation

```{include} ../README.md
   :start-after: <!---installation-start-dbeeaa52-->
   :end-before: <!---installation-end-dbeeaa52-->
```

Since such a set-up is fairly complex,
a [`Dockerfile`](https://github.com/simphony/SimNanoDOME/blob/master/Dockerfile)
is provided and is the recommended way of use. It can be used not only to build a docker image where the wrapper
can be run but also as a guideline for setting up the environment on your own 
system. Visit the [_"Docker"_ section](#docker) for more details.

```{include} ../README.md
   :start-after: <!---installation-start-b9ea19d3-->
   :end-before: <!---installation-end-b9ea19d3-->
```

## Docker

As the installation of OpenFOAM, its third-party add-ons, the UNIBO DIN add-ons, 
and ontodome is rather complex, a 
[`Dockerfile`](https://github.com/simphony/SimNanoDOME/blob/master/Dockerfile)
is provided that has a twofold purpose:
- Be used to easily set up the environment and wrapper in a container (a couple of hours is required for the image to build).
- Serve as detailed installation guide if a containerized set-up is not
  desired.

To build the docker image, clone the SimNanoDOME repository

```shell
git clone https://github.com/simphony/SimNanoDOME
```

and run the following commands.

```shell
cd simnanodome
docker build . -t simnanodome
```

After that, you can spin up a container using the image and access a Python 
shell within it running the command below.

```shell
docker run --rm -it simnanodome python
```

or access a bash shell using:

```shell
docker run --rm -it simnanodome bash
```