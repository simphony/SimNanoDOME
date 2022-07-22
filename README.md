# SimNanoDOME.

*Contact*: [Giorgio La Civita](mailto:giorgio.lacivita2@unibo.it) from the 
DIN, Alma Mater Studiorum - University of Bologna.

**Index**
- [SimNanoDOME.](#simnanodome)
  - [Compatibility](#compatibility)
  - [How to install](#installation)
  - [Introduction](#introduction)
  - [How to use](#howtouse)

## Compatibility

The following table describes the version compatibility between the [OSP core](https://gitlab.cc-asp.fraunhofer.de/simphony/osp-core) package and documentation presented in this project.

| __Wrapper development__ | __OSP core__ |
|:-----------------------:|:------------:|
|          1.0.0          |     3.5.1    |

The releases of OSP core are available [here](https://gitlab.cc-asp.fraunhofer.de/simphony/osp-core/-/releases).

## How to install
Simply follow these step:
  - Run from simnanodome's containing directory
  '''
	pip install simnanodome
  '''
    to install the wrapper and all its requirements.
  - Run
  '''
	pico install ontology.simnanofoam.yml
  '''
    to install the wrapper's ontology.

## Introduction
SimNanoDOME's wrapper is intended to be used for investigating gas-phase nano-particle synthesis using a Direct-Current (DC) plasma source. The wrapper makes available to the user three differente models of increasing complexity and computational time:
 - Moment method (Low Accuracy): is the cheapest one in terms of computational cost (about 30 minutes) and return to the user the mean diameter, the mean number density and the mean volume fraction of the nano-particle population. No PSD (Particle Size Distribution) is returned.
 - PBM (Medium Accuracy): the Population Balance Method returns to the user the Size Distribution of both Particles and Aggregates/Agglomerates by means of diameter, number density and volume fraction. Its computational time is in the order of a couple of hours.
 - CGMD (High Accuracy): is the most expensive method which can return to the user the same results of PBM method with the addition of the direct simulation of the aggregates/agglomerates formation, thus allowing to compute the Fractal dimension of the nano-particle population. Its computational cost is in the order of a couple of days.

## How to use
This wrapper can work in three ways:
  - Stand-alone NanoDOME session: the user can assess the nano-particle formation without linking to a CFD software. This could be used for a first-step evaluation of the considered process' feasibility. An example of how to use this mode can be found at simnanodome/examples/nanoDOME.py. The user specifies all the inputs required by nanodome such as gas composition, precursor specie and so on. The user can copy the nanoDOME.py script in this folder and run it as it is.
  - Stand-alone CFD session: the user can use the simcfd package as stand-alone in order to assess the feasibility of the plasma process under study and then post-process the results with an external software (e.g. Paraview).
  An example of how to use this mode can be found at examples/CFD.py. The user can copy the CFD.py script in this folder and run it as it is.
  - CFD-linked session: the user specifies the properties according to the current GUI requirements. This is the standard mode.
  An example of how to use this mode can be found at simnanodome/examples/nanoFoam.py. The user can copy the nanoDOME.py script in this folder and run it as it is.
  - Stand-alone Elenbaas session: the user can access a very reliable model for computing the thermodynamic properties of an LTE plasma discharge. Example of usage can be found at simnanodome/examples/nanoFoam.py.
  - Coupled CFD-NanoDOME session: a simple CFD model is coupled using a reactor network approach to NanoDOME. Example of usage can be found at simnanodome/examples/nanoFoam.py. The user can copy the nanoDOME.py script in this folder and run it as it is.
