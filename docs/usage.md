# Usage

SimNanoDOME can operate in five different modes

  - [Stand-alone NanoDOME](#stand-alone-nanodome)
  - [Stand-alone CFD](#stand-alone-cfd)
  - [CFD-linked](#cfd-linked)
  - [Stand-alone Elenbaas](#stand-alone-elenbaas)
  - [Coupled CFD-NanoDOME](#coupled-cfd-nanodome)

and includes four different SimPhoNy sessions that must be combined in 
different ways to realize each operation mode.

```python
from osp.wrappers.simcfd import CFDSession
from osp.wrappers.simcoupledreactor import CoupledReactorSession
from osp.wrappers.simelenbaas import ElenbaasSession
from osp.wrappers.simnanodome import NanoDOMESession
```

Read the [operation modes section](#operation-modes) to get an overview on what
each one does and how the coupling and linking works for each case.

## Simulation inputs

Regardless of the operation mode, the inputs of a SimNanoDOME simulation are 
instantiated as CUDS objects using the ontology entities from the `nanofoam` 
namespace.

```python
from osp.core.namespaces import nanofoam
```

The pattern of CUDS objects that SimNanoDOME expects depends on its operation 
mode, although it is roughly the same for all of them. To launch a simulation,
you will have to instantiate CUDS objects matching any of the patterns depicted
on the figure below. It is suggested that you do it in SimPhoNy's default
session, and then transfer them to the adequate sessions depending on the
operation mode. A code example of how to initialize the CUDS objects is
provided in [examples/nanoFoam.py](https://github.com/simphony/SimNanoDOME/blob/master/examples/nanoFoam.py#L22). 

<figure style="display: table; text-align:center; margin-left: auto; margin-right:auto">

![SimNanoDOME input](./static/graph_pattern.drawio.svg)

<figcaption style="display: table-caption; caption-side: bottom; text-align:center">

_Diagram showing the pattern of CUDS objects that SimNanoDOME expects to find in the session's knowledge graph._

</figcaption>
    
</figure>

Once the inputs of the simulation have been instantiated as CUDS objects, they
must be transferred to one of the SimPhoNy sessions included in the package, 
and then such session may be coupled or linked with others. As it can be seen 
on the diagram, there are two CUDS objects that are expected to be directly 
connected to the Wrapper CUDS: the `AccuracyLevel` and the `nanoReactor`. Such 
objects will be the ones exchanged between the different sessions to achieve 
the desired coupling and/or linking. Read the [next section](#operation-modes) 
to get an overview on what operation mode does and how the coupling and linking
works for each operation mode.

## Operation modes

### Stand-alone NanoDOME

The user can assess the nano-particle formation without linking to a CFD 
software. This could be used for a first-step evaluation of the considered 
process' feasibility. The user specifies all the inputs required by nanodome 
such as gas composition, precursor species and so on.

This operation mode uses the `NanoDOME` session to compute the nanoparticle 
size distribution. A code example of how to use this mode is available in 
[examples/nanoFoam.py](https://github.com/simphony/SimNanoDOME/blob/master/examples/nanoFoam.py#L228).

### Stand-alone CFD

The user can assess the nano-particle formation without linking to a CFD 
software. This could be used for a first-step evaluation of the considered 
process' feasibility. The user specifies all the inputs required by nanodome 
such as gas composition, precursor species and so on.

This operation mode links an `ElenbaasSession` to a `CFDSession`. The
`ElenbaasSession` first computes the plasma properties, that are then passed 
the `CFDSession` to compute the different streamlines.

A code example of how to use this mode is available in 
[examples/nanoFoam.py](https://github.com/simphony/SimNanoDOME/blob/master/examples/nanoFoam.py#L138).

### CFD-linked

The user specifies the properties according to the current GUI requirements. 
This is the standard mode.

This operation mode links an `ElenbaasSession` to a `CFDSession`. The
`ElenbaasSession` first computes the plasma properties, that are then passed 
the `CFDSession` to compute the streamlines and the nanoparticle size 
distribution.

A code example of how to use this mode is available in 
[examples/nanoFoam.py](https://github.com/simphony/SimNanoDOME/blob/master/examples/nanoFoam.py#L269).

### Stand-alone Elenbaas

The user can access a very reliable model for computing the thermodynamic 
properties of an LTE plasma discharge. This operation mode uses the 
`ElenbaasSession` to compute the Plasma properties.

A code example of how to use this mode is available in 
[examples/nanoFoam.py](https://github.com/simphony/SimNanoDOME/blob/master/examples/nanoFoam.py#L188).

### Coupled CFD-NanoDOME

A simple CFD model is coupled using a reactor network approach to NanoDOME. 
This operation mode couples a `CoupledReactorSession` with a `NanoDOMESession`.
At each time step, the results from the previous step are passed to the
`CoupledReactorSession` and then its results to the `NanoDOMESession`. This 
operation is repeated for each time step until the pre-established simulation
time has been covered. At the end, the nanoparticle size distribution can be 
extracted.

A code example of how to use this mode is available in 
[examples/nanoFoam.py](https://github.com/simphony/SimNanoDOME/blob/master/examples/nanoFoam.py#L430).
