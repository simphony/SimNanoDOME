"""Tests the SimPhoNy wrapper API methods."""

import unittest, os
from uuid import UUID

from common import generate_cuds, get_key_simulation_cuds
from osp.core.cuds import Cuds
from osp.core.namespaces import nanofoam as onto
from osp.core.utils import delete_cuds_object_recursively

from osp.wrappers.simcfd.cfdsession import CFDSession
from osp.wrappers.simelenbaas.elenbaassession import ElenbaasSession


class TestWrapper(unittest.TestCase):
    """Test of all wrapper API methods for the `CoupledReactorSession`."""

    template_wrapper: Cuds

    def setUp(self) -> None:
        """Generates the necessary CUDS to represent a simulation.

        The results are stored in `self.template_wrapper`.
        """
        self.template_wrapper = generate_cuds()

    def test_str(self):
        """Tests the `__str__` method of the session."""
        session = CFDSession(delete_simulation_files=True)
        try:
            self.assertIsInstance(str(session), str)
            self.assertIn('OpenFoam', str(session))
        finally:
            session.close()

    def test_load_from_backend(self):
        """Tests the `_load_from_backend` method of the session."""
        with CFDSession(delete_simulation_files=True) as session:
            onto.NanoFOAMWrapper(session=session)
            temp = onto.Temperature(value=8200.,
                             unit="K",
                             name="Temperature")

            fake_uid = UUID(int=8)

            self.assertListEqual(
                [None],
                list(session._load_from_backend([fake_uid])))
            self.assertListEqual(
                [temp.uid],
                list(x.uid
                     for x in session._load_from_backend([temp.uid])))

    def test_initialize_and_run(self):
        """Runs the simulation.

        Running the simulation for the first time involves calling the
        `_initialize` method and then the `_run` method.
        """
        key_cuds = get_key_simulation_cuds(self.template_wrapper)
        source = key_cuds['source']
        accuracy_level = key_cuds['accuracy_level']

        with ElenbaasSession(delete_simulation_files=True) as elen:
            # Run elenbaas
            elenwrapper = onto.NanoFOAMWrapper(session=elen)
            elenwrapper.add(source, accuracy_level)

            elen.run()

            # Get the plasma properties calculated from Elenbaas
            plasma = elenwrapper.get(source.uid).get(oclass=onto.Plasma)[0]
            source.add(plasma,rel=onto.hasPart)

            with CFDSession(delete_simulation_files=True) as session:
                wrapper = onto.NanoFOAMWrapper(session=session)
                wrapper.add(source, accuracy_level)

                session.test = True
                session.run()

                sim_dir = session._case_dir

                self.assertTrue(session._initialized)

            self.assertFalse(os.path.isdir(sim_dir))



if __name__ == '__main__':
    unittest.main()
