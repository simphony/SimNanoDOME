"""Test typical usage of the software (end-to-end test)."""

import logging
import unittest

from osp.core.namespaces import nanofoam as onto
from osp.core.cuds import Cuds

from common import generate_cuds, get_key_simulation_cuds
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

    def test_coupled(self):
        """Coupling of the CoupledReactorSession and a NanoDOMESession."""
        # Configuration.
        run_time = 1e-7
        save_time = 0.
        save_step = 0.5e-8


        # Recover CUDS.
        key_cuds = get_key_simulation_cuds(self.template_wrapper)
        reactor = key_cuds['reactor']
        source = key_cuds['source']
        accuracy_level = key_cuds['accuracy_level']
        time = key_cuds['time']
        dt = key_cuds['dt']
        cells = key_cuds['cells']
        precursor_type = key_cuds['precursor_type']

        with CoupledReactorSession(delete_simulation_files=True) as coupled, \
                NanoDOMESession(delete_simulation_files=True) as nano:
            coupled_wrapper = onto.NanoFOAMWrapper(session=coupled)
            coupled_wrapper.add(source, accuracy_level)

            nano_wrapper = onto.NanoFOAMWrapper(session=nano)
            nano_wrapper.add(source, accuracy_level)

            while time.value < run_time:

                logger.info(f"Time: {time.value}")

                coupled_wrapper.update(source)

                coupled.run()

                source.update(coupled_wrapper.get(source.uid).get(reactor.uid))

                save_time += dt.value

                if save_time > save_step:
                    logger.info("Post coupled")
                    for cl in cells:
                        t_fractions = cl.get(
                            oclass=onto.GasComposition)[0].get(
                            oclass=onto.MolarFraction)
                        for mol in t_fractions:
                            if mol.name is precursor_type.name:
                                logger.info(mol.value)

                nano_wrapper.update(source)

                nano.run()

                source.update(nano_wrapper.get(source.uid).get(reactor.uid))

                if save_time > save_step:
                    logger.info("Post nano")
                    for cl in cells:
                        t_fractions = cl.get(
                            oclass=onto.GasComposition)[0].get(
                            oclass=onto.MolarFraction)
                        for mol in t_fractions:
                            if mol.name is precursor_type.name:
                                logger.info(mol.value)

                    save_time = 0.

                time.value += dt.value

            logger.info(f"Time (end): {time.value}")

        self.assertGreaterEqual(time.value, run_time)


if __name__ == '__main__':
    unittest.main()
