"""Unit test examples, both at the "system" level and the "method" level."""

import unittest

import matplotlib.pyplot as plt
import numpy as np
from osp.core.cuds import Cuds
from osp.core.namespaces import nanofoam as onto

from osp.wrappers.simcoupledreactor.coupledreactorsession import \
    CoupledReactorSession
from osp.wrappers.simcoupledreactor.simple_reactor_engine import \
    simple_reactor_engine


class TestReactorEngine(unittest.TestCase):
    """Tests the reactor engine.

    Contains both unit tests at the method level and at the system level
    (reactor engine class).
    """
    reactor_engine: simple_reactor_engine

    def setUp(self):
        """Generates the necessary CUDS to represent a simulation.

        The results are stored in `self.template_wrapper`.
        """
        self.reactor_engine = simple_reactor_engine()
        self.n_cells = 20
        self.L = 1
        self.cbnd = 0.01
        self.x = 0.01

    def test_set_domain(self):
        """Tests the `set_domain` method."""
        self.reactor_engine.set_domain(self.n_cells, self.L, self.cbnd)
        self.assertEqual(self.n_cells+2, self.reactor_engine.nodes)
        self.assertEqual(self.L / (self.n_cells + 1), self.reactor_engine.deltax)

    def test_get_T(self):
        """Tests the `get_T` method."""
        self.assertRaises(AttributeError, lambda: self.reactor_engine.get_T(self.x))

        self.reactor_engine.set_domain(self.n_cells, self.L, self.cbnd)

        self.assertLessEqual(
            self.reactor_engine.get_T(self.x) - 8807.273211302227,
            1e-6
        )

    def test_get_U(self):
        """Tests the `get_U` method."""
        self.assertRaises(AttributeError, lambda: self.reactor_engine.get_U(self.x))

        self.reactor_engine.set_domain(self.n_cells, self.L, self.cbnd)

        self.assertLessEqual(
            self.reactor_engine.get_U(self.x) - 73.50544028359914,
            1e-6
        )

    def test_get_p(self):
        """Tests the `get_p` method."""
        self.assertRaises(AttributeError, lambda: self.reactor_engine.get_p(self.x))

        self.reactor_engine.set_domain(self.n_cells, self.L, self.cbnd)

        self.assertLessEqual(
            self.reactor_engine.get_p(self.x) - 101367.40580415892,
            1e-6
        )

    def test_get_molar_mass(self):
        """Tests the `get_molar_mass` method."""
        self.assertEqual(28.085, self.reactor_engine.get_molar_mass('Si'))
        self.assertEqual(39.948, self.reactor_engine.get_molar_mass('Ar'))

    def test_dt(self):
        self.reactor_engine.set_domain(self.n_cells, self.L, self.cbnd)

        dt_calc = self.reactor_engine.dt()

        self.assertEqual(dt_calc, 7.258218053409755e-05)

    def test_run(self):
        """Tests the `run` method."""
        self.reactor_engine.set_domain(self.n_cells, self.L, self.cbnd)
        cs = np.zeros(self.reactor_engine.nodes)
        cs[0] = self.cbnd
        cs_n, U, T, p, dt = self.reactor_engine.run(1e-2, cs)

        for el in cs_n:
            self.assertGreater(el,0.)

    def test_reactor_engine_system(self):
        """System test from `osp.wrappers.simcoupledreactor.test`."""
        eng = simple_reactor_engine()

        nn = 50

        eng.set_domain(self.n_cells, self.L, self.cbnd)

        cs = [0.] * nn
        cs[0] = self.cbnd

        t = 0.

        while t < 1e-2:
            cs, U, T, p, dt = eng.run(t,cs)

            t += dt


class TestCoupledReactorSession(unittest.TestCase):
    """Tests the CoupledReactorSession.

    Tests at the method level the methods that do not belong to the wrapper
    API, such methods have been already tested in `test_session.py`.
    """
    session: CoupledReactorSession

    def test_get_obj(self):
        """Tests the `_get_obj` method."""
        with CoupledReactorSession(delete_simulation_files=True) as session:
            wrapper = onto.NanoFOAMWrapper(session=session)
            time1 = onto.Time(value=16.,
                              unit="s",
                              name="Simulation Time")
            time2 = onto.Time(value=17.,
                              unit="μs",
                              name="Another Time")
            time3 = onto.Time(value=18.,
                              unit="ns",
                              name="Third Time")
            wrapper.add(time1, time2, time3)

            res = session._get_obj(wrapper, ['Simulation Time'])
            self.assertIsInstance(res, Cuds)
            self.assertEqual(time1.uid, res.uid)
            self.assertIsInstance(res.value, float)
            self.assertEqual(16., res.value)
            self.assertEqual("s", res.unit)
            self.assertEqual("Simulation Time", res.name)

            res = session._get_obj(wrapper, ['Simulation Time',
                                             "Third Time",
                                             "Another Time"])
            self.assertIsInstance(res, list)
            self.assertEqual(3, len(res))
            self.assertListEqual(
                [16., 18., 17.],
                [x.value for x in res]
            )
            self.assertListEqual(
                ["s", "ns", "μs"],
                [x.unit for x in res]
            )
            self.assertListEqual(
                ["Simulation Time", "Third Time", "Another Time"],
                [x.name for x in res]
            )

    def test_get_property(self):
        """Tests the `_get_property` method."""
        with CoupledReactorSession(delete_simulation_files=True) as session:
            wrapper = onto.NanoFOAMWrapper(session=session)
            time1 = onto.Time(value=16.,
                              unit="s",
                              name="Simulation Time")
            time2 = onto.Time(value=17.,
                              unit="μs",
                              name="Another Time")
            time3 = onto.Time(value=18.,
                              unit="ns",
                              name="Third Time")
            wrapper.add(time1, time2, time3)

            res = session._get_property(wrapper, ['Simulation Time'])
            self.assertIsInstance(res, float)
            self.assertEqual(16., res)

            res = session._get_property(wrapper, ['Simulation Time',
                                                  "Third Time",
                                                  "Another Time"])
            self.assertIsInstance(res, list)
            self.assertEqual(3, len(res))
            self.assertListEqual(
                [16., 18., 17.],
                [x for x in res]
            )


if __name__ == '__main__':
    unittest.main()
