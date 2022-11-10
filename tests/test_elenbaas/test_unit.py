"""Unit test examples, both at the "system" level and the "method" level."""

import unittest, os

import matplotlib.pyplot as plt
import numpy as np
from scipy import io as io

from osp.core.cuds import Cuds
from osp.core.namespaces import nanofoam as onto

from osp.wrappers.simelenbaas.elenbaassession import ElenbaasSession
import osp.wrappers.simelenbaas.elenbaasengine as elen_engine


class TestElenbaasEngine(unittest.TestCase):
    """Tests the Elenbaas engine.

    Contains both unit tests at the method level and at the system level
    (elenbaas_engine).
    """

    def setUp(self):
        """Generates the necessary data to represent a typical methods usage situation.

        The results are compared to validated data.
        """
        self.engine = elen_engine
        self.session = ElenbaasSession(delete_simulation_files=True)

        ar, h2, n2, o2 = 0.1, 0.2, 0.3, 0.4

        properties_dict = io.loadmat(os.path.join(self.session._case_files,"properties.mat"))
        properties = list(properties_dict.items())
        a100thd = np.asarray(properties[3][1])
        a100tra = np.asarray(properties[4][1])
        h100thd = np.asarray(properties[5][1])
        h100tra = np.asarray(properties[6][1])
        n100thd = np.asarray(properties[7][1])
        n100tra = np.asarray(properties[8][1])
        o100thd = np.asarray(properties[9][1])
        o100tra = np.asarray(properties[10][1])

        self.data_tra = a100tra
        self.data_tra[:,2:] = ar*a100tra[:,2:] + h2*h100tra[:,2:] + \
                           n2*n100tra[:,2:] + o2*o100tra[:,2:]
        self.data_thd = a100thd
        self.data_thd[:,2:] = ar*a100thd[:,2:] + h2*h100thd[:,2:] + \
                           n2*n100thd[:,2:] + o2*o100thd[:,2:]

        self.T = 800.

    def test_rad_h2(self):
        """Tests the `_rad_h2` method."""
        self.assertAlmostEqual(80., self.engine._rad_h2(self.T), delta = 1e-3)

    def test_rad_n2(self):
        """Tests the `_rad_n2` method."""
        self.assertAlmostEqual(3.692, self.engine._rad_n2(self.T), delta = 1e-3)

    def test_rad_o2(self):
        """Tests the `_rad_o2` method."""
        self.assertAlmostEqual(167., self.engine._rad_o2(self.T), delta = 1e-3)

    def test_rad_ar(self):
        """Tests the `_rad_ar` method."""
        self.assertAlmostEqual(18.774, self.engine._rad_ar(self.T), delta = 1e-3)

    def test_density(self):
        """Tests the `_density` method."""
        self.assertAlmostEqual(0.3899, self.engine._density(self.T,self.data_thd), delta = 1e-3)

    def test_elec_cond(self):
        """Tests the `_elec_cond` method."""
        self.assertEqual(2.16819e-05, self.engine._elec_cond(self.T,self.data_tra))

    def test_thermal_cond(self):
        """Tests the `_thermal_cond` method."""
        self.assertEqual(0.1227346, self.engine._thermal_cond(self.T,self.data_tra))

    def test_viscosity(self):
        """Tests the `_viscosity` method."""
        self.assertEqual(3.45126e-05, self.engine._viscosity(self.T,self.data_tra))

class TestElenbaasSession(unittest.TestCase):
    """Tests the ElenbaasSession.

    Tests at the method level the methods that do not belong to the wrapper
    API, such methods have been already tested in `test_session.py`.
    """
    session: ElenbaasSession

    def test_get_property(self):
        """Tests the `get_property` method."""
        with ElenbaasSession(delete_simulation_files=True) as session:
            wrapper = onto.NanoFOAMWrapper(session=session)

            inlet_1 = onto.InletDiameter(value=13e-3,
                                         unit='m',
                                         name = 'Inlet Diameter')
            inlet_2 = onto.InletDiameter(value=8e-3,
                                         unit='mm',
                                         name = 'Another inlet Diameter')
            inlet_3 = onto.InletDiameter(value=32e-3,
                                         unit='dm',
                                         name = 'Another another inlet Diameter')
            wrapper.add(inlet_1, inlet_2, inlet_3)

            res = session._get_property(wrapper, ['Inlet Diameter'])
            self.assertIsInstance(res, float)
            self.assertEqual(13e-3, res)

            res = session._get_property(wrapper, ['Inlet Diameter',
                                             'Another inlet Diameter',
                                             'Another another inlet Diameter'])
            self.assertIsInstance(res, list)
            self.assertEqual(3, len(res))
            self.assertListEqual(
                [13e-3, 8e-3, 32e-3],
                [x for x in res]
            )




if __name__ == '__main__':
    unittest.main()