"""Unit test examples, both at the "system" level and the "method" level."""

import unittest, os

import matplotlib.pyplot as plt
import numpy as np
from osp.core.cuds import Cuds
from osp.core.namespaces import nanofoam as onto

from .common import generate_cuds, get_key_simulation_cuds
from osp.wrappers.simnanodome.nanosession import NanoDOMESession
from osp.wrappers.simnanodome.nano_engine import nano_engine


class TestNanoEngine(unittest.TestCase):
    """Tests the nano engine.

    Contains both unit tests at the method level and at the system level
    (nano engine class).
    """
    nano_engine: nano_engine

    def setUp(self):
        """Generates the necessary CUDS to represent a simulation.

        The results are stored in `self.template_wrapper`.
        """
        self.nano_engine = nano_engine()
        self.template_wrapper = generate_cuds()

    def test_DataReader(self):
        """Tests the `DataReader` class and methods."""
        reader = nano_engine.DataReader(os.path.dirname(os.path.realpath(__file__))+"/data/PBM_plot.dat"," \t ")
        test = reader.getData()[1:]

        self.assertIsInstance(test,list)
        self.assertGreater(len(test),0)
        self.assertIsInstance(float(test[0][0]),float)

    def test_PSD_post(self):
        """Tests the `PSD_post` method."""
        # Get required inputs
        reader = nano_engine.DataReader(os.path.dirname(os.path.realpath(__file__))+"/data/PBM_plot.dat"," \t ")
        voll = float(reader.getData()[1:][-1][10])

        reader = nano_engine.DataReader(os.path.dirname(os.path.realpath(__file__))+"/data/PBM_aggregates_sizes.dat",", ")
        pps = [float(i.strip("\n").replace('[','').replace(']','')) for i in reader.getData()[-1]]

        # Call the method
        psd_diams, psd_numbs = nano_engine.PSD_post(None,pps,float(voll))

        self.assertEqual(15, len(psd_diams))
        self.assertEqual(15, len(psd_numbs))

    def test_counter_trigger(self):
        """Tests the `counter_trigger` method."""
        PRINT_EVERY = 20
        LL = 101
        CALLS = 0

        for INT in range(1,LL):
            if INT % PRINT_EVERY == 0:
                self.assertTrue(nano_engine.counter_trigger(None, INT, PRINT_EVERY))
                CALLS += 1
        self.assertEqual(5, CALLS)

    def test_Temp_gradient(self):
        """Tests the `Temp_gradient` method."""
        time = nano_engine.stream_evo(nano_engine,os.path.dirname(os.path.realpath(__file__))+"/data/streamline_1.csv",0)
        temp = nano_engine.stream_evo(nano_engine,os.path.dirname(os.path.realpath(__file__))+"/data/streamline_1.csv",1)
        tt = 0.001

        der = nano_engine.Temp_gradient(None,tt,time,temp)

        self.assertEqual(-175614.67614668683, der)

    def test_get_prec_mass(self):
        """Tests the `get_prec_mass` method."""
        fin = 1.660538921e-27 * 55.845
        val = nano_engine.get_prec_mass(None,"Fe")

        self.assertEqual(fin, val)

    def test_get_gas_mass(self):
        """Tests the `get_gas_mass` method."""
        fin = 1.660538921e-27 * 2.014
        val = nano_engine.get_gas_mass(None,"H2")

        self.assertEqual(fin, val)

    def test_get_bulk_liquid(self):
        """Tests the `get_bulk_liquid` method."""
        fin = 2700.
        val = nano_engine.get_bulk_liquid(None,"Al")

        self.assertEqual(fin, val)

    def test_get_bulk_solid(self):
        """Tests the `get_bulk_solid` method."""
        fin = 8960.
        val = nano_engine.get_bulk_solid(None,"Cu")

        self.assertEqual(fin, val)

    def test_get_melting_point(self):
        """Tests the `get_melting_point` method."""
        fin = 1687.
        val = nano_engine.get_melting_point(None,"Si")

        self.assertEqual(fin, val)

    def test_set_network(self):
        """Tests the `set_network` method."""
        specs = ["Si", "Ar", "He"]
        cs = [
            [0.06, 0.94, 0.0],
            [0.05, 0.95, 0.0],
            [0., 1.0, 0.0],
            [0., 1.0, 0.0]
            ]
        pp = [101325., 101325., 101325., 101325]
        TT = [1600., 1200., 800., 500]
        vels = [110., 60., 40., 2.]
        mass = 1.791193444382122e-25 # Si
        bulk_l = 1687.

        nano_engine.set_network(nano_engine, specs, pp, TT, cs, mass, bulk_l)

        self.assertTrue(nano_engine.net_set)

    def test_run_network(self):
        """Tests the `run_network` method."""
        tf = 1e-9
        specs = ["Si", "Ar", "He"]
        cs_0 = [
            [0.06, 0.94, 0.0],
            [0.05, 0.95, 0.0],
            [0., 1.0, 0.0],
            [0., 1.0, 0.0]
            ]
        pp = [101325., 101325., 101325., 101325]
        TT = [1600., 1200., 800., 500]
        vels = [110., 60., 40., 2.]
        mass = 1.791193444382122e-25 # Si
        bulk_l = 1687.

        cs = cs_0
        nano_engine.set_network(nano_engine, specs, pp, TT, cs, mass, bulk_l)
        self.assertTrue(nano_engine.net_set)

        cs = nano_engine.run_network(nano_engine, tf, pp, TT, vels, cs, specs)
        self.assertGreaterEqual(cs_0, cs)

    def test_nano_run_system_low(self):
        """Tests the `nano_run` method with Low accuracy."""
        with NanoDOMESession(delete_simulation_files=True) as session:
            wrapper = onto.NanoFOAMWrapper(session=session)
            session._pressure = 101325.
            session.species = ["Si", "Ar", "H2", "N2", "O2"]
            session._bool_stream = False
            session._temp_gradient = -1e+7
            session._temp_start = 2000
            session.eng.tf = 1e-8
            session._gas_fractions = [0.94, 0.04, 0., 0.]
            session._feedrate = 125/1000/3600
            session._flowrate = 40.
            session._dens_ref = 1.02
            session._acc_level = "Low"
            session._delete_simulation_files = True

            diam, numb, vol = session.eng.nano_run(session)

            self.assertIsInstance(diam,float)
            self.assertIsInstance(numb,float)
            self.assertIsInstance(vol,float)
            self.assertGreater(diam,0)
            self.assertGreater(numb,0)
            self.assertGreater(vol,0)

    def test_nano_run_system_medium(self):
        """Tests the `nano_run` method with Medium accuracy."""
        with NanoDOMESession(delete_simulation_files=True) as session:
            wrapper = onto.NanoFOAMWrapper(session=session)
            session._pressure = 101325.
            session.species = ["Si", "Ar", "H2", "N2", "O2"]
            session._bool_stream = False
            session._temp_gradient = -1e+7
            session._temp_start = 2000
            session.eng.tf = 1e-10
            session._gas_fractions = [0.94, 0.04, 0., 0.]
            session._feedrate = 125/1000/3600
            session._flowrate = 40.
            session._dens_ref = 1.02
            session._acc_level = "Medium"
            session._delete_simulation_files = True

            particles, primaries = session.eng.nano_run(session)
            self.assertGreater(len(particles), 0)
            self.assertGreater(len(primaries), 0)

    def test_nano_run_system_low_linked(self):
        """Tests the `nano_run` method with linked-like input."""
        with NanoDOMESession(delete_simulation_files=True) as session:
            wrapper = onto.NanoFOAMWrapper(session=session)
            session._pressure = 101325.
            session.species = ["Si", "Ar", "H2", "N2", "O2"]
            session._bool_stream = True
            session._stream = os.path.dirname(os.path.realpath(__file__))+"/data/streamline_1.csv"
            session.eng.tf = 2.5e-4
            session._gas_fractions = [0.94, 0.01, 0.02, 0.03]
            session._feedrate = 125/1000/3600
            session._flowrate = 40.
            session._dens_ref = 1.02
            session._acc_level = "Low"
            session._delete_simulation_files = True

            diam, numb, vol = session.eng.nano_run(session)

            self.assertIsInstance(diam,float)
            self.assertIsInstance(numb,float)
            self.assertIsInstance(vol,float)
            self.assertGreater(diam,0)
            self.assertGreater(numb,0)
            self.assertGreater(vol,0)

