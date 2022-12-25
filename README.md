# SimNanoDOME

<!---introduction-start-35660ec3-->

SimNanoDOME is a [SimPhoNy](https://github.com/simphony/simphony-osp)
[wrapper](https://simphony.readthedocs.io/en/v3.9.0/overview.html#fetch-data-from-a-database-run-a-simulation-and-immediately-store-the-results)
that is intended to be used for investigating gas-phase nano-particle synthesis
using a Direct-Current (DC) plasma source. The wrapper makes available to the 
user three different models of increasing complexity and computational time:
 - Moment method (Low Accuracy): is the cheapest one in terms of computational
   cost and returns to the user the mean diameter, the mean
   number density and the mean volume fraction of the nano-particle population.
   No PSD (Particle Size Distribution) is returned.
 - PBM (Medium Accuracy): the Population Balance Method returns to the user the 
   Size Distribution of both Particles and Aggregates/Agglomerates by means of
   diameter, number density and volume fraction.
 - CGMD (High Accuracy): is the most expensive method which can return to the 
   user the same results of PBM method with the addition of the direct 
   simulation of the aggregates/agglomerates formation, thus allowing to 
   compute the Fractal dimension of the nano-particle population.

*Contact*: [Giorgio La Civita](mailto:giorgio.lacivita2@unibo.it) and [Emanuele Ghedini](mailto:emanuele.ghedini@unibo.it) from the 
[DIN](https://ingegneriaindustriale.unibo.it/it),
[Alma Mater Studiorum - University of Bologna](https://www.unibo.it).

<!---introduction-end-35660ec3-->

## Installation

<!---installation-start-dbeeaa52-->

This wrapper requires OpenFOAM, compiled not only with its third party 
packages, but also with several add-ons from the 
[Industrial Engineering department at UNIBO](https://ingegneriaindustriale.unibo.it).
In addition, commit
[`a727b69`](https://github.com/nanodome/ontodome/commit/a727b6914f8fe2d926d13ae6622c0240d59726c9)
from the [ontodome](https://github.com/nanodome/ontodome) library is required. 
The UNIBO DIN add-ons are publicly available at: (https://github.com/giorgiolacivita/LTEPlasmaFoam) release v1.0.0.

<!---installation-end-dbeeaa52-->

Since such a set-up is fairly complex,
a [`Dockerfile`](https://github.com/simphony/SimNanoDOME/blob/master/Dockerfile)
is provided and is the recommended way of use (a couple of hours is required for the image to build). It can be used not only to build a docker image where the wrapper
can be run but also as a guideline for setting up the environment on your own system. Visit the
[_"Docker"_ section of the documentation](https://simnanodome.readthedocs.io/en/latest/installation.html#docker)
for more details.

<!---installation-start-b9ea19d3-->

After having installed said requirements, the installation of the wrapper 
itself is rather simple. Start by cloning this repository

```shell
git clone https://github.com/simphony/SimNanoDOME
```

and then install the Python package (for example, using
[`pip`](https://pip.pypa.io/)).

```shell
pip install simnanodome
```

[`pip`](https://pip.pypa.io/) will take care of automatically installing and/or
updating [SimPhoNy](https://github.com/simphony/simphony-osp) if needed.

After that, use SimPhoNy's ontology management tool,
[`pico`](https://simphony.readthedocs.io/en/v3.9.0/utils.html#pico), to install
the ontology that the wrapper requires in order to operate, which is included
with the code.

```shell
pico install simnanodome/ontology.simnanofoam.yml
```

<!---installation-end-b9ea19d3-->

## Documentation

Visit [SimNanoDOME's documentation](https://simnanodome.readthedocs.io)
to learn how to use the wrapper. You may also have a look at the
[`examples` folder](https://github.com/simphony/SimNanoDOME/tree/master/examples)
for additional examples.