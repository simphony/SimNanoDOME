"""Tests the SimPhoNy wrapper API methods."""

import csv
import os
import unittest
from uuid import UUID

from .common import generate_cuds, get_key_simulation_cuds
from osp.core.cuds import Cuds
from osp.core.namespaces import nanofoam as onto
from osp.core.utils import delete_cuds_object_recursively

import numpy as np
from osp.wrappers.simelenbaas.elenbaassession import \
    ElenbaasSession


class TestWrapper(unittest.TestCase):
    """Test of all wrapper API methods for the `ElenbaasSession`."""

    template_wrapper: Cuds

    def setUp(self) -> None:
        """Generates the necessary CUDS to represent a simulation.

        The results are stored in `self.template_wrapper`.
        """
        self.template_wrapper = generate_cuds()

    def test_str(self):
        """Tests the `__str__` method of the session."""
        session = ElenbaasSession(delete_simulation_files=True)
        try:
            self.assertIsInstance(str(session), str)
            self.assertIn('Elenbaas session for plasma source conditions', str(session))
        finally:
            session.close()

    def test_load_from_backend(self):
        """Tests the `_load_from_backend` method of the session."""
        with ElenbaasSession(delete_simulation_files=True) as session:
            onto.NanoFOAMWrapper(session=session)
            input_power = onto.InputPower(value=15000., unit='W',
                                      name='Input Power')

            fake_uid = UUID(int=8)

            self.assertListEqual(
                [None],
                list(session._load_from_backend([fake_uid])))
            self.assertListEqual(
                [input_power.uid],
                list(x.uid
                     for x in session._load_from_backend([input_power.uid])))

    def test_initialize_and_run_close(self):
        """Runs the simulation.

        Running the simulation for the first time involves calling the
        `_initialize` method and then the `_run` method.
        """
        key_cuds = get_key_simulation_cuds(self.template_wrapper)
        source = key_cuds['source']
        accuracy_level = key_cuds['accuracy_level']

        with ElenbaasSession(delete_simulation_files=True) as session:
            wrapper = onto.NanoFOAMWrapper(session=session)
            wrapper.add(source, accuracy_level)
            session.run()

            simulation_dir = session._case_dir

            self.assertTrue(session._initialized)

            plasma = wrapper.get(source.uid).get(oclass=onto.Plasma)[0]

            # Validate results
            for prop in plasma.get():
                val_path = os.path.join(os.path.dirname(os.path.abspath(__file__)),'validation',prop.path.split('/')[-1])
                # detect csv delimiters
                with open(prop.path) as file:
                    sniffer = csv.Sniffer()
                    dialect = sniffer.sniff(file.readline())
                    delimiter1 = str(dialect.delimiter)
                with open(val_path) as file:
                    sniffer = csv.Sniffer()
                    dialect = sniffer.sniff(file.readline())
                    delimiter2 = str(dialect.delimiter)
                file1 = np.genfromtxt(prop.path, delimiter=delimiter1)
                file2 = np.genfromtxt(val_path, delimiter=delimiter2)
                self.assertTrue(np.allclose(file1, file2))

        self.assertFalse(os.path.isdir(simulation_dir))




if __name__ == '__main__':
    unittest.main()
