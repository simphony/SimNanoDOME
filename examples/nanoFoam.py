"""
@author: Giorgio La Civita, UNIBO DIN
"""

# SimNANODOME Engine
import multiprocessing, os, numpy as np, matplotlib.pyplot as plt, csv

from osp.wrappers.simcfd.cfdsession import CFDSession
from osp.wrappers.simnanodome.nanosession import NanoDOMESession
from osp.wrappers.simelenbaas.elenbaassession import ElenbaasSession
from osp.wrappers.simcoupledreactor.coupledreactorsession import CoupledReactorSession

from osp.core.namespaces import nanofoam as onto
from osp.core.utils import pretty_print

# Engine settings
#####################################################################
# modes supported: elenbaas (elenbaas only), nanodome (nanodome only),
# cfd (openfoam and elenbaas), linked (nanofoam), coupled (nanocouplefoam)
mode = 'nanodome'

# Create the computational mesh, boundary conditions and properties
#####################################################################

# Set the accuracy level
# accuracy_level = onto.LowAccuracyLevel()
accuracy_level = onto.MediumAccuracyLevel()
# accuracy_level = onto.HighAccuracyLevel()

# Create precursor's species
prec = onto.SolidPrecursor()
prec_feedrate = onto.FeedRate(value = 125/1000/3600, unit = 'kg/s', name = 'Feed Rate')
prec_type = onto.Type(name = 'Fe')
prec.add(prec_feedrate, prec_type, rel = onto.hasProperty)

# Create plasma's source operative conditions
source = onto.PlasmaSource()
ipower = onto.InputPower(value = 30e3, unit = 'W', name = 'Input Power')
flow_rate = onto.FlowRate(value = 40., unit = 'slpm', name = 'Flow Rate')
source.add(ipower, flow_rate, rel = onto.hasProperty)
source.add(prec, rel = onto.hasPart)

# Create plasma's composition
comp = onto.GasComposition()
arf = onto.MolarFraction(value = 1., name = 'Ar', unit = '~')
h2f = onto.MolarFraction(value = 0., name = 'H2', unit = '~')
n2f = onto.MolarFraction(value = 0., name = 'N2', unit = '~')
o2f = onto.MolarFraction(value = 0., name = 'O2', unit = '~')
comp.add(arf, h2f, n2f, o2f, rel = onto.hasPart)

# Set reactor's dimensions
reactor_geom = onto.CylindricalReactorDimensions()
diameter = onto.Diameter(value=0.250, unit='m', name = 'Diameter')
length = onto.Length(value=0.875, unit='m', name = 'Length')
inlet_diameter = onto.InletDiameter(value=13e-3, unit='m', name = 'Inlet Diameter')
reactor_geom.add(diameter, length, inlet_diameter, rel = onto.hasPart)

# Process' CUDS
reactor = onto.nanoReactor()
reactor.add(reactor_geom, rel = onto.hasPart)

# Plot utility
def plot_distributions(dists, time = 0., file_name = None, savefig = False):

    def plot_dist(bins,counts,name, file_name, savefig):
        plt.hist(bins,density=True,weights=counts)
        if 'fractal' in name:
            plt.xlabel('Fractal dimension [#]')
        else:
            plt.xlabel('Diamater [nm]')
        plt.ylabel(name)
        if savefig is True:
            plt.savefig(os.path.join(os.getcwd(),"PSDs", str(file_name)+".png"))
        else:
            plt.show()
        plt.clf()

    if savefig is True:
        path = os.path.join(os.getcwd(),"PSDs")
        if not os.path.exists(path):
            os.makedirs(path)

    for dd in dists:
        bins = []
        counts = []
        fracs = []
        for bin in dd.get():
            diam = bin.get(oclass=onto.ParticleDiameter)[0].value
            numb = bin.get(oclass=onto.ParticleNumberDensity)[0].value
            bins.append(diam)
            counts.append(numb)
            try:
                frac = bin.get(oclass=onto.ParticleFractalDimension)[0].value
                fracs.append(frac)
            except:
                pass
        # if len(fracs) > 0:
        #     plot_dist(fracs,counts,'Particles fractal dimension probability density [#]')
        if savefig is True:
            plot_dist(bins,counts,dd.name + ' diameter probability density [#]', str(time) + "_" + file_name, savefig)
        else:
            plot_dist(bins,counts,dd.name + ' diameter probability density [#]', file_name, savefig)

# Parallel linked execution utility
def nano_link(del_files,source,reactor,tcond,stream,conn):
    with NanoDOMESession(delete_simulation_files = del_files) as nano:
        nanowrapper = onto.NanoFOAMWrapper(session=nano)
        stream.name = str(nanowrapper.uid)
        tcond.add(stream,rel=onto.hasProperty)
        primaries = onto.NanoParticleSizeDistribution(name = 'Primaries')
        particles = onto.NanoParticleSizeDistribution(name = 'Particles')
        reactor.add(primaries, particles, rel = onto.hasPart)

        nanowrapper.add(source, accuracy_level)
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

