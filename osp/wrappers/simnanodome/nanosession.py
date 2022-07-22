"""
@author: Giorgio La Civita, UNIBO DIN
"""

import os
from distutils import dir_util

from osp.core.session import SimWrapperSession
from osp.core.namespaces import nanofoam as onto
from .nano_engine import nano_engine as eng

class NanoDOMESession(SimWrapperSession):
    """
    Session class for nanoDOME wrapper.
    """

    def __init__(self, engine="nanodome", case="nanodome",
    delete_simulation_files=True, **kwargs):
        super().__init__(engine, **kwargs)
        # Whether or not to store the generated files by the simulation engine
        self._delete_simulation_files = delete_simulation_files

        # Engine specific initializations
        self._initialized = False
        self._case_dir = None

    def __str__(self):
        return "nanoDOME session for nanoparticle synthesis"

    def close(self):
        """Invoked, when the session is being closed"""
        if self._delete_simulation_files and self._case_dir:
            try:
                dir_util.remove_tree(self._case_dir)
            except:
                pass
        # Close the running instance of the nanoDOME
        if self._initialized:
            self._initialized = False

    # OVERRIDE
    def _run(self, root_cuds_object):
        """Call the run command of the engine."""
        if self._initialized:
            # Run nanoDOME
            if self._bool_coupled is False:
                self._nano_run(root_cuds_object)
            else:
                self._nano_coupled_run(root_cuds_object)
        else:
            raise ValueError("Session not initialized")

    # OVERRIDE
    def _load_from_backend(self, uids,expired=None):
        """Loads the cuds object from the simulation engine"""
        for uid in uids:
            if uid in self._registry:
                yield self._registry.get(uid)
            else:
                yield None

    # OVERRIDE
    def _apply_added(self, root_obj, buffer):
        """Adds the added cuds to the engine."""
        pass

    # OVERRIDE
    def _apply_updated(self, root_obj, buffer):
        """Updates the updated cuds in the engine."""
        pass

    # OVERRIDE
    def _apply_deleted(self, root_obj, buffer):
        """Deletes the deleted cuds from the engine."""
        pass

    def _initialize(self, root_cuds_object, buffer):

        self.eng = eng()

        self._case_dir = os.path.join(os.getcwd(),
                                "nanodome-%s" % root_cuds_object.uid)

        if not self._delete_simulation_files:
            os.mkdir(self._case_dir, mode=0o777)

        # Get the base CUDS
        self._source = root_cuds_object.get(oclass=onto.PlasmaSource)[0]
        self._reactor = self._source.get(oclass=onto.nanoReactor)[0]

        # Extract nanoDOME parameters from CUDS
        accuracy_level = root_cuds_object.get(oclass=onto.AccuracyLevel)[0]
        if accuracy_level.is_a(onto.LowAccuracyLevel):
            self._acc_level = "Low"
        elif accuracy_level.is_a(onto.MediumAccuracyLevel):
            self._acc_level = "Medium"
        elif accuracy_level.is_a(onto.HighAccuracyLevel):
            self._acc_level = "High"

        self.prec_type = self._source.get(oclass= \
                         onto.SolidPrecursor)[0].get(oclass=onto.Type)[0].name

        self.gas_names = ["Ar","H2","N2","O2"]

        if self._reactor.get(oclass= onto.ThermoCond):
            if self._reactor.get(oclass= onto.ThermoCond)[0].get(oclass=onto.TemperatureStreamline):
                self._bool_stream = True
                self._bool_coupled = False

                self._gas_fractions = self._get_property(self._reactor.get(oclass= \
                                 onto.GasComposition)[0],self.gas_names)

                if (sum(self._gas_fractions) != 1.):
                    raise ValueError ("Sum of gas fractions not 1!")

                self.species = [self.prec_type] + self.gas_names

                self._feedrate = self._get_property(self._source.get(oclass= \
                                 onto.SolidPrecursor)[0],["Feed Rate"])

                # Set process conditions
                self._pressure = self._get_property(self._reactor.get(oclass= \
                                 onto.ThermoCond)[0],["Pressure"])

                self._flowrate = self._get_property(self._source,["Flow Rate"])

                self._stream = self._get_property(self._reactor.get(oclass= \
                                 onto.ThermoCond)[0],[str(root_cuds_object.uid)])

                plasma = self._source.get(oclass=onto.Plasma)[0]
                dens_file = self._get_property(plasma,["Reference density"])
                with open(dens_file,"r") as file:
                    for line in file:
                        self._dens_ref = float(line.split()[1])

            else:
                self._bool_stream = False
                self._bool_coupled = False

                self._gas_fractions = self._get_property(self._reactor.get(oclass= \
                                 onto.GasComposition)[0],self.gas_names)

                if (sum(self._gas_fractions) != 1.):
                    raise ValueError ("Sum of gas fractions not 1!")

                self.species = [self.prec_type] + self.gas_names

                self._feedrate = self._get_property(self._source.get(oclass= \
                                 onto.SolidPrecursor)[0],["Feed Rate"])

                # Set process conditions
                self._pressure = self._get_property(self._reactor.get(oclass= \
                                 onto.ThermoCond)[0],["Pressure"])

                self._flowrate = self._get_property(self._source,["Flow Rate"])

                self._temp_gradient = self._get_property(self._reactor.get(oclass= \
                             onto.ThermoCond)[0],["Temporal Temperature Gradient"])

                self._temp_start = self._get_property(self._reactor.get(oclass= \
                             onto.ThermoCond)[0],["Temperature"])

                self._dens_ref = self._gas_fractions[0]*1.784 + \
                                 self._gas_fractions[1]*0.0899 + \
                                 self._gas_fractions[2]*1.25 + \
                                 self._gas_fractions[3]*1.429;

        else:
            self._bool_stream = False
            self._bool_coupled = True

            self._feedrate = self._get_property(self._source.get(oclass= \
                             onto.SolidPrecursor)[0],["Feed Rate"])

            self._flowrate = self._get_property(self._source,["Flow Rate"])

            pp = []
            TT = []
            cs = []
            self.species = [self.prec_type] + self.gas_names

            w_cells = self._reactor.get(oclass=onto.reactorCell)
            self.cells = [None]*(len(w_cells))
            for cl in w_cells:
                self.cells[int(cl.name)] = cl
            for cell in self.cells:
                tcond = cell.get(oclass=onto.ThermoCond)[0]
                for prop in tcond.get(rel=onto.hasPart):
                    if prop.is_a(onto.Pressure):
                        pp.append(prop.value)
                    elif prop.is_a(onto.Temperature):
                        TT.append(prop.value)

                mols = cell.get(oclass=onto.GasComposition)[0].get(oclass=onto.MolarFraction)

                cs_temp = [None]*(len(self.species))
                for ss in mols:
                    if ss.name == self.prec_type:
                        cs_temp[0] = ss.value
                    elif ss.name in self.gas_names:
                        cs_temp[self.gas_names.index(ss.name)+1] = ss.value
                cs.append(cs_temp)

            self.eng.set_network(self.species, pp, TT, cs)

        self._initialized = True

    def _get_obj(self, obj, names):
        """Extracts target object or objects for given objs names"""
        res = []
        res_names = []
        for i in names:
            for ii in obj.get():
                try:
                    obj_name = ii.name
                    if obj_name == i:
                        res.append(ii)
                        res_names.append(obj_name)
                except:
                    pass

        if len(res) == 0:
            raise ValueError('Nothing found')
        elif len(res) != len(names):
            diff = [x for x in names if x not in res_names]
            print(diff, 'not found. Please specify a valid name in your', \
                             obj.oclass ,'CUDS',end='\n')
            raise ValueError

        else:
            if len(res) == 1:
                return res[0]
            else:
                return res

    def _get_property(self, obj, names):
        """Extracts target property or properties from obj for given objs names"""
        res = []
        res_names = []
        for i in names:
            for ii in obj.get():
                try:
                    obj_name = ii.name
                    if obj_name == i:
                        try:
                            res.append(ii.value)
                        except:
                            try:
                                res.append(ii.path)
                            except:
                                res.append(obj_name)
                        res_names.append(obj_name)
                except:
                    pass

        if len(res) == 0:
            raise ValueError('Nothing found')
        elif len(res) != len(names):
            diff = [x for x in names if x not in res_names]
            print(diff, 'not found. Please specify a valid name in your', \
                             obj.oclass ,'CUDS',end='\n')
            raise ValueError

        else:
            if len(res) == 1:
                return res[0]
            else:
                return res

    def _check_logfile(self):
        """Print solver's output to the standart output"""
        sim_log_path = os.path.join(
            self._case_dir,
            "log")
        with open(sim_log_path, "r") as logs:
            for line in logs:
                print(line)

    def _nano_run(self, root_cuds_object):

        # Pass the results to the Engine
        # for dist in self._reactor.get(oclass=onto.NanoParticleSizeDistribution):
        for dist in self._reactor.get(oclass=onto.NanoParticleSizeDistribution):
            if dist.name == 'Particles':
                self._part_res = dist
            elif dist.name == 'Primaries':
                self._prim_res = dist
            else:
                raise ValueError("Distributions can be named Particles or Primaries. \
                                 Please check the name attribute of your CUDS")

        if self._acc_level == "Low":

            mean_diam, numb_dens, vol_frac = self.eng.nano_run(self)

            mean_prim_size = onto.ParticleDiameter(
                value=mean_diam, unit='nm', name='Mean particles diameter')
            prim_numb_dens = onto.ParticleNumberDensity(
                value=numb_dens, unit='#/m3', name='Mean particles number density')
            prim_vol_perc = onto.ParticleVolumePercentage(
                value=vol_frac, unit='m3/m3', name='Mean particles volume percentage')
            result = onto.Bin()
            result.add(mean_prim_size, prim_numb_dens, prim_vol_perc,
                        rel=onto.hasProperty)
            self._part_res.add(result, rel=onto.hasPart)

        else:

            particles, primaries = self.eng.nano_run(self)

            # Create  and fill bins then add them to the SizeDistribution CUDS
            for parti in range(0, len(particles)):
                result = onto.Bin()

                size_class = onto.ParticleDiameter(value=particles[parti][0],
                                    unit="nm",name="Size class")
                size_dist = onto.ParticleNumberDensity(value=particles[parti][1],
                                    unit="#/m3",name="Size distribution")
                fract_dim = onto.ParticleFractalDimension(value=particles[parti][2],
                                    unit="~",name="Mean fractal dimension")
                result.add(size_dist, size_class, fract_dim, rel=onto.hasProperty)

                self._part_res.add(result, rel=onto.hasPart)

            for prim in range(0, len(primaries)):
                result = onto.Bin()

                size_class = onto.ParticleDiameter(value=primaries[prim][0],
                                    unit="nm",name="Size class")
                size_dist = onto.ParticleNumberDensity(value=primaries[prim][1],
                                    unit="#/m3",name="Size distribution")
                result.add(size_dist, size_class, rel=onto.hasProperty)

                self._prim_res.add(result, rel=onto.hasPart)


    def _nano_coupled_run(self,root_cuds_object):

        pp = []
        TT = []
        vels = []
        cs = []

        self.cells = [None]*(len(self._reactor.get(oclass=onto.reactorCell)))
        for cl in self._reactor.get(oclass=onto.reactorCell):
            self.cells[int(cl.name)] = cl

        for cell in self.cells:
            vels.append(cell.get(oclass=onto.Velocity)[0].value)

            tcond = cell.get(oclass=onto.ThermoCond)[0]
            for prop in tcond.get(rel=onto.hasPart):
                if prop.is_a(onto.Pressure):
                    pp.append(prop.value)
                elif prop.is_a(onto.Temperature):
                    TT.append(prop.value)

            mols = cell.get(oclass=onto.GasComposition)[0].get(oclass=onto.MolarFraction)

            cs_temp = [None]*(len(self.species))
            for ss in mols:
                if ss.name == self.prec_type:
                    cs_temp[0] = ss.value
                elif ss.name in self.gas_names:
                    cs_temp[self.gas_names.index(ss.name)+1] = ss.value
            cs.append(cs_temp)

        tf = self._get_property(self._reactor, ["Simulation Time"])

        # cs = self.eng.run_network(tf,pp,TT,vels,cs)

        # # Timestep update
        # dt_w = self._get_obj(self._reactor, ["Current Timestep"])
        # dt = self.eng.net.get_dt()
        # if dt_w.value > dt and dt != 0.:
        #     dt_w.value = dt

        for idx, cl in enumerate(self.cells):
            gas = cl.get(oclass=onto.GasComposition)[0]
            for mol in gas.get(oclass=onto.MolarFraction):
                for sp in self.species:
                    if mol.name == sp:
                        mol.value = cs[idx][self.species.index(sp)]

        # Update the nano-particles size distributions
        # and print them if required by the user
        for idx, cl in enumerate(self.cells):

            prim_psd, part_psd = self.eng.psd_cell_network(idx)

            if len(part_psd) != 0 or len(prim_psd) != 0:

                prim = self._get_obj(cl,["Primaries"])
                part = self._get_obj(cl,["Particles"])

                for idx2 in range(0, len(prim_psd)):
                    result = onto.Bin()

                    size_class = onto.ParticleDiameter(value=prim_psd[idx2][0],
                                        unit="nm",name="Size class")
                    size_dist = onto.ParticleNumberDensity(value=prim_psd[idx2][1],
                                        unit="#/m3",name="Size distribution")
                    result.add(size_dist, size_class, rel=onto.hasProperty)

                    prim.add(result, rel=onto.hasPart)

                for idx3 in range(0, len(part_psd)):
                    result = onto.Bin()

                    size_class = onto.ParticleDiameter(value=part_psd[idx3][0],
                                        unit="nm",name="Size class")
                    size_dist = onto.ParticleNumberDensity(value=part_psd[idx3][1],
                                        unit="#/m3",name="Size distribution")
                    fract_dim = onto.ParticleFractalDimension(value=part_psd[idx3][2],
                                        unit="~",name="Mean fractal dimension")
                    result.add(size_dist, size_class, fract_dim, rel=onto.hasProperty)

                    part.add(result, rel=onto.hasPart)
