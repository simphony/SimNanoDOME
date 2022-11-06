"""Test typical usage of the software (end-to-end test)."""

import unittest, filecmp, os, multiprocessing
import numpy as np

from osp.core.namespaces import nanofoam as onto
from osp.core.cuds import Cuds

from common import generate_cuds, get_key_simulation_cuds
from osp.wrappers.simelenbaas.elenbaassession import \
    ElenbaasSession
from osp.wrappers.simcfd.cfdsession import CFDSession
from osp.wrappers.simnanodome import NanoDOMESession


class TestWrapper(unittest.TestCase):
    """Typical usage of the CFD Session."""

    template_wrapper: Cuds

    def setUp(self) -> None:
        """Generates the necessary CUDS to represent a simulation.

        The results are stored in `self.template_wrapper`. This function
        runs before each test method from this test case.
        """
        self.template_wrapper = generate_cuds()

    def test_cfd(self):
        """CFDSession usage test."""
        # Recover CUDS.
        key_cuds = get_key_simulation_cuds(self.template_wrapper)
        source = key_cuds['source']
        accuracy_level = key_cuds['accuracy_level']
        reactor = key_cuds['reactor']
        tcond = key_cuds['tcond']

        with ElenbaasSession(delete_simulation_files=True) as elen:

            # Run elenbaas
            elenwrapper = onto.NanoFOAMWrapper(session=elen)
            elenwrapper.add(source, accuracy_level)

            elen.run()

            # Get the plasma properties calculated from Elenbaas
            plasma = elenwrapper.get(source.uid).get(oclass=onto.Plasma)[0]
            source.add(plasma,rel=onto.hasPart)

            with CFDSession(delete_simulation_files=True) as cfd:

                # Run cfd
                cfdwrapper = onto.NanoFOAMWrapper(session=cfd)
                cfdwrapper.add(source, accuracy_level)

                cfd.test = True
                cfd.run()

                streams = cfdwrapper.get(source.uid).get(reactor.uid).get(tcond.uid) \
                            .get(oclass=onto.TemperatureStreamline)

                self.assertTrue(len(streams),5)

    def test_linked_low(self):
        """Linked method with Low Accuracy usage test."""
        # Recover CUDS.
        key_cuds = get_key_simulation_cuds(self.template_wrapper)
        source = key_cuds['source']
        reactor = key_cuds['reactor']
        tcond = key_cuds['tcond']

        with ElenbaasSession(delete_simulation_files=True) as elen:

            # Run elenbaas
            ##########################################################
            elenwrapper = onto.NanoFOAMWrapper(session=elen)
            accuracy_level = onto.LowAccuracyLevel()
            elenwrapper.add(source, accuracy_level)

            elen.run()

            # Get the plasma properties calculated from Elenbaas
            plasma = elenwrapper.get(source.uid).get(oclass=onto.Plasma)[0]
            source.add(plasma,rel=onto.hasPart)

            with CFDSession(delete_simulation_files=True) as cfd:

                # Run cfd
                ##########################################################
                cfdwrapper = onto.NanoFOAMWrapper(session=cfd)
                accuracy_level = onto.LowAccuracyLevel()
                cfdwrapper.add(source, accuracy_level)

                cfd.test = True
                cfd.run()

                # Run nanodome processes
                ##########################################################

                # Get the TemperatureStreamline CUDS from the cfd session
                streams = cfdwrapper.get(source.uid).get(reactor.uid).get(tcond.uid) \
                            .get(oclass=onto.TemperatureStreamline)

                self.assertTrue(len(streams),5)

                procs = []
                for idx in range(len(streams)):
                    parent_conn, child_conn = multiprocessing.Pipe()
                    p = multiprocessing.Process(target=nano_link, \
                                args=(True,source,reactor,tcond,streams[idx],child_conn,accuracy_level,))
                    procs.append([p,parent_conn,child_conn])
                    p.start()

                res = []
                for p,pa,ch in procs:
                    res.append(pa.recv())
                    p.join()

                prims = []
                parts = []
                for pr,pa in res:
                    prims.append(pr)
                    parts.append(pa)

                diams = []
                numbs = []
                vols = []

                for part in parts:
                    for data in part[0]:
                        if data[1] == str(onto.ParticleDiameter):
                            diams.append(data[0])
                        elif data[1] == str(onto.ParticleNumberDensity):
                            numbs.append(data[0])
                        elif data[1] == str(onto.ParticleVolumePercentage):
                            vols.append(data[0])


                mean_diam = np.average(np.asarray(diams))
                numb_dens = np.average(np.asarray(numbs))
                vol_frac = np.average(np.asarray(vols))
                mean_prim_size = onto.ParticleDiameter(
                    value=mean_diam, unit='nm', name='Mean particles diameter')
                prim_numb_dens = onto.ParticleNumberDensity(
                    value=numb_dens, unit='#/m3', name='Mean particles number density')
                prim_vol_perc = onto.ParticleVolumePercentage(
                    value=vol_frac, unit='m3/m3', name='Mean particles volume percentage')

                result = onto.Bin()
                result.add(mean_prim_size, prim_numb_dens, prim_vol_perc,
                            rel=onto.hasProperty)
                particles = onto.NanoParticleSizeDistribution(name = 'Particles')
                particles.add(result, rel=onto.hasPart)
                reactor.add(particles)

    def test_linked_medium(self):
        """Linked method with Medium Accuracy usage test."""
        # Recover CUDS.
        key_cuds = get_key_simulation_cuds(self.template_wrapper)
        source = key_cuds['source']
        reactor = key_cuds['reactor']
        tcond = key_cuds['tcond']

        with ElenbaasSession(delete_simulation_files=True) as elen:

            # Run elenbaas
            ##########################################################
            elenwrapper = onto.NanoFOAMWrapper(session=elen)
            accuracy_level = onto.MediumAccuracyLevel()
            elenwrapper.add(source, accuracy_level)

            elen.run()

            # Get the plasma properties calculated from Elenbaas
            plasma = elenwrapper.get(source.uid).get(oclass=onto.Plasma)[0]
            source.add(plasma,rel=onto.hasPart)

            with CFDSession(delete_simulation_files=True) as cfd:

                # Run cfd
                ##########################################################
                cfdwrapper = onto.NanoFOAMWrapper(session=cfd)
                accuracy_level = onto.MediumAccuracyLevel()
                cfdwrapper.add(source, accuracy_level)

                cfd.test = True
                cfd.run()

                # Run nanodome processes
                ##########################################################

                # Get the TemperatureStreamline CUDS from the cfd session
                streams = cfdwrapper.get(source.uid).get(reactor.uid).get(tcond.uid) \
                            .get(oclass=onto.TemperatureStreamline)

                self.assertTrue(len(streams),5)

                procs = []
                for idx in range(len(streams)):
                    parent_conn, child_conn = multiprocessing.Pipe()
                    p = multiprocessing.Process(target=nano_link, \
                                args=(True,source,reactor,tcond,streams[idx],child_conn,accuracy_level,))
                    procs.append([p,parent_conn,child_conn])
                    p.start()

                res = []
                for p,pa,ch in procs:
                    res.append(pa.recv())
                    p.join()

                prims = []
                parts = []
                for pr,pa in res:
                    prims.append(pr)
                    parts.append(pa)

                part_diams = []
                part_numbs = []
                prim_diams = []
                prim_numbs = []
                frac_dims = []

                for prim in prims:
                    for data_bin in prim:
                        for data in data_bin:
                            if data[1] == str(onto.ParticleDiameter):
                                prim_diams.append(data[0])
                            elif data[1] == str(onto.ParticleNumberDensity):
                                prim_numbs.append(data[0])

                for part in parts:
                    for data_bin in part:
                        for data in data_bin:
                            if data[1] == str(onto.ParticleDiameter):
                                part_diams.append(data[0])
                            elif data[1] == str(onto.ParticleNumberDensity):
                                part_numbs.append(data[0])
                            elif data[1] == str(onto.ParticleFractalDimension):
                                frac_dims.append(data[0])

                # Create and fill bins then add them to the NanoParticleSizeDistribution CUDS
                pr_counts, pr_bins = np.histogram(prim_diams,range=(np.amin(prim_diams), \
                                        np.amax(prim_diams)),weights=prim_numbs)

                pa_counts, pa_bins = np.histogram(part_diams,range=(np.amin(part_diams), \
                                    np.amax(part_diams)),weights=part_numbs)

                fd_counts, fd_bins = np.histogram(frac_dims,range=(np.amin(frac_dims), \
                                    np.amax(frac_dims)),weights=part_numbs)

                particles = onto.NanoParticleSizeDistribution(name = 'Particles')
                for idx,numb in enumerate(pa_counts):
                    result = onto.Bin()
                    size_dist = onto.ParticleNumberDensity(value=numb,
                                        unit="#/m3",name="Size distribution")
                    size_class = onto.ParticleDiameter(value=pa_bins[idx],
                                        unit="nm",name="Size class")
                    fract_dim = onto.ParticleFractalDimension(value=fd_bins[idx],
                                        unit="~",name="Mean fractal dimension")
                    result.add(size_dist, size_class, fract_dim, rel=onto.hasProperty)
                    particles.add(result, rel=onto.hasPart)
                reactor.add(particles)

                primaries = onto.NanoParticleSizeDistribution(name = 'Primaries')
                for idx,numb in enumerate(pr_counts):
                    result = onto.Bin()
                    size_dist = onto.ParticleNumberDensity(value=numb,
                                        unit="#/m3",name="Size distribution")
                    size_class = onto.ParticleDiameter(value=pr_bins[idx],
                                        unit="nm",name="Size class")
                    result.add(size_dist, size_class, rel=onto.hasProperty)
                    primaries.add(result, rel=onto.hasPart)
                reactor.add(primaries)