# Run the wrappers based on input
#########################################################
if mode == 'cfd':

    # Set thermodynamic conditions
    tcond = onto.ThermoCond()
    pressure = onto.Pressure(value=101325, unit='m^2/s^2', name = 'Pressure')
    tcond.add(pressure, rel = onto.hasPart)

    reactor.add(tcond, comp, rel = onto.hasPart)
    source.add(reactor, rel = onto.hasProperty)

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

            cfd.run()

            streams = cfdwrapper.get(source.uid).get(reactor.uid).get(tcond.uid) \
                        .get(oclass=onto.TemperatureStreamline)

            for idx,stream in enumerate(streams,start=1):
                x = []
                y = []

                with open(stream.path,'r') as csvfile:
                    plots = csv.reader(csvfile, delimiter=',')
                    for row in plots:
                        x.append(float(row[0]))
                        y.append(float(row[1]))

                plt.plot(x,y)
                plt.xlabel('Time (s)')
                plt.ylabel('Temperature (K)')
                plt.title('Streamline number '+str(idx))
                plt.legend()
                plt.show()

elif mode == 'elenbaas':

    # Set thermodynamic conditions
    reactor.add(comp, rel = onto.hasPart)
    source.add(reactor, rel = onto.hasProperty)

    with ElenbaasSession(delete_simulation_files=True) as elen:

        elenwrapper = onto.NanoFOAMWrapper(session=elen)
        elenwrapper.add(source, accuracy_level)

        elen.run()

        plasma = elenwrapper.get(source.uid).get(oclass=onto.Plasma)[0]

        for idx,prop in enumerate(plasma.get(),start=1):
            if not prop.name == "Reference density":
                x = []
                y = []

                with open(prop.path,'r') as file:
                    plots = csv.reader(file, delimiter=',')
                    for row in plots:
                        try:
                            x.append(float(row[0]))
                            y.append(float(row[1]))
                        except:
                            pass
                file.close()

                plt.plot(x,y)

                if 'profile' in prop.name:
                    plt.xlabel('Radial distance (m)')
                else:
                    plt.xlabel('Temperature (K)')
                plt.ylabel(prop.name + ' ' + prop.unit)
                plt.title(prop.name)
                plt.show()

elif mode == 'nanodome':

    # Set thermodynamic conditions
    tcond = onto.ThermoCond()
    pressure = onto.Pressure(value=101325, unit='m^2/s^2', name = 'Pressure')
    temp_grad = onto.TemperatureGradient(value = -1e+7, unit = 'K/s', name = 'Temporal Temperature Gradient')
    temp = onto.Temperature(value = 2000, unit = 'K', name = 'Temperature')
    tcond.add(pressure, temp, temp_grad, rel = onto.hasPart)

    reactor.add(tcond, comp, rel = onto.hasPart)
    source.add(reactor, rel = onto.hasProperty)

    with NanoDOMESession(delete_simulation_files=True) as nano:
        nanowrapper = onto.NanoFOAMWrapper(session=nano)

        # Results CUDS
        particles = onto.NanoParticleSizeDistribution(name = 'Particles')
        primaries = onto.NanoParticleSizeDistribution(name = 'Primaries')
        reactor.add(particles, primaries, rel = onto.hasPart)
        nanowrapper.add(source, accuracy_level)

        # Run the session
        ##########################################################
        nano.run()

        # Get the results
        res = nanowrapper.get(source.uid).get(reactor.uid)
        particles = res.get(particles.uid)
        primaries = res.get(primaries.uid)

        # Histogram plotting examples for Particles and Primaries
        # for Medium and High Accuracy Levels

        if accuracy_level.is_a(onto.LowAccuracyLevel):
            pretty_print(particles)

        elif (accuracy_level.is_a(onto.MediumAccuracyLevel) or \
            accuracy_level.is_a(onto.HighAccuracyLevel)):

            plot_distributions([primaries,particles])

elif mode == 'linked':

    # Set thermodynamic conditions
    tcond = onto.ThermoCond()
    pressure = onto.Pressure(value=101325, unit='m^2/s^2', name = 'Pressure')
    tcond.add(pressure, rel = onto.hasPart)

    reactor.add(tcond, comp, rel = onto.hasPart)
    source.add(reactor, rel = onto.hasProperty)

    with ElenbaasSession(delete_simulation_files=True) as elen:

        # Run elenbaas
        ##########################################################
        elenwrapper = onto.NanoFOAMWrapper(session=elen)
        elenwrapper.add(source, accuracy_level)

        elen.run()

        # Get the plasma properties calculated from Elenbaas
        plasma = elenwrapper.get(source.uid).get(oclass=onto.Plasma)[0]
        source.add(plasma,rel=onto.hasPart)

        with CFDSession(delete_simulation_files=True) as cfd:

            # Run cfd
            ##########################################################
            cfdwrapper = onto.NanoFOAMWrapper(session=cfd)
            cfdwrapper.add(source, accuracy_level)

            cfd.run()

            # Run nanodome processes
            ##########################################################

            # Get the TemperatureStreamline CUDS from the cfd session
            streams = cfdwrapper.get(source.uid).get(reactor.uid).get(tcond.uid) \
                        .get(oclass=onto.TemperatureStreamline)
            procs = []

            for idx in range(len(streams)):
                parent_conn, child_conn = multiprocessing.Pipe()
                p = multiprocessing.Process(target=nano_link, \
                            args=(True,source,reactor,tcond,streams[idx],child_conn,))
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

            if accuracy_level.is_a(onto.LowAccuracyLevel):

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

            else:
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

            # Histogram plotting examples for Particles and Primaries
            # for Medium and High Accuracy Levels

            if accuracy_level.is_a(onto.LowAccuracyLevel):
                pretty_print(particles)

            elif (accuracy_level.is_a(onto.MediumAccuracyLevel) or \
                accuracy_level.is_a(onto.HighAccuracyLevel)):

                plot_distributions([primaries,particles])

