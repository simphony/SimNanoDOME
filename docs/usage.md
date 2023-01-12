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
on the figures from the [operation modes section](#operation-modes). It is
suggested that you do it in SimPhoNy's default session, and then transfer them
to the adequate sessions depending on the operation mode. A code example of how
to initialize the CUDS objects is provided in 
[examples/nanoFoam.py](https://github.com/simphony/SimNanoDOME/blob/master/examples/nanoFoam.py#L22).

Once the inputs of the simulation have been instantiated as CUDS objects, they
must be transferred to one of the SimPhoNy sessions included in the package, 
and then such session may be coupled or linked with others. As it can be seen 
on the aforementioned figures, there are two CUDS objects that are expected to 
be directly connected to the Wrapper CUDS: the `AccuracyLevel` and the 
`nanoReactor`. Such objects will be the ones exchanged between the different 
sessions to achieve the desired coupling and/or linking. Read the 
[operation modes section](#operation-modes) to get an overview on what an 
operation mode does.

## Operation modes

### Stand-alone NanoDOME

The user can assess the nano-particle formation without linking to a CFD 
software. This could be used for a first-step evaluation of the considered 
process' feasibility. The user specifies all the inputs required by nanoDOME 
such as gas composition, precursor species and so on.

<figure style="display: table; text-align:center; margin-left: auto; margin-right:auto">

![SimNanoDOME input for Stand-alone NanoDome](./static/nanodome.drawio.svg)

<figcaption style="display: table-caption; caption-side: bottom; text-align:center">

_Diagram showing the pattern of CUDS objects that SimNanoDOME expects to find 
in the session's knowledge graph and the CUDS objects that are produced 
as simulation outputs for the nanodome mode._

</figcaption>
    
</figure>

This operation mode uses the `NanoDOME` session to compute the nanoparticle 
size distribution. A code example of how to use this mode is available in 
[examples/nanoFoam.py](https://github.com/simphony/SimNanoDOME/blob/master/examples/nanoFoam.py#L228).

### Stand-alone CFD

The user can assess the plasma reactor thermodynamic conditions. This could be used for a first-step evaluation of the considered 
process' feasibility. The user specifies all the inputs required by Elenbaas and the CFD software 
such as gas composition, plasma source operative conditions and so on.

This operation mode links an `ElenbaasSession` to a `CFDSession`. The
`ElenbaasSession` first computes the plasma source properties, that are then passed 
the `CFDSession` to compute the different streamlines.

<figure style="display: table; text-align:center; margin-left: auto; margin-right:auto">

![SimNanoDOME input](./static/cfd.drawio.svg)

<figcaption style="display: table-caption; caption-side: bottom; text-align:center">

_Diagram showing the pattern of CUDS objects that SimNanoDOME expects to find 
in the session's knowledge graph for the cfd mode. Inputs are in green and outputs in blue._

</figcaption>
    
</figure>

A code example of how to use this mode is available in 
[examples/nanoFoam.py](https://github.com/simphony/SimNanoDOME/blob/master/examples/nanoFoam.py#L138).

### CFD-linked

The user can evaluate the nano-particle gas phase synthesis by linking a CFD software and NanoDOME. In this way the thermodynamic properties of the reactor are taken into account.
This is the standard mode.

This operation mode links an `ElenbaasSession` to a `CFDSession` which is then linked to a `NanoDOMESession`. The
`ElenbaasSession` first computes the plasma properties, that are then passed 
the `CFDSession` to compute the streamlines and used as input for several `NanoDOMESession` to evaluate the nanoparticle size 
distribution.

<figure style="display: table; text-align:center; margin-left: auto; margin-right:auto">

![SimNanoDOME input](./static/linked.drawio.svg)

<figcaption style="display: table-caption; caption-side: bottom; text-align:center">

_Diagram showing the pattern of CUDS objects that SimNanoDOME expects to find 
in the session's knowledge graph for cfd-linked mode. Inputs are in green and outputs in blue._

</figcaption>
    
</figure>

A code example of how to use this mode is available in 
[examples/nanoFoam.py](https://github.com/simphony/SimNanoDOME/blob/master/examples/nanoFoam.py#L269).

### Stand-alone Elenbaas

The user can access a very reliable model for computing the thermodynamic 
properties of an LTE plasma discharge. This operation mode uses the 
`ElenbaasSession` to compute the plasma source properties.

<figure style="display: table; text-align:center; margin-left: auto; margin-right:auto">

![SimNanoDOME input](./static/elenbaas.drawio.svg)

<figcaption style="display: table-caption; caption-side: bottom; text-align:center">

_Diagram showing the pattern of CUDS objects that SimNanoDOME expects to find 
in the session's knowledge graph for elenbaas mode. Inputs are in green and outputs in blue._

</figcaption>
    
</figure>

A code example of how to use this mode is available in 
[examples/nanoFoam.py](https://github.com/simphony/SimNanoDOME/blob/master/examples/nanoFoam.py#L188).

### Coupled CFD-NanoDOME

A simple CFD model is coupled using a reactor network approach to NanoDOME. 
This operation mode couples a `CoupledReactorSession` with several `NanoDOMESession`.
At each time step, the results from the previous step are passed to the
`CoupledReactorSession` and then its results to the `NanoDOMESession`. This 
operation is repeated for each time step until the pre-established simulation
time has been covered. At the end, the nanoparticle size distribution can be 
extracted.

<figure style="display: table; text-align:center; margin-left: auto; margin-right:auto">

![SimNanoDOME input](./static/coupled.drawio.svg)

<figcaption style="display: table-caption; caption-side: bottom; text-align:center">

_Diagram showing the pattern of CUDS objects that SimNanoDOME expects to find 
in the session's knowledge graph for the coupled mode. Inputs are in green and outputs in blue._

</figcaption>
    
</figure>

A code example of how to use this mode is available in 
[examples/nanoFoam.py](https://github.com/simphony/SimNanoDOME/blob/master/examples/nanoFoam.py#L430).

### Examples

The user can develop its own workflow from scratch or using the example available in 
[examples/nanoFoam.py](https://github.com/simphony/SimNanoDOME/blob/master/examples/nanoFoam.py#1).
The user can also directly use the example script as it is by selecting the desidered mode and changing the CUDS values.
This is recommended for CFD-linked mode in particular since the linking process is not handled by the wrappers. For this reason a linking algorithm has been provided in the example file.