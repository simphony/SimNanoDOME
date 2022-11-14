"""Test typical usage of the software (end-to-end test)."""

import logging
import unittest

from osp.core.namespaces import nanofoam as onto
from osp.core.cuds import Cuds

from .common import generate_cuds, get_key_simulation_cuds
from osp.wrappers.simcoupledreactor.coupledreactorsession import \
    CoupledReactorSession
from osp.wrappers.simnanodome.nanosession import NanoDOMESession

logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.INFO)


class TestWrapper(unittest.TestCase):
    """Typical usage of the Coupled Reactor Session."""

    template_wrapper: Cuds

    def setUp(self) -> None:
        """Generates the necessary CUDS to represent a simulation.

        The results are stored in `self.template_wrapper`. This function
        runs before each test method from this test case.
        """
        self.template_wrapper = generate_cuds()

    def test_nanodome_low(self):
        """NanoDOMESession standalone for Low Accuracy."""

        # Recover CUDS.
        key_cuds = get_key_simulation_cuds(self.template_wrapper)
        reactor = key_cuds['reactor']
        source = key_cuds['source']

        with NanoDOMESession(delete_simulation_files=True) as nano:
            nanowrapper = onto.NanoFOAMWrapper(session=nano)

            # Results CUDS
            particles = onto.NanoParticleSizeDistribution(name = 'Particles')
            primaries = onto.NanoParticleSizeDistribution(name = 'Primaries')
            reactor.add(particles, primaries, rel = onto.hasPart)
            accuracy_level = onto.LowAccuracyLevel()
            nanowrapper.add(source, accuracy_level)

            # Run the session
            ##########################################################
            nano.eng.tf = 1e-8
            nano.run()

            # Get the results
            res = nanowrapper.get(source.uid).get(reactor.uid)
            particles = res.get(particles.uid)
            primaries = res.get(primaries.uid)

            self.assertGreater(len(particles.get(oclass=onto.Bin)), 0)

    def test_nanodome_medium(self):
        """NanoDOMESession standalone for Medium Accuracy."""

        # Recover CUDS.
        key_cuds = get_key_simulation_cuds(self.template_wrapper)
        reactor = key_cuds['reactor']
        source = key_cuds['source']

        with NanoDOMESession(delete_simulation_files=True) as nano:
            nanowrapper = onto.NanoFOAMWrapper(session=nano)

            # Results CUDS
            particles = onto.NanoParticleSizeDistribution(name = 'Particles')
            primaries = onto.NanoParticleSizeDistribution(name = 'Primaries')
            reactor.add(particles, primaries, rel = onto.hasPart)
            accuracy_level = onto.MediumAccuracyLevel()
            nanowrapper.add(source, accuracy_level)

            # Run the session
            ##########################################################
            nano.eng.tf = 1e-10
            nano.run()

            # Get the results
            res = nanowrapper.get(source.uid).get(reactor.uid)
            particles = res.get(particles.uid)
            primaries = res.get(primaries.uid)

            self.assertGreater(len(particles.get(oclass=onto.Bin)), 0)
            self.assertGreater(len(primaries.get(oclass=onto.Bin)), 0)

if __name__ == '__main__':
    unittest.main()