# Parallel linked execution utility
def nano_link(del_files,source,reactor,tcond,stream,conn,accuracy_level):
    with NanoDOMESession(delete_simulation_files = del_files) as nano:
        nanowrapper = onto.NanoFOAMWrapper(session=nano)
        stream.name = str(nanowrapper.uid)
        tcond.add(stream,rel=onto.hasProperty)
        primaries = onto.NanoParticleSizeDistribution(name = 'Primaries')
        particles = onto.NanoParticleSizeDistribution(name = 'Particles')
        reactor.add(primaries, particles, rel = onto.hasPart)

        nanowrapper.add(source, accuracy_level)
        if accuracy_level is onto.LowAccuracyLevel():
            nano.eng.tf = 2.5e-4
        else:
            nano.eng.tf = 1e-7
        nano.run()
        primaries = nanowrapper.get(source.uid).get(reactor.uid).get(primaries.uid)
        particles = nanowrapper.get(source.uid).get(reactor.uid).get(particles.uid)

        prims = []
        for idx,bins in enumerate(primaries.get()):
            data_bin = []
            for data in bins.get():
                data_bin.append([data.value, str(data.oclass)])
            prims.append(data_bin)

        parts = []
        for idx,bins in enumerate(particles.get()):
            data_bin = []
            for data in bins.get():
                 data_bin.append([data.value, str(data.oclass)])
            parts.append(data_bin)

        conn.send([prims,parts])
        conn.close()

if __name__ == '__main__':
    unittest.main()
