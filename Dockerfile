FROM python:3.10 AS runner

LABEL maintainer="giorgio.lacivita2@unibo.it"
LABEL dockerfile.version="1.1"

ENV user=simdomeuser HOME=/home/simdomeuser

# Install requirements
RUN apt-get update && apt-get install -y apt-utils
RUN apt-get install -y git bash qt5-qmake libboost-dev \
    build-essential flex cmake zlib1g-dev libopenmpi-dev openmpi-bin gnuplot \
    libreadline-dev libncurses-dev libgmp-dev libmpfr-dev libmpc-dev unzip \
    rsync autoconf autotools-dev gawk libfl-dev mpi-default-bin \
    mpi-default-dev libfftw3-dev libscotch-dev libptscotch-dev \
    libboost-system-dev libboost-thread-dev libcgal-dev

WORKDIR $HOME/build

# Get OpenFOAM v1906, its third party packages and UNIBO-DIN addons
ADD https://develop.openfoam.com/Development/openfoam/-/archive/OpenFOAM-v1906/openfoam-OpenFOAM-v1906.tar.gz $HOME/build/openfoam-OpenFOAM-v1906.tar.gz
ADD https://sourceforge.net/projects/openfoam/files/v1906/ThirdParty-v1906.tgz/download $HOME/build/ThirdParty-v1906.tgz

RUN tar -xf $HOME/build/openfoam-OpenFOAM-v1906.tar.gz && \
    mv openfoam-OpenFOAM-v1906/ OpenFOAM-v1906/
RUN tar -xf ThirdParty-v1906.tgz

RUN git clone https://github.com/giorgiolacivita/LTEPlasmaFoam.git OpenFOAM-v1906-add-ons

WORKDIR $HOME/build/OpenFOAM-v1906-add-ons
RUN rm -rf LICENSE README.md user-v1906
WORKDIR $HOME/build
RUN cp -rf OpenFOAM-v1906-add-ons/OpenFOAM-v1906/* OpenFOAM-v1906/ && rm -rf OpenFOAM-v1906-add-ons

RUN rm -f openfoam-OpenFOAM-v1906.tar.gz ThirdParty-v1906.tgz

# Compile OpenFOAM with the third party packages and the UNIBO-DIN addons
WORKDIR $HOME/build/OpenFOAM-v1906
RUN bash -c 'chmod +rwx /home/simdomeuser/build/OpenFOAM-v1906/etc/bashrc'
RUN bash -c 'source /home/simdomeuser/build/OpenFOAM-v1906/etc/bashrc && wclean all'
RUN sed -i '/pybind11/d' applications/solvers/incompressible/reactNetFoam/Make/options && \
    sed -i 's/\$(c++WARN) //g' wmake/rules/linux64Gcc/c++ && \
    sed -i -e '/isAdministrator/,+9d' src/OpenFOAM/db/dynamicLibrary/dynamicCode/dynamicCode.C
RUN bash -c 'source /home/simdomeuser/build/OpenFOAM-v1906/etc/bashrc && ./Allwmake -j -q -s'
RUN bash -c 'echo "source /home/simdomeuser/build/OpenFOAM-v1906/etc/bashrc" >> /etc/bash.bashrc '

# Get ontodome and simnanodome
WORKDIR $HOME/build
RUN git clone https://github.com/nanodome/ontodome.git
RUN mkdir simnanodome
RUN git clone https://github.com/simphony/SimNanoDOME.git
RUN mv SimNanoDOME/* simnanodome/ && rm -rf SimNanoDOME

# Compile ontodome and link it to simnanodome
WORKDIR $HOME/build/ontodome
RUN git checkout a727b6914f8fe2d926d13ae6622c0240d59726c9
RUN mkdir -p $HOME/build/simnanodome/osp/wrappers/simnanodome/nanolib/
RUN sed -i 's|/usr/include/python3.9|/usr/local/include/python3.10|g' ontodome.pro && \
    qmake -qt=5 ontodome.pro && \
    make && \
    ln -sf $HOME/build/ontodome/libontodome.so.1 $HOME/build/simnanodome/osp/wrappers/simnanodome/nanolib/libontodome.so

# Install SimNanoDOME
ENV PIP_ROOT_USER_ACTION=ignore \
    OMPI_ALLOW_RUN_AS_ROOT=1 \
    OMPI_ALLOW_RUN_AS_ROOT_CONFIRM=1

RUN pip install osp-core

WORKDIR $HOME/build/simnanodome

RUN python -m osp.core.pico install ontology.simnanofoam.yml && \
    pip install .
