"""Integration test examples."""

import unittest

from osp.core.cuds import Cuds
from osp.core.namespaces import nanofoam as onto

from common import generate_cuds, get_key_simulation_cuds
from osp.wrappers.simnanodome.nanosession import NanoDOMESession
from osp.wrappers.simnanodome.nano_engine import nano_engine


class TestIntegration(unittest.TestCase):
    """Nanodome Integration test."""

    template_wrapper: Cuds

    def setUp(self) -> None:
        """Generates the necessary CUDS to represent a simulation.

        The results are stored in `self.template_wrapper`.
        """
        self.template_wrapper = generate_cuds()

    def test_nano_engine_with_nano_session_low(self):
        """Tests the interaction between the session and the engine.

        Tests the interaction between `NanodomeSession` and
        `nano_engine`.
        """
        key_cuds = get_key_simulation_cuds(self.template_wrapper)
        source = key_cuds['source']

        with NanoDOMESession(delete_simulation_files=True) as session:
            wrapper = onto.NanoFOAMWrapper(session=session)
            accuracy_level = onto.LowAccuracyLevel()
            wrapper.add(source, accuracy_level)

            self.assertFalse(session._initialized)

            session.eng.tf = 1e-8
            session.run()

            self.assertTrue(session._initialized)
            self.assertTrue(isinstance(session.eng,
                                       nano_engine))

            val_mean_diam = 6.8020459579367625
            val_numb_dens = 1.1545961749511164e+16
            val_vol_frac = 1.9025996934712173e-07
            mean_diam, numb_dens, vol_frac = session.eng.nano_run(session)
            self.assertLessEqual(abs(val_mean_diam - mean_diam),
                                 1e-6)
            self.assertLessEqual(abs(val_numb_dens - numb_dens),
                                 1e-6)
            self.assertLessEqual(abs(val_vol_frac - vol_frac),
                                 1e-6)

    def test_nano_engine_with_nano_session_medium(self):
        """Tests the interaction between the session and the engine.

        Tests the interaction between `NanodomeSession` and
        `nano_engine`.
        """
        key_cuds = get_key_simulation_cuds(self.template_wrapper)
        source = key_cuds['source']

        with NanoDOMESession(delete_simulation_files=True) as session:
            wrapper = onto.NanoFOAMWrapper(session=session)
            accuracy_level = onto.MediumAccuracyLevel()
            wrapper.add(source, accuracy_level)

            self.assertFalse(session._initialized)

            session.eng.tf = 1e-10
            session.run()

            self.assertTrue(session._initialized)
            self.assertTrue(isinstance(session.eng,
                                       nano_engine))

            particles, primaries = session.eng.nano_run(session)
            self.assertGreater(len(particles), 0)
            self.assertGreater(len(primaries), 0)


if __name__ == '__main__':
    unittest.main()
