"""Unit test examples, both at the "system" level and the "method" level."""

import unittest, os, filecmp, shutil

import matplotlib.pyplot as plt
import numpy as np
from scipy import io as io

from osp.core.cuds import Cuds
from osp.core.namespaces import nanofoam as onto

from osp.wrappers.simcfd.cfdsession import CFDSession


class TestCFDSession(unittest.TestCase):
    """Tests the CFDSession.

    Tests at the method level the methods that do not belong to the wrapper
    API, such methods have been already tested in `test_session.py`.
    """
    session: CFDSession

    def test_get_property(self):
        """Tests the `get_property` method."""
        with CFDSession(delete_simulation_files=True) as session:
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


    def test_derivate(self):
        """Tests the `_derivate` method."""
        with CFDSession(delete_simulation_files=True) as session:
            wrapper = onto.NanoFOAMWrapper(session=session)

            # Read data file
            with open(os.path.dirname(os.path.realpath(__file__))+"/data/entropy","r") as file:
                data = []
                for line in file.readlines():
                    row = line.split(',')
                    data.append([float(row[0]),float(row[1])])
            file.close()

            der = session._derivate(data)

            with open(os.path.dirname(os.path.realpath(__file__))+"/res", "w") as out_der:
                out_der.write('(' + '\n')
                for item in der:
                    out_der.write('(' + str(item[0]) + ' ' + str(item[1]) + ')' + '\n')
                out_der.write(')')
            out_der.close()

            self.assertTrue(filecmp.cmp(os.path.dirname(os.path.realpath(__file__))+"/validation/dSdT",
                                        os.path.dirname(os.path.realpath(__file__))+"/res"))
            os.remove(os.path.dirname(os.path.realpath(__file__))+"/res")


    def test_create_launcher(self):
        """Tests the `_create_launcher` method."""
        with CFDSession(delete_simulation_files=True) as session:
            wrapper = onto.NanoFOAMWrapper(session=session)

            os.makedirs(os.path.dirname(os.path.realpath(__file__))+"/tmp/templates")
            session._case_dir = os.path.dirname(os.path.realpath(__file__))+"/tmp"
            shutil.copyfile(os.path.dirname(os.path.realpath(__file__))+"/data/Allprep_template",session._case_dir+"/templates/Allprep_template")
            shutil.copyfile(os.path.dirname(os.path.realpath(__file__))+"/data/Allrun_template",session._case_dir+"/templates/Allrun_template")

            session._create_launcher(1)

            self.assertTrue(filecmp.cmp(os.path.dirname(os.path.realpath(__file__))+"/validation/Allrun",
                                            session._case_dir+"/Allrun"))

            self.assertTrue(filecmp.cmp(os.path.dirname(os.path.realpath(__file__))+"/validation/Allprep",
                                            session._case_dir+"/Allprep"))


    def test_create_blockmesh(self):
        """Tests the `_create_blockmesh` method."""
        with CFDSession(delete_simulation_files=True) as session:
            wrapper = onto.NanoFOAMWrapper(session=session)

            os.makedirs(os.path.dirname(os.path.realpath(__file__))+"/tmp/templates")
            os.makedirs(os.path.dirname(os.path.realpath(__file__))+"/tmp/system")
            session._case_dir = os.path.dirname(os.path.realpath(__file__))+"/tmp"
            shutil.copyfile(os.path.dirname(os.path.realpath(__file__))+"/data/blockMeshDict_template",session._case_dir+"/templates/blockMeshDict_template")

            session._create_blockmesh(0.5,1.1,13e-3)

            self.assertTrue(filecmp.cmp(os.path.dirname(os.path.realpath(__file__))+"/validation/blockMeshDict",
                                            session._case_dir+"/system/blockMeshDict"))


    def test_import_stream_file(self):
        """Tests the `_import_stream_file` method."""
        with CFDSession(delete_simulation_files=True) as session:
            wrapper = onto.NanoFOAMWrapper(session=session)

            os.makedirs(os.path.dirname(os.path.realpath(__file__))+"/tmp")
            session._case_dir = os.path.dirname(os.path.realpath(__file__))+"/tmp"

            shutil.copyfile(os.path.dirname(os.path.realpath(__file__))+"/data/streamline_1.csv",session._case_dir+"/streamline_1.csv")

            res = session._import_stream_file(session._case_dir+"/streamline_1.csv")

            self.assertGreater(len(res), 0)
            self.assertTrue(res.dtype,float)


    def test_create_stream_files(self):
        """Tests the `_create_stream_files` method."""
        with CFDSession(delete_simulation_files=True) as session:
            wrapper = onto.NanoFOAMWrapper(session=session)

            os.makedirs(os.path.dirname(os.path.realpath(__file__))+"/tmp")
            session._case_dir = os.path.dirname(os.path.realpath(__file__))+"/tmp"

            session._create_stream_files(os.path.dirname(os.path.realpath(__file__))+"/data/",session._case_dir)

            for idx in range(1,5):
                self.assertTrue(filecmp.cmp(session._case_dir+"/streamline_"+str(idx)+".csv",
                                os.path.dirname(os.path.realpath(__file__))+"/validation/"+"streamline_"+str(idx)+".csv"))


    def test_create_stream_sets(self):
        """Tests the `_create_stream_sets` method."""
        with CFDSession(delete_simulation_files=True) as session:
            wrapper = onto.NanoFOAMWrapper(session=session)

            os.makedirs(os.path.dirname(os.path.realpath(__file__))+"/tmp/templates")
            os.makedirs(os.path.dirname(os.path.realpath(__file__))+"/tmp/system")
            session._case_dir = os.path.dirname(os.path.realpath(__file__))+"/tmp"
            shutil.copyfile(os.path.dirname(os.path.realpath(__file__))+"/data/blockMeshDict_template",session._case_dir+"/templates/blockMeshDict_template")
            shutil.copyfile(os.path.dirname(os.path.realpath(__file__))+"/data/streamSets_template",session._case_dir+"/templates/streamSets_template")

            session._create_stream_sets(13e-3)

            self.assertTrue(filecmp.cmp(os.path.dirname(os.path.realpath(__file__))+"/validation/streamSets",
                                            session._case_dir+"/system/streamSets"))



if __name__ == '__main__':
    unittest.main()
