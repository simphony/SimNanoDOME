"""
@author: Giorgio La Civita, UNIBO DIN
"""

import numpy as np, os, time
from osp.wrappers.simnanodome.nanolib import libontodome as nn

class nano_engine:

    def PSD_post(self,psd,voll):

        vol = np.asarray(voll).astype(float)
        psd = np.asarray(psd).astype(float)

        pmin = np.amin(psd)
        pmax = np.amax(psd)

        counters, bins = np.histogram(psd, range=(pmin, pmax), bins=15)
        psd_diams = np.zeros(len(counters))
        psd_numbs = np.zeros(len(counters))

        for kk in range(0,len(counters)):
            psd_diams[kk] = (bins[kk])
            psd_numbs[kk] = (counters[kk]/vol)

        return psd_diams,psd_numbs

    def counter_trigger(self,iter, every_n_iter):

        return ((np.floor(iter/every_n_iter) - iter/every_n_iter) == 0)

    class WallClock:
        def __init__(self):
            self.t1 = time.time()
            self.t2 = time.time()

        def start(self):
            self.t1 = time.time()

        def stop(self):
            self.t2 = time.time()

        def interval(self):
            return self.t2 - self.t1


    class DataReader:
        def __init__(self,filename,delimiter = ','):
            self.filename = filename
            self.delimiter = delimiter

        def getData(self):
            try:
                with open(self.filename,'r') as file:
                    dataList = []
                    for line in file.readlines():
                        if line == '\r' or line == '\n' or len(line) == 0:
                            continue
                        else:
                            vec = []
                            for el in line.split(self.delimiter):
                                vec.append(el)
                            dataList.append(vec)
                    return dataList
            except:
                raise ValueError('File not found.')

    def stream_evo(self,TimeTemp_stream, index):
        readert = self.DataReader(TimeTemp_stream,',')

        data = []
        for dat in readert.getData():
            data.append(float(dat[index]))

        return data

    def Temp_gradient(self,t, time_evo, temp_evo):
        if t <= time_evo[0]:
            der = 0.
        elif t >= time_evo[-1]:
            der = 0.
        else:
            ii = 0
            while ii <= len(time_evo) -1:
                if t <= time_evo[ii]:
                    break
                ii+=1;
            ii-=1;
            val = temp_evo[ii] + (t - time_evo[ii])*(temp_evo[ii+1]-temp_evo[ii])/(time_evo[ii+1]-time_evo[ii]);
            der = (val - temp_evo[ii])/(t - time_evo[ii]);

        return der

    def get_prec_mass(self,spec):
        AMU = 1.660538921e-27 #[kg]

        masses = [ (28.085,"Si"),
                  (55.845,"Fe"),
                  (63.546,"Cu"),
                  (47.867,"Ti"),
                  (26.981,"Al"),
                  (107.8682,"Ag")]

        ret = None
        for ms in masses:
            if ms[1] == spec:
                ret = ms[0]
                break

        if ret is None:
            print ("Precursor", spec, "not found in current database.")
            raise ValueError
        else:
            return ret*AMU

    def get_gas_mass(self,spec):
        AMU = 1.660538921e-27 #[kg]

        masses = [ (39.948,"Ar"),
                  (2.014,"H2"),
                  (2*14.007,"N2"),
                  (2*15.999,"O2")]

        ret = None
        for ms in masses:
            if ms[1] == spec:
                ret = ms[0]
                break

        if ret is None:
            print ("Species", spec, "not found in current database.")
            raise ValueError
        else:
            return ret*AMU

    def get_bulk_liquid(self,spec):

        masses = [ (2570.,"Si"),
                  (6980.,"Fe"),
                  (8020.,"Cu"),
                  (4110.,"Ti"),
                  (2700,"Al"),
                  (9320.,"Ag")]

        ret = None
        for ms in masses:
            if ms[1] == spec:
                ret = ms[0]
                break

        if ret is None:
            print ("Species", spec, "not found in current database.")
            raise ValueError
        else:
            return ret

    def get_bulk_solid(self,spec):

        masses = [ (2329.,"Si"),
                  (7874.,"Fe"),
                  (8960.,"Cu"),
                  (4507.,"Ti"),
                  (2300,"Al"),
                  (10490.,"Ag")]

        ret = None
        for ms in masses:
            if ms[1] == spec:
                ret = ms[0]
                break

        if ret is None:
            print ("Species", spec, "not found in current database.")
            raise ValueError
        else:
            return ret

    def get_melting_point(self,spec):

        masses = [ (1687.,"Si"),
                  (1811.,"Fe"),
                  (1357.77,"Cu"),
                  (1941.,"Ti"),
                  (933.47,"Al"),
                  (1234.96,"Ag")]

        ret = None
        for ms in masses:
            if ms[1] == spec:
                ret = ms[0]
                break

        if ret is None:
            print ("Species", spec, "not found in current database.")
            raise ValueError
        else:
            return ret

    def nano_run(self,dictio):

        vals = []
        units = []

        AMU = 1.660538921e-27 #[kg]
        K_BOL = 1.380650524e-23 #[J/K]

        clock = nano_engine.WallClock()

        gas = nn.GasMixture()

        vals.append(nn.Real(0.))
        units.append(nn.Unit("s"))
        t = nn.Time(vals[-1],units[-1])
        gas.create_relation_to(t)

        vals.append(nn.Real(dictio._pressure))
        units.append(nn.Unit("Pa"))
        p_start = nn.Pressure(vals[-1],units[-1])

        vals.append(nn.Real(0.))
        units.append(nn.Unit("Pa/s"))
        dpdt = nn.PressureTimeDerivative(vals[-1],units[-1])

        gas.create_relation_to(p_start)
        gas.create_relation_to(dpdt)

        mols = []
        species = []
        for sp in dictio.species:
            vals.append(nn.Real(0.))
            units.append(nn.Unit("#"))
            mols.append(nn.MolarFraction(vals[-1],units[-1]))
            species.append(nn.SingleComponentComposition(mols[-1],sp))
            species[-1].create_relation_to(mols[-1])
            gas.create_relation_to(species[-1])

        if dictio._bool_stream:
            vals.append(nn.Real(0.))
            units.append(nn.Unit("K/s"))
            dTdt = nn.TemperatureTimeDerivative(vals[-1],units[-1])

            time_evo = self.stream_evo(dictio._stream,0)
            temp_evo = self.stream_evo(dictio._stream,1)

            vals.append(nn.Real(temp_evo[0]))
            units.append(nn.Unit("K"))
            T_start = nn.Temperature(vals[-1],units[-1])

        else:
            vals.append(nn.Real(dictio._temp_gradient))
            units.append(nn.Unit("K/s"))
            dTdt = nn.TemperatureTimeDerivative(vals[-1],units[-1])

            vals.append(nn.Real(dictio._temp_start))
            units.append(nn.Unit("K"))
            T_start = nn.Temperature(vals[-1],units[-1])

        gas.create_relation_to(dTdt)
        gas.create_relation_to(T_start)

        # Precursor material properties
        stpm = nn.SurfaceTensionPolynomialSoftwareModel()
        stmr = nn.SurfaceTensionMaterialRelation()
        vals.append(nn.Real(0.))
        units.append(nn.Unit("N/m"))
        st = nn.SurfaceTension(vals[-1],units[-1])
        stmr.create_relation_to(stpm)
        st.create_relation_to(stmr)
        species[0].create_relation_to(st)
        stmr.run()

        sapm = nn.SaturationPressurePolynomialSoftwareModel()
        samr = nn.SaturationPressureMaterialRelation()
        vals.append(nn.Real(0.))
        units.append(nn.Unit("Pa"))
        sa = nn.SaturationPressure(vals[-1],units[-1])
        samr.create_relation_to(sapm)
        sa.create_relation_to(samr)
        species[0].create_relation_to(sa)
        samr.run()

        masses = []
        # Prec properties
        vals.append(nn.Real(self.get_prec_mass(dictio.species[0])))
        units.append(nn.Unit("kg"))
        masses.append(nn.Mass(vals[-1],units[-1]))
        species[0].create_relation_to(masses[-1])

        vals.append(nn.Real(self.get_bulk_liquid(dictio.species[0])))
        units.append(nn.Unit("kg/m3"))
        sibl = nn.BulkDensityLiquid(vals[-1],units[-1])
        species[0].create_relation_to(sibl)

        vals.append(nn.Real(self.get_bulk_solid(dictio.species[0])))
        units.append(nn.Unit("kg/m3"))
        sibs = nn.BulkDensitySolid(vals[-1],units[-1])
        species[0].create_relation_to(sibs)

        vals.append(nn.Real(self.get_melting_point(dictio.species[0])))
        units.append(nn.Unit("K"))
        melp = nn.MeltingPoint(vals[-1],units[-1])
        species[0].create_relation_to(melp)

        MM = 0.
        for idx,gas_m in enumerate(dictio._gas_fractions,start = 1):
            MM += gas_m*self.get_gas_mass(dictio.species[idx])
            vals.append(nn.Real(self.get_gas_mass(dictio.species[idx])))
            units.append(nn.Unit("kg"))
            masses.append(nn.Mass(vals[-1],units[-1]))
            species[idx].create_relation_to(masses[-1])

        prec_mass = self.get_prec_mass(dictio.species[0])

        nm_prec = dictio._feedrate/(prec_mass/AMU)
        nm_gas = 0.

        nm_gases = []
        for idx,gf in enumerate(dictio._gas_fractions,start=1):
            val = (gf*self.get_gas_mass(dictio.species[idx])/AMU/(MM/AMU))*dictio._flowrate*dictio._dens_ref/60000.
            nm_gases.append(val)
            nm_gas += val;

        ntot = nm_prec + nm_gas

        mols_n = np.true_divide([nm_prec] + nm_gases, ntot)
        for idx,sp in enumerate(species):
            sp.get_related_objects(mols[0])[0].value = mols_n[idx]

        gp = nn.GasModel()
        gp.create_relation_to(gas)

        cnt = nn.ClassicalNucleationTheory()
        cnt.create_relation_to(species[0])

        # Overall end time
        iter = 0
        tf = 7e-4

        # NanoDOME settings based on accuracy level
        if dictio._acc_level == "Low":
            if dictio._bool_stream:
                t_end = tf #time_evo[-1]
            else:
                t_end = tf

            dt = 1e-9
            SAVE_EVERY = 1000

            if dictio._delete_simulation_files is False:
                lognormal_path = os.path.join(dictio._case_dir, "MOMENTS_Lognormal_plot.dat")
                plot_data = os.path.join(dictio._case_dir, "MOMENTS_plot.dat")
                with open(plot_data,"w") as plot:
                    print("Time[sec]" , '\t'
                        , "Temp[K]" , '\t'
                        , "Nucl_Rate" , '\t'
                        , "Species_#_density" , '\t'
                        , "Stable_cluster_size[m]" , '\t'
                        , "AVG_diameter[m]" , '\t'
                        , "Agg_density[#/m3]" , '\t'
                        ,file=plot)
                plot.close()

            part = nn.MomentModelPratsinis()
            part.create_relation_to(species[0])
            T_stop = 300.

        elif dictio._acc_level == "Medium":
            if dictio._bool_stream:
                t_end = tf #time_evo[-1]
            else:
                t_end = tf

            Df = 1.6 #based on NanoDOME D3.4
            vol = np.power(1e-4, 3)

            part = nn.PBMFractalParticlePhase(Df,vol)
            part.create_relation_to(species[0])

            SAVE_EVERY = 1500
            PSD_DATA = 2.5e-5
            save_step = 0.

            if dictio._delete_simulation_files is False:
                plot_data = os.path.join(dictio._case_dir, "PBM_plot.dat")
                with open(plot_data,"w") as plot:
                    print("Time[sec]" , '\t'
                        , "Temp[K]" , '\t'
                        , "Nucl_Rate" , '\t'
                        , "Species_#_density" , '\t'
                        , "Stable_cluster_diameter[m]" , '\t'
                        , "AVG_Part_Num[#]: " , '\t'
                        , "Sint_level[%]" , '\t'
                        , "AVG_diameter[m]" , '\t'
                        , "Agg._#[#]" , '\t'
                        , "Agg_density[#/m3]" , '\t'
                        , "Volume[m]" , '\t'
                        , "AVG_fract_dim" , '\t'
                        , "Part._mean_dim" , '\t'
                        , "ts_exec_time" ,file=plot)
                plot.close()

                part_sizes_file = os.path.join(dictio._case_dir, "PBM_particles_sizes.dat")
                agg_sizes_file = os.path.join(dictio._case_dir, "PBM_aggregates_sizes.dat")

            clock.start()
            T_stop = 520.

        elif dictio._acc_level == "High":
            if dictio._bool_stream:
                t_end = tf #time_evo[-1]
            else:
                t_end = tf

            T_melt = self.get_melting_point(dictio.species[0])
            bliq = self.get_bulk_liquid(dictio.species[0])
            bsol = self.get_bulk_solid(dictio.species[0])

            dt = 1e-10
            SAVE_EVERY = 5000
            SAVE_SNAPSHOT = 1e-5
            snap_count = 0.
            PSD_DATA = 2.5e-5
            save_step = 0.

            V_start = 9e-18

            part = nn.ConstrainedLangevinParticlePhase(V_start)
            part.create_relation_to(species[0])

            if not dictio._delete_simulation_files:
                plot_data = os.path.join(dictio._case_dir, "CGMD_plot.dat")
                with open(plot_data,"w") as plot:
                    print("Time[sec]" , '\t'
                        , "Temp[K]" , '\t'
                        , "Nucl_Rate" , '\t'
                        , "Species_#_density" , '\t'
                        , "Stable_cluster_size[m]" , '\t'
                        , "AVG_Part_Num[#]: " , '\t'
                        , "Sint_level[%]" , '\t'
                        , "AVG_diameter[m]" , '\t'
                        , "Agg._#[#]" , '\t'
                        , "Agg_density[#/m3]" , '\t'
                        , "Volume[m]" , '\t'
                        , "AVG_fract_dim" , '\t'
                        , "Part._mean_dim" , '\t'
                        , "ts_exec_time" ,file=plot)
                plot.close()

                part_sizes_file = os.path.join(dictio._case_dir, "CGMD_particles_sizes.dat")
                agg_sizes_file = os.path.join(dictio._case_dir, "CGMD_aggregates_sizes.dat")

                vtk_path = os.path.join(dictio._case_dir, "CGMD_vtk/")
                os.mkdir(vtk_path, mode=0o777)

            T_stop = 520.


        while (t.value <= t_end):

            if dictio._bool_stream:
                dTdt.value = self.Temp_gradient(t.value,time_evo,temp_evo)
            if T_start.value <= T_stop:
                dTdt.value = 0.

            if dictio._acc_level == "Low":
                g_prec = part.timestep(dt)
                gp.timestep(dt, [g_prec,0.,0.,0.,0.])

                if (self.counter_trigger(iter,SAVE_EVERY)):

                    if dictio._delete_simulation_files is False:
                        # save lognormal values
                        part.print_lognormal_val(lognormal_path)

                        # save simulation data
                        with open(plot_data,"a") as plot:
                            print(
                                t.value , '\t'
                                , T_start.value , '\t'
                                , cnt.nucleation_rate() , '\t'
                                , gp.get_n() , '\t'
                                , cnt.stable_cluster_diameter() , '\t'
                                , 10*part.get_mean_diameter() , '\t'
                                , part.get_n_density() , '\t'
                                , file=plot)

                        plot.close()

            elif dictio._acc_level == "Medium":

                dt = part.calc_dt()

                gp.timestep(dt/2.,[0.,0.,0.,0.,0.])
                part.volume_expansion(dt/2.)

                g_prec = part.timestep(dt)
                gp.timestep(dt,[-g_prec,0.,0.,0.,0.])

                gp.timestep(dt/2.,[0.,0.,0.,0.,0.])
                part.volume_expansion(dt/2.)

                save_step += dt

            elif dictio._acc_level == "High":

                d_min = part.get_particles_smallest_diameter()

                prec_bulk = (bsol if (T_start.value < T_melt) else bliq)

                dt_max_lang = d_min * prec_bulk / gp.get_gas_flux()

                dt_max_coll = np.sqrt(np.pi*prec_bulk*np.power(d_min,5) / (24*3*K_BOL*T_start.value))

                if (part.get_aggregates_number() >= 1):
                    dt = np.amin([dt_max_coll,dt_max_lang])
                    if (dt >1e-10):
                        dt = 1e-10

                g_prec = part.timestep(dt)

                gp.timestep(dt, [-g_prec,0.,0.,0.,0.])

                snap_count += dt
                save_step += dt

            # Save agglomerates and particles datas for PSD
            # Only for Medium and High accuracy levels
            if dictio._delete_simulation_files is False:
                if dictio._acc_level == "Medium" or dictio._acc_level == "High":
                    if self.counter_trigger(iter, SAVE_EVERY):
                        clock.stop()

                        # save simulation data
                        with open(plot_data,"a") as plot:
                            print( t.value , '\t'
                                , T_start.value , '\t'
                                , cnt.nucleation_rate() , '\t'
                                , gp.get_n() , '\t'
                                , cnt.stable_cluster_diameter() , '\t'
                                , part.get_mean_particles_number() , '\t'
                                , part.get_mean_sintering_level() , '\t'
                                , 10*part.get_aggregates_mean_spherical_diameter() , '\t'
                                , part.get_aggregates_number() , '\t'
                                , part.get_aggregates_density() , '\t'
                                , part.get_volume() , '\t'
                                , part.get_mean_fractal_dimension() , '\t'
                                , part.get_particles_mean_diameter() , '\t'
                                , clock.interval() / float(SAVE_EVERY) , file=plot)

                        plot.close()
                        clock.start()

                    # Save particles and aggregates sizes for PSD
                    if (save_step>=PSD_DATA):
                        clock.stop()

                        particles_sizes = part.get_particles_sizes();
                        aggregates_sizes = part.get_aggregates_sizes();

                        # print particles sizes
                        with open(part_sizes_file,"w") as psd:
                            print(10*particles_sizes,file=psd)
                        psd.close();

                        # print aggregates sizes
                        with open(agg_sizes_file,"w") as asd:
                            print(10*aggregates_sizes,file=asd)
                        asd.close()

                        save_step = 0.
                        clock.start()

                    # Save VTK only for High accuracy level
                    if dictio._acc_level == "High":
                        if snap_count >= SAVE_SNAPSHOT and \
                                        part.get_aggregates_number() > 0:

                            part.save_vtk(iter, vtk_path)
                            snap_count = 0.

            iter += 1
            t.value+=dt

        # Save last computed agglomerates and particles datas for PSD
        # Only for Medium and High accuracy levels
        if dictio._delete_simulation_files is False:
            if dictio._acc_level == "Medium" or dictio._acc_level == "High":
                particles_sizes = part.get_particles_sizes();
                aggregates_sizes = part.get_aggregates_sizes();

                # print particles sizes
                with open(part_sizes_file,"w") as psd:
                    print(particles_sizes,file=psd)
                psd.close();

                # print aggregates sizes
                with open(agg_sizes_file,"w") as asd:
                    print(aggregates_sizes,file=asd)
                asd.close()


        if dictio._acc_level == "Low":
            mean_diam = 10*part.get_mean_diameter()
            numb_dens = part.get_n_density()
            vol_frac = np.pi*np.power(mean_diam, 3)*numb_dens/6.

            return mean_diam*1e+9, numb_dens, vol_frac*100

        else:

            part_size_class, part_size_dist = self.PSD_post( \
                                 part.get_aggregates_sizes(),part.get_volume())

            prim_size_class, prim_size_dist = self.PSD_post( \
                                 part.get_particles_sizes(),part.get_volume())

            particles = []
            primaries = []

            # Create  and fill bins then add them to the SizeDistribution CUDS
            for parti in range(0, len(part_size_dist)):

                particles.append([part_size_class[parti]*1e+9*10, part_size_dist[parti], \
                                  part.get_mean_fractal_dimension()])

            for prim in range(0, len(prim_size_dist)):

                primaries.append([prim_size_class[prim]*1e+9*10, prim_size_dist[prim]])

            return particles, primaries


    def set_network(self,specs,pp,TT,cs, mass, bulk_l):

        cells = []
        for idx, csi in enumerate(cs):
            cells.append(nn.nanoCell(specs, pp[idx], TT[idx], csi, mass, bulk_l))
        net = nn.nanoNetwork(cells)

        self.net = net
        self.net_set = True

    def run_network(self,tf,pp,TT,vels,cs,specs):

        if not self.net_set == True:
            self.set_network(specs, pp, TT, cs,self.get_prec_mass(specs[0]), self.get_bulk_liquid(specs[0]))

        while self.net.get_t() < tf:
            cs = self.net.timestep(pp, TT, vels, cs)

        return cs

    def psd_cell_network(self,idx):

        particles = []
        primaries = []

        if len(self.net.get_cell_aggregates_diameters(idx)) != 0 or \
           len(self.net.get_cell_particles_diameters(idx)) != 0:

            part_size_class, part_size_dist = self.PSD_post( \
                        self.net.get_cell_aggregates_diameters(idx), \
                        self.net.get_cell_pbm_volume(idx))

            prim_size_class, prim_size_dist = self.PSD_post( \
                        self.net.get_cell_particles_diameters(idx), \
                        self.net.get_cell_pbm_volume(idx))

            for parti in range(0, len(part_size_class)):

                particles.append([part_size_class[parti]*1e+9, part_size_dist[parti], \
                                  self.net.get_cell_mean_fractal_dimension(idx)])

            for primi in range(0, len(prim_size_class)):

                primaries.append([prim_size_class[primi]*1e+9, prim_size_dist[primi]])

        return primaries, particles