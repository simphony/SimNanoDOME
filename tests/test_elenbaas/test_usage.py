"""Test typical usage of the software (end-to-end test)."""

import unittest, filecmp, os

from osp.core.namespaces import nanofoam as onto
from osp.core.cuds import Cuds

from .common import generate_cuds, get_key_simulation_cuds
from osp.wrappers.simelenbaas.elenbaassession import \
    ElenbaasSession


class TestWrapper(unittest.TestCase):
    """Typical usage of the Elenbaas Session."""

    template_wrapper: Cuds

    def setUp(self) -> None:
        """Generates the necessary CUDS to represent a simulation.

        The results are stored in `self.template_wrapper`. This function
        runs before each test method from this test case.
        """
        self.template_wrapper = generate_cuds()

    def test_elenbaas(self):
        """ElenbaasSession usage test."""
        # Recover CUDS.
        key_cuds = get_key_simulation_cuds(self.template_wrapper)
        source = key_cuds['source']
        accuracy_level = key_cuds['accuracy_level']

        with ElenbaasSession(delete_simulation_files=True) as session:
            wrapper = onto.NanoFOAMWrapper(session=session)
            wrapper.add(source, accuracy_level)

            session.run()

            plasma = wrapper.get(source.uid).get(oclass=onto.Plasma)[0]

            # Validate results
            for prop in plasma.get():
                val_path = os.path.join(os.path.dirname(os.path.abspath(__file__)),'validation',prop.path.split('/')[-1])
                self.assertTrue(filecmp.cmp(prop.path,val_path))




if __name__ == '__main__':
    unittest.main()
