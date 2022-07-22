"""
@author: Giorgio La Civita, UNIBO DIN
"""

import os, subprocess, psutil, zipfile
import numpy as np
from distutils import dir_util

from osp.core.session import SimWrapperSession
from osp.core.namespaces import nanofoam as onto

class CFDSession(SimWrapperSession):
    """
    Session class for cfd wrapper.
    """

    def __init__(self, engine="rhoSimpleFoam", case="nanodome",
    delete_simulation_files=True, **kwargs):
        super().__init__(engine, **kwargs)
        # Whether or not to store the generated files by the simulation engine
        self._delete_simulation_files = delete_simulation_files

        # Engine specific initializations
        self._initialized = False
        self._case_dir = None
        # self._case_files =  os.path.abspath(
        #                     os.path.join(os.getcwd(), 
        #                                  os.pardir,
        #                                  "osp/wrappers/simcfd/cases/nanodome/"))
        # self._foam_core = os.path.abspath(
        #                     os.path.join(os.getcwd(), 
        #                                  os.pardir,
        #                                  "osp/wrappers/simcfd/modules/foam/OpenFOAM-v1906"))
        self._case_files = os.path.join(
            os.path.dirname(__file__),
            "cases", case
            )
        self._foam_core = os.path.join(
            os.path.dirname(__file__), "modules/foam/OpenFOAM-v1906"
            )
        self._load_path = os.path.join(
            self._foam_core,"etc/bashrc"
            )

    def __str__(self):
        return "OpenFoam session for nanoparticle synthesis"

    def close(self):
        """Invoked, when the session is being closed"""
        if self._delete_simulation_files and self._case_dir:
            dir_util.remove_tree(self._case_dir)
        # Close the running instance of the OpenFOAM
        if self._initialized:
            self._initialized = False

    # OVERRIDE
    def _run(self, root_cuds_object):
        """Call the run command of the engine based on simulation type (standalone, linked or coupled)."""

        if self._initialized:

            # Run the CFD simulation
            os.chmod(os.path.join(self._case_dir,"Allrun"), 0o744)
            subprocess.call(os.path.join(self._case_dir,"Allrun"))

            # Collect and manipulate stream files
            stream_paths = self._create_stream_files(self._case_dir,os.path.join(self._case_dir,"streams"))

            # Add the steamlines CUDS objects to the engine's registry
            tcond = self._reactor.get(oclass=onto.ThermoCond)[0]

            for idx,stream in enumerate(stream_paths):
                t_stream = onto.TemperatureStreamline(path=stream, \
                                              name=str(root_cuds_object.uid), \
                                              unit = 'K')
                tcond.add(t_stream,rel=onto.hasProperty)

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

    def _initialize(self, root_cuds_object, added):
        """Initialize solver for a given use case"""

        #Check if Foam has been installed
        foam_install_dir = os.path.join( os.path.dirname(__file__), "modules/foam/")
        foam_install_zip = os.path.join( os.path.dirname(__file__), "modules/foam.zip")
        if not os.path.exists(foam_install_dir):
            with zipfile.ZipFile(foam_install_zip, 'r') as zip_ref:
                zip_ref.extractall(foam_install_dir)

        # Initialize the solver
        self._case_dir = os.path.join(os.getcwd(),
                            "cfd-%s" % root_cuds_object.uid)
        dir_util.copy_tree(self._case_files, self._case_dir)

        # Get the base CUDS
        self._source = root_cuds_object.get(oclass=onto.PlasmaSource)[0]
        self._reactor = self._source.get(oclass=onto.nanoReactor)[0]

        # Get blockmesh parameters from CUDS
        accuracy_level = root_cuds_object.get(oclass=onto.AccuracyLevel)[0]

        diameter, length, inlet_diameter = self._get_property(self._reactor.get( \
                              oclass=onto.CylindricalReactorDimensions)[0], \
                                ["Diameter","Length","Inlet Diameter"])

        # Extract nanoDOME parameters from CUDS
        arf,h2f,n2f,o2f = self._get_property(self._reactor.get(oclass= \
                                 onto.GasComposition)[0],["Ar","H2","N2","O2"])

        # Set thermodynamic conditions
        p = self._get_property(self._reactor.get( \
                                oclass=onto.ThermoCond)[0],["Pressure"])
        self._write_dict({"pchamb ": str(p)}, "p_template", "p", "0")

        # Create the input file for the blockMesh
        self._create_blockmesh(accuracy_level, diameter, length, inlet_diameter)

        # Create controlDict
        params = {}
        self._write_dict(params,
                         "controlDict_template",
                         "controlDict",
                         "system")

        # Create the streamlines set files
        self._create_stream_sets(inlet_diameter)

        # Set serial or parallel execution based on available threads
        available_threads = psutil.cpu_count()

        if available_threads == 1:
            par_switch = 0
            self._create_launcher(self._load_path,par_switch)
        else:
            par_switch = 1
            # Create the input file for decomposePar
            # Parameters for parallel execution
            par_params = dict()
            # Set parameters for parallel execution
            # Parallel execution has been limited to 4 due to mesh size
            if available_threads - 1 > 4:
                par_params["nnp"] = 4
            else:
                par_params["nnp"] = available_threads - 1
            self._write_dict(par_params,
                             "decomposeParDict_template",
                             "decomposeParDict",
                             "system")
            self._create_launcher(self._load_path,par_switch)

        # Get the plasma properties
        plasma = self._source.get(oclass=onto.Plasma)[0]

        # Write the OpenFOAM compliant thermodynamic property files
        for prop in plasma.get(oclass=onto.PlasmaProperty):
            # file_util.copy_file(prop.path, self._case_dir+'/constant/')
            with open(prop.path,'r') as file:
                if 'densRef' in prop.path:
                    pass
                elif 'radial profile' in prop.name or 'radiative' in prop.name:
                    with open(self._case_dir+'/constant/' + str(prop.path.rsplit('/', 1)[-1]), 'a') as out:
                        for line in file.readlines():
                            row = line.split(',')
                            out.write(row[0] + ' ' + row[1])
                    out.close()
                else:
                    f_name = str(prop.path.rsplit('/', 1)[-1])

                    if 'entropy' in prop.name or 'capacity' in prop.name or 'enthalpy' in prop.name:
                        if 'entropy' in prop.name:
                            f_name = 'S'
                        elif 'enthalpy' in prop.name:
                            f_name = 'H'
                        elif 'capacity' in prop.name:
                            f_name = 'Cp'

                    with open(self._case_dir+'/constant/' + f_name, 'a') as out:
                        out.write('(' + '\n')
                        data = []
                        for line in file.readlines():
                            row = line.split(',')
                            data.append([float(row[0]),float(row[1])])
                            out.write('(' + row[0] + ' ' + row[1].strip() + ')' + '\n')
                        out.write(')')

                    if 'entropy' in prop.name or 'capacity' in prop.name or 'enthalpy' in prop.name:
                        der = self._derivate(data)
                        with open(self._case_dir+'/constant/' \
                                  + 'd' + f_name + 'dT' \
                                  , 'a') as out_der:
                            out_der.write('(' + '\n')
                            for item in der:
                                out_der.write('(' + str(item[0]) + ' ' + str(item[1]) + ')' + '\n')
                            out_der.write(')')
                        out_der.close()

                    out.close()
            file.close()

        # Prepare mesh and decomposition if needed
        os.chmod(os.path.join(self._case_dir,"Allprep"), 0o744)
        subprocess.call(os.path.join(self._case_dir,"Allprep"))

        self._initialized = True

    def _derivate(self,prop):
        """Calculates the numerical derivative of a list using the finite difference method"""
        der = []

        for i in range(0,len(prop)):
            if i == 0:
                der.append([prop[i][0], (prop[i+1][1]-prop[i][1])/(prop[i+1][0]-prop[i][0])])
            elif i == len(prop)-1:
                der.append([prop[i][0], (prop[i][1]-prop[i-1][1])/(prop[i][0]-prop[i-1][0])])
            else:
                der.append([prop[i][0], (prop[i+1][1]-prop[i-1][1])/(prop[i+1][0]-prop[i-1][0])])

        return der

    def _create_launcher(self, load_path, par_switch):
        run_params = dict()
        run_params["path"] = load_path
        run_params["par_switch"] = par_switch
        prep_params = run_params.copy()
        # Write the OpenFOAM's environment loader script
        self._write_script(run_params,
                         "Allrun_template", "Allrun","")
        self._write_script(prep_params,
                         "Allprep_template", "Allprep","")

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

    def _create_blockmesh(self, accuracy_level, diameter, length, inlet_diameter):
        # Parameters for the blockMesh generation
        mesh_params = dict()
        # # Set accuracy level
        # # medium by default
        # if accuracy_level.is_a(onto.HighAccuracyLevel):
        #     self._deltax = 0.15
        #     self._deltaz = 0.45
        # elif accuracy_level.is_a(onto.LowAccuracyLevel):
        #     self._deltax = 0.45
        #     self._deltaz = 0.65
        # else:
        #     self._deltax = 0.3
        #     self._deltaz = 0.55
        # Fixed mesh generation parameters
        deltax = 0.175 #0.15
        deltaz = 0.1 #0.1
        R = 0.5*inlet_diameter
        RR = 0.5*diameter
        LL = length
        fr = R
        redz = 1
        angle = np.radians(2.5)
        deltaxx0 = 4*deltax*0.5*pow(10,np.floor(np.log10(R)))
        deltaxx1 = deltax*0.1*pow(10,np.floor(np.log10((RR-R))))
        deltazz = redz*deltaz*0.1*pow(10,np.floor(np.log10(LL)))

        # Set blockMesh parameters
        # Chamber dimensions calculation based on PL-34 system
        mesh_params["fs"] = LL*0.4848
        mesh_params["ss"] = LL*0.4848 + LL*0.3939
        mesh_params["stretchx"] = 3
        mesh_params["stretchz"] = 1
        mesh_params["stretchz1"] = 1/mesh_params.get("stretchz")
        mesh_params["xcells0"] = int(np.ceil(R/deltaxx0))
        mesh_params["xcells1"] = int(np.ceil((RR-R)/deltaxx1))
        mesh_params["zcells"] = int(np.ceil(LL/deltazz))
        mesh_params["r0c"] = R*np.cos(angle)
        mesh_params["r0s"] = R*np.sin(angle)
        mesh_params["r0c_"] = -R*np.cos(angle)
        mesh_params["r0s_"] = -R*np.sin(angle)
        mesh_params["r1c"] = RR*np.cos(angle)
        mesh_params["r1s"] = RR*np.sin(angle)
        mesh_params["r1c_"] = -RR*np.cos(angle)
        mesh_params["r1s_"] = -RR*np.sin(angle)
        mesh_params["r2c"] = fr*np.cos(angle)
        mesh_params["r2s"] = fr*np.sin(angle)
        mesh_params["r2c_"] = -fr*np.cos(angle)
        mesh_params["r2s_"] = -fr*np.sin(angle)

        # Write the blockMesh input dictionary
        self._write_dict(mesh_params,
                         "blockMeshDict_template",
                         "blockMeshDict",
                         "system")

    def _create_stream_files(self,basepath,destpath):
        strct = 1
        stream_paths = []

        if not os.path.exists(destpath):
            os.makedirs(destpath)

        for dirname, dirs, files in os.walk(os.path.join(basepath,"postProcessing")):

            T_found = False
            U_found = False
            for filename in files:
                filepath = os.path.join(dirname, filename)

                if filename == "track0_T.csv":
                    Tdat = self._import_stream_file(filepath)
                    T_found = True
                elif filename == "track0_U.csv":
                    Udat = self._import_stream_file(filepath)
                    U_found = True

            if T_found is True & U_found is True:
                temp_evo = []
                for idx in range(0,len(Udat)):
                    if Udat[idx,0] == 0:
                        temp_evo.append(0.0)
                    else:
                        umag = pow((pow(Udat[idx-1,1],2)+pow(Udat[idx-1,2],2)+pow(Udat[idx-1,3],2)),0.5)
                        temp_evo.append(temp_evo[idx-1] + (Udat[idx,0] - Udat[idx-1,0])/umag)

                streamline = []
                idx = 0
                for step in Udat:
                    streamline.append([temp_evo[idx],Tdat[idx,1]])
                    idx += 1
                # Export the streamline file in CSV format
                outname = destpath + "/streamline_" + str(strct) + ".csv"
                stream_paths.append(outname)
                np.savetxt(outname,np.asarray(streamline), delimiter = ',')
                strct += 1
                T_found = False
                U_found = False

        print("Streamfiles exported.")
        print("")

        return stream_paths

    def _import_stream_file(self,filename):
        "Imports a series of streamlines data from an OpenFOAM CFD simulation."
        "Datas must be in CSV format style following this format: variable1,variable2"
        try:
            fl = open(filename,"r")
        except IOError:
            print("File not found")
        finally:
            datas = []
            for line in fl:
                lnstr = np.array(line.split(","))
                if lnstr[0]=="distance":
                    pass
                elif lnstr[0]=="\n":
                    pass
                else:
                    datas.append(lnstr.astype(np.float))
        return np.asarray(datas)

    def _create_stream_sets(self, inlet_diameter):
        coords = np.linspace(1e-6,0.5*inlet_diameter-1e-6,num=5)
        for ii,xcoo in enumerate(coords, start=1):
            point = str((xcoo, 0, 1e-6)).replace(',', '')
            # Parameters for streamSets file
            stream_params = dict()
            stream_params["stream"] = "stream" + str(ii)
            stream_params["points"] = "(" + point + ")"

            # Write the streamSets input file
            self._write_set(stream_params,
                             "streamSets_template",
                             "streamSets",
                             "system")

    def _write_script(self, params, template_name, file_name, folder):
        """Fill in a templated dictionary file with provided parameters"""
        # Path to the template file
        template_path = os.path.join(
            self._case_dir,
            "templates",
            template_name)
        # Path to the file for the case
        file_path = os.path.join(
            self._case_dir,
            folder,
            file_name)

        with open(template_path, "r") as template:
            with open(file_path, "w") as f:
                for line in template:
                    key = line.split()[0] if line.split() else None
                    if key in params:
                        line = "%s='%s'" % (key, params[key])
                        del params[key]
                    print(line.strip(), file=f)
                for key, value in params.items():
                    print("%s = %s" % (key, value), file=f)

    def _write_dict(self, params, template_name, file_name, folder):
        """Fill in a templated dictionary file with provided parameters"""
        # Path to the template file
        template_path = os.path.join(
            self._case_dir,
            "templates",
            template_name)
        # Path to the file for the case
        file_path = os.path.join(
            self._case_dir,
            folder,
            file_name)

        with open(template_path, "r") as template:
            with open(file_path, "w") as f:
                for line in template:
                    key = line.split()[0] if line.split() else None
                    if key in params:
                        line = "%s %s;" % (key, params[key])
                        del params[key]
                    print(line.strip(), file=f)
                for key, value in params.items():
                    print("%s %s;" % (key, value), file=f)

    def _write_set(self, params, template_name, file_name, folder):
        """Fill in a templated dictionary file with provided parameters"""
        # Path to the template file
        template_path = os.path.join(
            self._case_dir,
            "templates",
            template_name)
        # Path to the file for the case
        file_path = os.path.join(
            self._case_dir,
            folder,
            file_name)

        with open(template_path, "r") as template:
            with open(file_path, "a+") as f:
                for line in template:
                    key = line.split()[0] if line.split() else None
                    if key in params:
                        if key == "stream":
                            line = "%s" % (params[key])
                        else:
                            line = "%s %s;" % (key, params[key])
                        del params[key]
                    print(line.strip(), file=f)
                for key, value in params.items():
                    print("%s %s;" % (key, value), file=f)
