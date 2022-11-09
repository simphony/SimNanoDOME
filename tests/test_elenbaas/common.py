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

        # Set the accuracy level
        accuracy_level = onto.MediumAccuracyLevel()

        # Create precursor's species
        precursor = onto.SolidPrecursor()
        precursor_feed_rate = onto.FeedRate(value=1e-3, unit='kg/s',
                                            name='Feed Rate')
        precursor_type = onto.Type(name='Si')
        precursor.add(precursor_feed_rate,
                      precursor_type,
                      rel=onto.hasProperty)

        # Create plasma's source operative conditions
        source = onto.PlasmaSource()
        input_power = onto.InputPower(value=15000., unit='W',
                                      name='Input Power')
        flow_rate = onto.FlowRate(value=60.,
                                  unit='slpm',
                                  name='Flow Rate')
        source.add(input_power, flow_rate, rel=onto.hasProperty)
        source.add(precursor, rel=onto.hasPart)

        # Create plasma's composition
        comp = onto.GasComposition()
        arf = onto.MolarFraction(value=1., name='Ar', unit='~')
        h2f = onto.MolarFraction(value=0., name='H2', unit='~')
        n2f = onto.MolarFraction(value=0., name='N2', unit='~')
        o2f = onto.MolarFraction(value=0., name='O2', unit='~')
        comp.add(arf, h2f, n2f, o2f, rel=onto.hasPart)

        # Set reactor's dimensions
        reactor_geom = onto.CylindricalReactorDimensions()
        diameter = onto.Diameter(value=0.3, unit='m', name='Diameter')
        length = onto.Length(value=1.5, unit='m', name='Length')
        inlet_diameter = onto.InletDiameter(value=13e-3,
                                            unit='m',
                                            name='Inlet Diameter')
        reactor_geom.add(diameter,
                         length,
                         inlet_diameter,
                         rel=onto.hasPart)

        # Process' CUDS
        reactor = onto.nanoReactor()
        reactor.add(reactor_geom, rel=onto.hasPart)
        reactor.add(comp, rel = onto.hasPart)
        source.add(reactor, rel = onto.hasProperty)

        wrapper.add(source, accuracy_level)

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
    key_cuds['accuracy_level'] = (
        wrapper.get(oclass=onto.MediumAccuracyLevel)
        or wrapper.get(oclass=onto.LowAccuracyLevel)
        or wrapper.get(oclass=onto.HighAccuracyLevel)
    )[0]
    key_cuds['results'] = key_cuds['source'].get(oclass=onto.PlasmaProperty)

    return key_cuds
