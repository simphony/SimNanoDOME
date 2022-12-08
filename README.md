# SimNanoDOME

SimNanoDOME is a [SimPhoNy](https://github.com/simphony/simphony-osp)
[wrapper](https://simphony.readthedocs.io/en/v3.9.0/overview.html#fetch-data-from-a-database-run-a-simulation-and-immediately-store-the-results)
that is intended to be used for investigating gas-phase nano-particle synthesis
using a Direct-Current (DC) plasma source. The wrapper makes available to the 
user three different models of increasing complexity and computational time:
 - Moment method (Low Accuracy): is the cheapest one in terms of computational
   cost (about 30 minutes) and returns to the user the mean diameter, the mean
   number density and the mean volume fraction of the nano-particle population.
   No PSD (Particle Size Distribution) is returned.
 - PBM (Medium Accuracy): the Population Balance Method returns to the user the 
   Size Distribution of both Particles and Aggregates/Agglomerates by means of
   diameter, number density and volume fraction. Its computational time is in
   the order of a couple of hours.
 - CGMD (High Accuracy): is the most expensive method which can return to the 
   user the same results of PBM method with the addition of the direct 
   simulation of the aggregates/agglomerates formation, thus allowing to 
   compute the Fractal dimension of the nano-particle population. Its 
   computational cost is in the order of a couple of days.

*Contact*: [Giorgio La Civita](mailto:giorgio.lacivita2@unibo.it) from the 
[DIN](https://ingegneriaindustriale.unibo.it/it),
[Alma Mater Studiorum - University of Bologna](https://www.unibo.it).

## Installation

This wrapper requires a version of OpenFOAM that includes not only its third
party packages, but also several add-ons from the
[Industrial Engineering department at UNIBO](https://ingegneriaindustriale.unibo.it).
Such add-ons are not publicly available: contact 
[Giorgio La Civita](mailto:giorgio.lacivita2@unibo.it) if you are interested in
obtaining them. In addition, the [ontodome](https://github.com/nanodome/ontodome)
library is required (commit
[`a727b69`](https://github.com/nanodome/ontodome/commit/a727b6914f8fe2d926d13ae6622c0240d59726c9)
is known to work). Since the installation of such requirements is very complex,
a
[`Dockerfile`](https://github.com/simphony/SimNanoDOME/blob/master/Dockerfile) 
is provided. See the [_"Docker"_ section](#Docker) for more details.

After having installed said requirements, the installation of the wrapper 
itself is rather simple. Start by cloning this repository

```commandline
git clone https://github.com/simphony/SimNanoDOME
```

and then install the Python package (for example, using
[`pip`](https://pip.pypa.io/)).

```commandline
pip install simnanodome
```

[`pip`](https://pip.pypa.io/) will take care of automatically installing and/or
updating [SimPhoNy](https://github.com/simphony/simphony-osp) if needed.

After that, use SimPhoNy's ontology management tool,
[`pico`](https://simphony.readthedocs.io/en/v3.9.0/utils.html#pico), to install
the ontology that the wrapper requires in order to operate, which is included
with the code.

```commandline
pico install simnanodome/ontology.simnanofoam.yml
```

### Docker

The installation of OpenFOAM, its third-party add-ons, the UNIBO DIN add-ons, 
and ontodome is rather complex, therefore, a 
[`Dockerfile`(https://github.com/simphony/SimNanoDOME/blob/master/Dockerfile)
is provided that has a twofold purpose:
- Be used to easily set up the environment and wrapper in a container.
- Serve as detailed installation guide if a containerized set-up is not
  desired.

The UNIBO DIN add-ons for OpenFOAM must be provided in order to build the 
Docker image, as a file named `OpenFOAM_src.zip` located in the same folder as
the Dockerfile.

## Usage
This wrapper can work in three ways:
  - Stand-alone NanoDOME session: the user can assess the nano-particle 
    formation without linking to a CFD software. This could be used for a 
    first-step evaluation of the considered process' feasibility. An example of
    how to use this mode can be found at simnanodome/examples/nanoDOME.py. The 
    user specifies all the inputs required by nanodome such as gas composition, 
    precursor specie and so on. The user can copy the nanoDOME.py script in 
    this folder and run it as it is.
  - Stand-alone CFD session: the user can use the simcfd package as stand-alone
    in order to assess the feasibility of the plasma process under study and 
    then post-process the results with an external software (e.g. Paraview).
    An example of how to use this mode can be found at examples/CFD.py. The
    user can copy the CFD.py script in this folder and run it as it is.
  - CFD-linked session: the user specifies the properties according to the
    current GUI requirements. This is the standard mode.
    An example of how to use this mode can be found at
    simnanodome/examples/nanoFoam.py. The user can copy the nanoDOME.py script
    in this folder and run it as it is.
  - Stand-alone Elenbaas session: the user can access a very reliable model for
    computing the thermodynamic properties of an LTE plasma discharge. Example 
    of usage can be found at simnanodome/examples/nanoFoam.py.
  - Coupled CFD-NanoDOME session: a simple CFD model is coupled using a reactor
    network approach to NanoDOME. Example of usage can be found at 
    simnanodome/examples/nanoFoam.py. The user can copy the nanoDOME.py script
    in this folder and run it as it is.
