"""Integration test examples."""

import unittest, os

from osp.core.cuds import Cuds
from osp.core.namespaces import nanofoam as onto

from .common import generate_cuds, get_key_simulation_cuds
from osp.wrappers.simelenbaas.elenbaassession import ElenbaasSession
from osp.wrappers.simelenbaas.elenbaasengine import elen_run


class TestIntegration(unittest.TestCase):
    """Integration tests."""

    template_wrapper: Cuds

    def setUp(self) -> None:
        """Generates the necessary CUDS to represent a simulation.

        The results are stored in `self.template_wrapper`.
        """
        self.template_wrapper = generate_cuds()

    def test_reactor_engine_with_reactor_session(self):
        """Tests the interaction between the session and the engine.

        Tests the interaction between `ElenbaasSession` and
        `elenbaasengine`.
        """
        key_cuds = get_key_simulation_cuds(self.template_wrapper)
        source = key_cuds['source']
        accuracy_level = key_cuds['accuracy_level']

        with ElenbaasSession(delete_simulation_files=True) as session:
            wrapper = onto.NanoFOAMWrapper(session=session)
            wrapper.add(source, accuracy_level)

            self.assertFalse(session._initialized)

            session.run()

            self.assertTrue(session._initialized)

            # Check if plasma property files have been generated
            results_file_list = ['VR', 'TR', 'epsR', 'kR', 'radiation.rad', 'rho', 'Cp',
                                'enthalpy', 'mu', 'kappa', 'sigmaE', 'entropy', 'densRef']

            self.assertListEqual(sorted(os.listdir(session._case_dir)), sorted(results_file_list), msg="Expected files number does not match the actual number")

            # Check if results have been transferd to wrapper as CUDS
            results_CUDS_list = ['Velocity radial profile',
                                 'Temperature radial profile',
                                 'Rate of dissipation of turbulent kinetic energy radial profile',
                                 'Turbulent kinetic energy radial profile',
                                 'Plasma radiative heat transfer',
                                 'Density',
                                 'Specific heat capacity (Cp)',
                                 'Specific enthalpy',
                                 'Dynamic viscosity',
                                 'Thermal conductivity',
                                 'Electrical conductivty',
                                 'Specific entropy',
                                 'Reference density']

            CUDS_res = wrapper.get(oclass=onto.PlasmaSource)[0].get(oclass=onto.Plasma)[0].get()
            CUDS_names = list()
            for res in CUDS_res:
                CUDS_names.append(res.name)

            self.assertListEqual(sorted(results_CUDS_list), sorted(CUDS_names), msg="Expected CUDS number does not match the actual number")


if __name__ == '__main__':
    unittest.main()