class TestNanoSession(unittest.TestCase):
    """Tests the NanoSession.

    Tests at the method level the methods that do not belong to the wrapper
    API, such methods have been already tested in `test_session.py`.
    """
    session: NanoDOMESession
    template_wrapper: Cuds

    def setUp(self) -> None:
        """Generates the necessary CUDS to represent a simulation.

        The results are stored in `self.template_wrapper`.
        """
        self.template_wrapper = generate_cuds()

    def test_get_obj(self):
        """Tests the `_get_obj` method."""
        with NanoDOMESession(delete_simulation_files=True) as session:
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
        with NanoDOMESession(delete_simulation_files=True) as session:
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

    def test_nano_run(self):
        """Tests the `_nano_run` method."""

        key_cuds = get_key_simulation_cuds(self.template_wrapper)

        with NanoDOMESession(delete_simulation_files=True) as session:
            wrapper = onto.NanoFOAMWrapper(session=session)

            reactor = key_cuds['reactor']
            source = key_cuds['source']

            accuracy_level = onto.LowAccuracyLevel()

            # Results CUDS
            particles = onto.NanoParticleSizeDistribution(name = 'Particles')
            primaries = onto.NanoParticleSizeDistribution(name = 'Primaries')
            reactor.add(particles, primaries, rel = onto.hasPart)
            wrapper.add(source, accuracy_level)

            # Run the session
            ##########################################################
            session.test = True
            session.eng.tf = 1e-8
            session.run()


    def test_nano_coupled_run(self):
        """Tests the `_nano_coupled_run` method."""
        with NanoDOMESession(delete_simulation_files=True) as session:
            wrapper = onto.NanoFOAMWrapper(session=session)

            # Set the accuracy level
            accuracy_level = onto.MediumAccuracyLevel()

            # Create precursor's species
            precursor = onto.SolidPrecursor()
            precursor_feed_rate = onto.FeedRate(value=1e-3, unit='kg/s',
                                                name='Feed Rate')
            precursor_type = onto.Type(name='Si')
            precursor.add(precursor_feed_rate,
                        precursor_type,
                        rel=onto.hasProperty)

            # Create plasma's source operative conditions
            source = onto.PlasmaSource()
            input_power = onto.InputPower(value=15000., unit='W',
                                        name='Input Power')
            flow_rate = onto.FlowRate(value=60.,
                                    unit='slpm',
                                    name='Flow Rate')
            source.add(input_power, flow_rate, rel=onto.hasProperty)
            source.add(precursor, rel=onto.hasPart)

            # Create plasma's composition
            comp = onto.GasComposition()
            arf = onto.MolarFraction(value=1., name='Ar', unit='~')
            h2f = onto.MolarFraction(value=0., name='H2', unit='~')
            n2f = onto.MolarFraction(value=0., name='N2', unit='~')
            o2f = onto.MolarFraction(value=0., name='O2', unit='~')
            comp.add(arf, h2f, n2f, o2f, rel=onto.hasPart)

            # Set reactor's dimensions
            reactor_geom = onto.CylindricalReactorDimensions()
            diameter = onto.Diameter(value=0.3, unit='m', name='Diameter')
            length = onto.Length(value=1.5, unit='m', name='Length')
            inlet_diameter = onto.InletDiameter(value=13e-3,
                                                unit='m',
                                                name='Inlet Diameter')
            reactor_geom.add(diameter,
                            length,
                            inlet_diameter,
                            rel=onto.hasPart)

            # Process' CUDS
            reactor = onto.nanoReactor()
            reactor.add(reactor_geom, rel=onto.hasPart)

            cells = []
            cells_number = 5
            temps = [1600, 1000, 800, 600, 500]
            vels = [110, 60, 30, 4, 2]
            for idx in range(cells_number):
                cell = onto.reactorCell(name=str(idx))

                comp = onto.GasComposition()

                if idx == 0:
                    prec_mol = onto.MolarFraction(value = 0.05 , name = precursor_type.name , unit = '~')
                    arf = onto.MolarFraction(value = 0.95, name = 'Ar', unit = '~')
                else:
                    prec_mol = onto.MolarFraction(value = 0. , name = precursor_type.name , unit = '~')
                    arf = onto.MolarFraction(value = 1., name = 'Ar', unit = '~')
                h2f = onto.MolarFraction(value=0., name='H2', unit='~')
                n2f = onto.MolarFraction(value=0., name='N2', unit='~')
                o2f = onto.MolarFraction(value=0., name='O2', unit='~')

                comp.add(prec_mol, arf, h2f, n2f, o2f, rel=onto.hasPart)

                primaries = onto.NanoParticleSizeDistribution(name='Primaries')
                particles = onto.NanoParticleSizeDistribution(name='Particles')

                cell.add(primaries, particles, rel=onto.hasPart)

                cell.add(onto.Velocity(value=vels[idx], name=str(idx), unit='m/s'))

                # Set thermodynamic conditions
                thermo_cond = onto.ThermoCond()
                pressure = onto.Pressure(value=101325, unit='m^2/s^2',
                                        name='Pressure')
                temp = onto.Temperature(value=temps[idx], unit='K',
                                        name='Temperature')
                thermo_cond.add(pressure, temp, rel=onto.hasPart)

                cell.add(thermo_cond, comp, rel=onto.hasPart)
                cells.append(cell)
                reactor.add(cell)

            time = onto.Time(value=0., unit="s", name="Simulation Time")
            dt = onto.Time(value=1e-8, unit="s", name="Current Timestep")
            reactor.add(time, dt, rel=onto.hasPart)
            source.add(reactor, rel=onto.hasProperty)

            wrapper.add(source, accuracy_level)

            session.test = True
            session.run()



if __name__ == '__main__':
    unittest.main()
