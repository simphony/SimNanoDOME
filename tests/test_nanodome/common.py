"""Common functions useful for most tests."""

from typing import Dict, List, Union

from osp.core.cuds import Cuds
from osp.core.namespaces import nanofoam as onto
from osp.core.session import CoreSession


def generate_cuds() -> Cuds:
    """Generates the necessary CUDS to represent a simulation.

    Such CUDS are added to a wrapper object for later retrieval. A new
    `CoreSession` is used to store the CUDS.

    Returns:
        The wrapper CUDS packing all the CUDS object representing the
        simulation.
    """
    session = CoreSession()
    with session:
        wrapper = onto.NanoFOAMWrapper(session=session)

        # Create precursor's species
        prec = onto.SolidPrecursor()
        prec_feedrate = onto.FeedRate(value = 125/1000/3600, unit = 'kg/s', name = 'Feed Rate')
        prec_type = onto.Type(name = 'Si')
        prec.add(prec_feedrate, prec_type, rel = onto.hasProperty)

        # Create plasma's source operative conditions
        source = onto.PlasmaSource()
        ipower = onto.InputPower(value = 30e3, unit = 'W', name = 'Input Power')
        flow_rate = onto.FlowRate(value = 40., unit = 'slpm', name = 'Flow Rate')
        source.add(ipower, flow_rate, rel = onto.hasProperty)
        source.add(prec, rel = onto.hasPart)

        # Create plasma's composition
        comp = onto.GasComposition()
        arf = onto.MolarFraction(value = 1., name = 'Ar', unit = '~')
        h2f = onto.MolarFraction(value = 0., name = 'H2', unit = '~')
        n2f = onto.MolarFraction(value = 0., name = 'N2', unit = '~')
        o2f = onto.MolarFraction(value = 0., name = 'O2', unit = '~')
        comp.add(arf, h2f, n2f, o2f, rel = onto.hasPart)

        # Set reactor's dimensions
        reactor_geom = onto.CylindricalReactorDimensions()
        diameter = onto.Diameter(value=0.250, unit='m', name = 'Diameter')
        length = onto.Length(value=0.875, unit='m', name = 'Length')
        inlet_diameter = onto.InletDiameter(value=13e-3, unit='m', name = 'Inlet Diameter')
        reactor_geom.add(diameter, length, inlet_diameter, rel = onto.hasPart)

        # Set thermodynamic conditions
        tcond = onto.ThermoCond()
        pressure = onto.Pressure(value=101325, unit='m^2/s^2', name = 'Pressure')
        temp_grad = onto.TemperatureGradient(value = -1e+7, unit = 'K/s', name = 'Temporal Temperature Gradient')
        temp = onto.Temperature(value = 2000, unit = 'K', name = 'Temperature')
        tcond.add(pressure, temp, temp_grad, rel = onto.hasPart)

        # Process' CUDS
        reactor = onto.nanoReactor()

        # Results' CUDS
        particles = onto.NanoParticleSizeDistribution(name = 'Particles')
        primaries = onto.NanoParticleSizeDistribution(name = 'Primaries')
        reactor.add(particles, primaries, rel = onto.hasPart)

        reactor.add(reactor_geom, tcond, comp, rel = onto.hasPart)
        source.add(reactor, rel = onto.hasProperty)

        wrapper.add(source)

        return wrapper


def get_key_simulation_cuds(wrapper: Cuds) -> \
        Dict[str, Union[Cuds,
                        List[Cuds]]]:
    """Returns important CUDS managing the simulation.

    Given a wrapper object, this function extracts the CUDS important for the
    simulation runtime from a wrapper object.

    Args:
        wrapper: Wrapper object containing the CUDS necessary for the
          simulation.
    """
    key_cuds = dict()
    key_cuds['source'] = wrapper.get(oclass=onto.PlasmaSource)[0]
    key_cuds['reactor'] = key_cuds['source'].get(oclass=onto.nanoReactor)[0]

    return key_cuds