elif mode == 'coupled':

    if not accuracy_level.is_a(onto.MediumAccuracyLevel):
        raise ValueError("This method only works with Medium accuracy level.")

    cells = []
    cells_number = 5
    for idx in range(cells_number):
        cell = onto.reactorCell(name = str(idx))

        comp = onto.GasComposition()

        prec_mol = onto.MolarFraction(value = 0. , name = prec_type.name , unit = '~')
        arf = onto.MolarFraction(value = 1., name = 'Ar', unit = '~')
        h2f = onto.MolarFraction(value = 0., name = 'H2', unit = '~')
        n2f = onto.MolarFraction(value = 0., name = 'N2', unit = '~')
        o2f = onto.MolarFraction(value = 0., name = 'O2', unit = '~')

        comp.add(prec_mol, arf, h2f, n2f, o2f, rel = onto.hasPart)

        primaries = onto.NanoParticleSizeDistribution(name = 'Primaries')
        particles = onto.NanoParticleSizeDistribution(name = 'Particles')

        cell.add(primaries,particles, rel=onto.hasPart)

        cell.add(onto.Velocity(value = 0., name = str(idx), unit = 'm/s'))

        # Set thermodynamic conditions
        tcond = onto.ThermoCond()
        pressure = onto.Pressure(value=101325, unit='m^2/s^2', name = 'Pressure')
        temp = onto.Temperature(value = 500, unit = 'K', name = 'Temperature')
        tcond.add(pressure, temp, rel = onto.hasPart)

        cell.add(tcond,comp,rel=onto.hasPart)
        cells.append(cell)
        reactor.add(cell)

    time = onto.Time(value = 0., unit="s", name="Simulation Time")
    dt = onto.Time(value = 1e-8, unit="s", name="Current Timestep")
    reactor.add(time,dt, rel = onto.hasPart)
    source.add(reactor, rel = onto.hasProperty)

    save_time = 0.
    save_step = 5e-5

    with CoupledReactorSession(delete_simulation_files=True) as coupled, \
        NanoDOMESession(delete_simulation_files=True) as nano:

        coupledwrapper = onto.NanoFOAMWrapper(session=coupled)
        coupledwrapper.add(source, accuracy_level)

        nanowrapper = onto.NanoFOAMWrapper(session=nano)
        nanowrapper.add(source, accuracy_level)

        tf = 1.1e-6
        while time.value < tf:

            print("Time: ",time.value)
            print("")

            coupledwrapper.update(source)

            coupled.run()

            source.update(coupledwrapper.get(source.uid).get(reactor.uid))

            save_time += dt.value

            if save_time > save_step:
                print("Post coupled")
                for cl in cells:
                    t_fracs = cl.get(oclass=onto.GasComposition)[0].get(oclass=onto.MolarFraction)
                    for mol in t_fracs:
                        if mol.name is prec_type.name:
                            print(mol.value)
                print("")

            nanowrapper.update(source)

            nano.run()

            source.update(nanowrapper.get(source.uid).get(reactor.uid))

            if save_time > save_step:
                print("Post nano")
                for cl in cells:
                    t_fracs = cl.get(oclass=onto.GasComposition)[0].get(oclass=onto.MolarFraction)
                    for mol in t_fracs:
                        if mol.name is prec_type.name:
                            print(mol.value)
                print("")

                # Get the PSD
                results = nanowrapper.get(source.uid).get(reactor.uid).get(oclass=onto.reactorCell)
                for idx, res in enumerate(results):

                    for dist in res.get(oclass=onto.NanoParticleSizeDistribution):
                        if dist.name == "Particles":
                            part_uid = dist.uid
                        elif dist.name == "Primaries":
                            prim_uid = dist.uid

                    particles = res.get(part_uid)
                    primaries = res.get(prim_uid)

                    if (particles.get(oclass=onto.Bin)) or \
                        (primaries.get(oclass=onto.Bin)) :

                        # Histogram plotting examples for Particles and Primaries
                        # for Medium and High Accuracy Levels
                        plot_distributions([primaries,particles], time.value, "cell_" + str(res.name), savefig = True)

                save_time = 0.

            time.value += dt.value

        print("Final time: ", time.value)
        print("")

else:
    raise SystemExit('No valid mode selected. Available modes are: elenbaas, cfd, nanodome, linked and coupled')
