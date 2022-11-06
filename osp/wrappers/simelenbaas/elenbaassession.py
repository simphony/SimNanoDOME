"""
@author: Giorgio La Civita, UNIBO DIN
"""

import os
from distutils import dir_util

from osp.core.session import SimWrapperSession
from osp.core.namespaces import nanofoam as onto

from .elenbaasengine import elen_run

class ElenbaasSession(SimWrapperSession):
    """
    Session class for Elenbaas wrapper.
    """

    def __init__(self, engine="elenbaas", case="",
    delete_simulation_files=True, **kwargs):
        super().__init__(engine, **kwargs)
        # Whether or not to store the generated files by the simulation engine
        self._delete_simulation_files = delete_simulation_files

        # Engine specific initializations
        self._initialized = False
        self._case_dir = None
        self._case_files = os.path.join(os.path.dirname(__file__))

    def __str__(self):
        return "Elenbaas session for plasma source conditions"

    def close(self):
        """Invoked, when the session is being closed"""
        if self._delete_simulation_files and self._case_dir:
            dir_util.remove_tree(self._case_dir)

        if self._initialized:
            self._initialized = False

    # OVERRIDE
    def _run(self, root_cuds_object):
        """Call the run command of the engine."""
        if self._initialized:
            elen_run(self._elen_dict,self._case_files,self._case_dir)
            self._create_CUDS()
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
        if not self._initialized:
            self._initialize(root_obj)

    # OVERRIDE
    def _apply_updated(self, root_obj, buffer):
        """Updates the updated cuds in the engine."""
        pass

    # OVERRIDE
    def _apply_deleted(self, root_obj, buffer):
        """Deletes the deleted cuds from the engine."""
        pass

    def _initialize(self, root_cuds_object, buffer):

        self._case_dir = os.path.join(os.getcwd(),
                                "elenbaas-%s" % root_cuds_object.uid)
        os.mkdir(self._case_dir, mode=0o777)

        # Get the base CUDS
        self._source = root_cuds_object.get(oclass=onto.PlasmaSource)[0]
        self._reactor = self._source.get(oclass=onto.nanoReactor)[0]

        # Set plasma source process conditions
        arf,h2f,n2f,o2f = self._get_property(self._reactor.get(oclass= \
                                 onto.GasComposition)[0],["Ar","H2","N2","O2"])
        input_power = self._get_property(self._source,["Input Power"])
        flowrate = self._get_property(self._source,["Flow Rate"])
        inlet_diameter = self._get_property(self._reactor.get(oclass = \
                    onto.CylindricalReactorDimensions)[0],["Inlet Diameter"])

        self._elen_dict = dict()
        self._elen_dict["Ar"] = arf
        self._elen_dict["H2"] = h2f
        self._elen_dict["N2"] = n2f
        self._elen_dict["O2"] = o2f
        self._elen_dict["Input Power"] = input_power
        self._elen_dict["Flow Rate"] = flowrate
        self._elen_dict["Inlet Radius"] = 0.5*inlet_diameter

        self._initialized = True

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
        """Print solver's output to the standard output"""
        sim_log_path = os.path.join(
            self._case_dir,
            "log")
        with open(sim_log_path, "r") as logs:
            for line in logs:
                print(line)

    def _create_CUDS(self):
        """Save the calculated data in CUDS"""
        plasma = onto.Plasma()
        self._source.add(plasma,rel=onto.hasPart)

        for dirname, dirs, files in os.walk(self._case_dir):
            for filename in files:
                filepath = os.path.join(dirname, filename)
                # Save all profile for boundary conditions and radiation sink
                if 'VR'  in filepath:
                    plasma.add(onto.PlasmaProperty(path = filepath, \
                                                   name = 'Velocity radial profile', \
                                                   unit = 'm/s'))
                elif 'TR'  in filepath:
                    plasma.add(onto.PlasmaProperty(path = filepath, \
                                                   name = 'Temperature radial profile', \
                                                   unit = 'K'))
                elif 'epsR'  in filepath:
                    plasma.add(onto.PlasmaProperty(path = filepath, \
                                                   name = 'Rate of dissipation of turbulent kinetic energy radial profile', \
                                                   unit = 'm2/s3'))
                elif 'kR'  in filepath:
                    plasma.add(onto.PlasmaProperty(path = filepath, \
                                                   name = 'Turbulent kinetic energy radial profile', \
                                                   unit = 'm2/s2'))
                elif 'radiation.rad'  in filepath:
                    # Write radiation source file
                    plasma.add(onto.PlasmaProperty(path = filepath, \
                                                   name = 'Plasma radiative heat transfer', \
                                                   unit = 'W/m3'))
                elif 'rho'  in filepath:
                    # Save all thermophysical properties datas
                    # rho
                    plasma.add(onto.PlasmaProperty(path = filepath, \
                                                   name = 'Density', \
                                                   unit = 'kg/m3'))
                elif 'Cp'  in filepath:
                    # Cp
                    plasma.add(onto.PlasmaProperty(path = filepath, \
                                                   name = 'Specific heat capacity (Cp)', \
                                                   unit = 'J/kg/K'))
                elif 'enthalpy'  in filepath:
                    # H
                    plasma.add(onto.PlasmaProperty(path = filepath, \
                                                   name = 'Specific enthalpy', \
                                                   unit = 'J/kg'))
                elif 'mu'  in filepath:
                    # mu
                    plasma.add(onto.PlasmaProperty(path = filepath, \
                                                   name = 'Dynamic viscosity', \
                                                   unit = 'Pa s'))
                elif 'kappa'  in filepath:
                    # kappa
                    plasma.add(onto.PlasmaProperty(path = filepath, \
                                                   name = 'Thermal conductivity', \
                                                   unit = 'W/m/k'))
                elif 'sigmaE'  in filepath:
                    # sigma
                    plasma.add(onto.PlasmaProperty(path = filepath, \
                                                   name = 'Electrical conductivty', \
                                                   unit = 'S/m'))
                elif 'entropy'  in filepath:
                    # S
                    plasma.add(onto.PlasmaProperty(path = filepath, \
                                                   name = 'Specific entropy', \
                                                   unit = 'J/kg/K'))
                elif 'densRef'  in filepath:
                    # Save reference density value for nanoDOME
                    plasma.add(onto.PlasmaProperty(path = filepath, \
                                                   name = 'Reference density', \
                                                   unit = 'kg/m3'))