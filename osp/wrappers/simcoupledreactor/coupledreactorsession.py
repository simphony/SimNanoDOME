"""
@author: Giorgio La Civita, UNIBO DIN
"""

from distutils import dir_util

from osp.core.session import SimWrapperSession
from osp.core.namespaces import nanofoam as onto

from .simple_reactor_engine import simple_reactor_engine

class CoupledReactorSession(SimWrapperSession):
    """
    Session class for CoupledReactor wrapper.
    """

    def __init__(self, engine="coupledreactor", case="",
    delete_simulation_files=True, **kwargs):
        super().__init__(engine, **kwargs)
        # Whether or not to store the generated files by the simulation engine
        self._delete_simulation_files = delete_simulation_files

        # Engine specific initializations
        self._initialized = False
        self._case_dir = None


    def __str__(self):
        return "CoupledReactor session for coupled nanoparticle synthesis"

    def close(self):
        """Invoked, when the session is being closed"""
        if self._delete_simulation_files and self._case_dir:
            dir_util.remove_tree(self._case_dir)
        # Close the running instance of the nanoDOME
        if self._initialized:
            self._initialized = False

    # OVERRIDE
    def _run(self, root_cuds_object):
        """Call the run command of the engine."""
        if self._initialized:

            time = self._get_property(self.reactor, ["Simulation Time"])

            cs = []
            cells = self.reactor.get(oclass=onto.reactorCell)
            self.cells = [0 for x in range(len(cells))]
            for cl in cells:
                self.cells[int(cl.name)] = cl

            for cl in self.cells:
                comp = cl.get(oclass=onto.GasComposition)[0]
                mol = self._get_property(comp,[self.prec_name])
                cs.append(mol)

            # Run the engine for a single timestep
            cs, U, T, p, dt = self.eng.run(time,cs)

            for idx, cl in enumerate(self.cells):
                vel = cl.get(oclass=onto.Velocity)[0]
                vel.value = U[idx]
                Tt = cl.get(oclass=onto.ThermoCond)[0].get(oclass=onto.Temperature)[0]
                Tt.value = T[idx]
                pt = cl.get(oclass=onto.ThermoCond)[0].get(oclass=onto.Pressure)[0]
                pt.value = p[idx]
                gas = cl.get(oclass=onto.GasComposition)[0]
                for mol in gas.get(oclass=onto.MolarFraction):
                    if mol.name == self.prec_name:
                        mol.value = cs[int(cl.name)]

            # re-normalize molar fractions so that their sum equals 1
            for cl in self.cells:
                gas = cl.get(oclass=onto.GasComposition)[0]
                for mol in gas.get(oclass=onto.MolarFraction):
                    if mol.name == self.prec_name:
                        mol.value = cs[int(cl.name)]
                mol_sum = 0.
                for mol in gas.get(oclass=onto.MolarFraction):
                    mol_sum += mol.value
                for mol in gas.get(oclass=onto.MolarFraction):
                    mol.value /= mol_sum

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

        source = root_cuds_object.get(oclass=onto.PlasmaSource)[0]
        self.reactor = source.get(oclass=onto.nanoReactor)[0]

        # Get the simplified domain properties
        L = self.reactor.get(oclass=onto.CylindricalReactorDimensions)[0].get( \
                           oclass=onto.Length)[0].value
        feedrate = source.get(oclass=onto.SolidPrecursor)[0].get( \
                             oclass=onto.FeedRate)[0].value
        self.prec_name = source.get(oclass=onto.SolidPrecursor)[0].get( \
                             oclass=onto.Type)[0].name

        # Get the nanoCells and sort them by ascending name as index
        # Add also the initial precursor vapour molar fraction
        cells = self.reactor.get(oclass=onto.reactorCell)

        self.cells = [0 for x in range(len(cells))]
        for cl in cells:
            self.cells[int(cl.name)] = cl

        # Get the molar fractions of the gas phase of the first cell,
        # compute and update the new gas phase composition
        comp = 0.
        for cp in self.cells[0].get(oclass=onto.GasComposition)[0].get(oclass=onto.MolarFraction):
            comp += cp.value

        # Create and initialize the engine
        self.eng = simple_reactor_engine()

        mol_flux = feedrate/self.eng.get_molar_mass(self.prec_name)/1e-3
        comp = mol_flux + comp
        self.prec_m_frac = mol_flux / comp

        for cp in self.cells[0].get(oclass=onto.GasComposition)[0].get(oclass=onto.MolarFraction):
            if cp.name == self.prec_name:
                cp.value = self.prec_m_frac
            else:
                cp.value /= comp

        self.eng.set_domain(len(cells),L, self.prec_m_frac)

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
