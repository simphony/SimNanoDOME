FROM python:3.10 AS runner

LABEL maintainer="giorgio.lacivita2@unibo.it"
LABEL dockerfile.version="1.0"

ENV user=simdomeuser HOME=/home/simdomeuser

# Install requirements
RUN apt-get update && apt-get install -y git bash qt5-qmake libboost-dev build-essential flex cmake zlib1g-dev  \
    libopenmpi-dev openmpi-bin gnuplot libreadline-dev libncurses-dev libgmp-dev libmpfr-dev libmpc-dev unzip rsync \
    autoconf autotools-dev gawk libfl-dev mpi-default-bin mpi-default-dev libfftw3-dev libscotch-dev libptscotch-dev \
    libboost-system-dev libboost-thread-dev libcgal-dev

WORKDIR $HOME/build

# Get OpenFOAM v1906 and its ThirdParties
ADD https://develop.openfoam.com/Development/openfoam/-/archive/OpenFOAM-v1906/openfoam-OpenFOAM-v1906.tar.gz $HOME/build/OpenFOAM-v1906.tar.gz
ADD https://sourceforge.net/projects/openfoam/files/v1906/ThirdParty-v1906.tgz/download $HOME/build/ThirdParty-v1906.tgz

# Uncompress OpenFOAM and ThirdParty files
RUN tar -xf $HOME/build/OpenFOAM-v1906.tar.gz && \
    mv openfoam-OpenFOAM-v1906 OpenFOAM-v1906
RUN tar -xf ThirdParty-v1906.tgz

# Remove source files
RUN rm -f OpenFOAM-v1906.tar.gz ThirdParty.tgz

# Get the UNIBO-DIN addons to OpenFOAM
COPY OpenFOAM_src.zip .

#Compile OpenFOAM with the addons
RUN unzip -q OpenFOAM_src.zip && \
    cp -r OpenFOAM_src/OpenFOAM/OpenFOAM-v1906/* OpenFOAM-v1906/ && \
    rm -r OpenFOAM_src.zip OpenFOAM_src/

WORKDIR $HOME/build/OpenFOAM-v1906
RUN bash -c 'source /home/simdomeuser/build/OpenFOAM-v1906/etc/bashrc && wclean all'
RUN sed -i '/pybind11/d' applications/solvers/incompressible/reactNetFoam/Make/options && \
    sed -i 's/\$(c++WARN) //g' wmake/rules/linux64Gcc/c++ && \
    sed -i -e '/isAdministrator/,+9d' src/OpenFOAM/db/dynamicLibrary/dynamicCode/dynamicCode.C
RUN bash -c 'source /home/simdomeuser/build/OpenFOAM-v1906/etc/bashrc && ./Allwmake -j -q -s'

# Get ontodome and simnanodome
COPY ontodome $HOME/build/ontodome
COPY simnanodome $HOME/build/simnanodome

# Compile ontodome and link it to simnanodome
WORKDIR $HOME/build/ontodome
RUN sed -i 's|/usr/include/python3.9|/usr/local/include/python3.10|g' ontodome.pro && \
    qmake -qt=5 ontodome.pro && \
    make && \
    ln -sf $HOME/build/ontodome/libontodome.so.1.0.0 $HOME/build/simnanodome/osp/wrappers/simnanodome/nanolib/

# Install simnanodome
ENV PIP_ROOT_USER_ACTION=ignore \
    OMPI_ALLOW_RUN_AS_ROOT=1 \
    OMPI_ALLOW_RUN_AS_ROOT_CONFIRM=1

RUN pip install osp-core

WORKDIR $HOME/build/simnanodome

RUN python -m osp.core.pico install ontology.simnanofoam.yml && \
    pip install .
