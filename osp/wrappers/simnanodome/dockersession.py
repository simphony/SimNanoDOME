#SimPhoNy - EU-project funded by the 7th Framework Programme (Project number 604005)
#(https://www.simphony-project.eu/, https://github.com/simphony)

#e-mail: Emanuele Ghedini, emanuele.ghedini@unibo.it; Giorgio La Civita, giorgio.lacivita2@unibo.it

#Copyright (C) 2018  Alma Mater Studiorum - Università di Bologna
#This program is free software: you can redistribute it and/or modify
#it under the terms of the GNU Lesser General Public License as
#published by the Free Software Foundation, either version 3 of the
#License, or (at your option) any later version.

#This program is distributed in the hope that it will be useful,
#but WITHOUT ANY WARRANTY; without even the implied warranty of
#MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#GNU General Public License for more details.

#You should have received a copy of the GNU General Public License
#along with this program.  If not, see <http://www.gnu.org/licenses/>.

import os, subprocess, shutil, time
import numpy as np

from osp.core.session import SimWrapperSession
from osp.core.utils import pretty_print
from osp.core import ONTOLOGY_NAMESPACE_REGISTRY, get_entity
from osp.core import force_cfd_ontology as onto
from pyofi import Controller


def CudsFinder(cuds, target_namespace, foam_concept):
    """
    Return the disred instance with an attribute `foam_concept`
    within the basal `cuds` of oclass `input_data` resulting
    from the `CudsBuilder`.
    This attribute holding instance originates from an oclass with
    `target_namespace` (e.g. "control_dict_data") and represents
    an entity of an OpenFoam-native dict-file (e.g. ControlDict).
    The search is carried out by tracing the `path` through the
    `cuds`. This path was found during the scan through the tree
    of the related ontology

    Parameters
    ----------
    cuds : osp.core.cuds.Cuds
        CUDS-object (instantiated oclass `input_data` from the `CudsBuilder`)
        to be scanned for the subobject holding the desired `foam_concept`
        and `foam_value`
    target_namespace : str
        Namespace of the entity which is representing the kind of
        OpenFoam-native file, in which the `foam_concept` and `foam_value`
        are hosted. (e.g. "mesh_dict_data", "control_dict_data", ...)
    foam_concept : str
        Key or namespace in the dictionary of an OpenFoam file (e.g. "blocks",
        "deltaH", ...)

    Returns
    -------
    osp.core.cuds.Cuds
        instance of a certain oclass holding `foam_concept`as object-own
        attribute found during the scan of the `target_cuds`
    """
    target_entity = _return_entity(cuds, target_namespace)
    for subclass in target_entity.subclasses:
        if foam_concept in subclass.attributes.values():
            path = subclass.superclasses
    for superentity in target_entity.superclasses:
        path.remove(superentity)
    target_cuds = cuds.get(oclass=target_entity)[0]
    return _trace_path(target_cuds, path)


def _trace_path(target_cuds, path):
    """
    Recursively query down the path of subclasses from the
    superior `target_cuds` on, until the list is empty.
    The desired subobject at the end of the path is then
    returned

    Parameters
    ----------
    target_cuds : osp.core.cuds.Cuds
        Instantiated oclass of the superior entity to be queried for the next
        subclass in the `path` list (e.g. kinetics_dict_data,
        control_dict_data,...)
    path : list
        List of ontology classes leading to the ultimate subclass which was
        searched for during the scan in `SimPhonyUtils::_scan_cuds()`

    Returns
    -------
    osp.core.cuds.Cuds
        instance of a certain oclass holding
            `foam_concept`as object-own attribute found during the scan of
            the `target_cuds` `SimPhonyUtils::_scan_cuds()`
    """
    if len(path):
        subcuds = target_cuds.get(oclass=path[-1])[0]
        path.pop(-1)
        return _trace_path(subcuds, path)
    else:
        return target_cuds


def _return_entity(cuds, namespace):
    """
    Function to return another oclass within the
    ontology of the root cuds objects by passing
    an additional string. This might be useful if
    the user may switch between different ontologies
    for different workflows in the future

    Parameters
    ----------
    cuds : osp.core.cuds.Cuds
        Root cuds object of any desired oclass
    namespace : str
        Namespace of the desired entity to be returned by the function

    Returns
    -------
    osp.core.ontology.oclass.OntologyClass
        Ontology class belonging to the passed namespace
    """
    ontoname = cuds.oclass.namespace.name
    return get_entity(".".join((ontoname, namespace)))


class NanoDockerSession(SimWrapperSession):

    def __init__(self, engine=None, **kwargs):
        super().__init__(engine, **kwargs)
        self._case_files=os.path.join(os.path.dirname(__file__),
                                      "cases", "dow_example")
        self._initialized = False

    def __str__(self):
        return "NanoDOME Session for nanoparticle synthesis calculations"

    # OVERRIDE
    def _run(self, root_cuds_object):
        simulation = self._get_current_simulation(root_cuds_object)
        tmax = self._get_ofi_args(
            simulation, "endTime", "ControlDictData"
        )
        dt = self._get_ofi_args(
            simulation, "deltaT", "ControlDictData"
        )
        dx = self._get_ofi_args(
            simulation, "cell_numbers", "MeshDictData"
        )
        print(f"Run PUFoam until tmax={tmax} with dt={dt} and dx={dx}")
        self._ofi.run(
            float(tmax), float(dt), dx[0]
        )
        print("Run completed")
        simulation.is_completed = True
        self._gather_output(simulation)
        if simulation.ofi_segment == "exit":
            self.close()

    def close(self):
        """Invoked, when the session is being closed"""
        # Close the running instance of the OpenFOAM
        if self._initialized:
            self._ofi.exit()
            self._ofi = None
            # Wait for the OpenFOAM to close
            # If the process couldn't terminate, kill it
            if self._ofi_process.wait() is None:
                self._ofi_process.kill()
            self._ofi_process = None
            self._initialized = False      

    # OVERRIDE
    def _load_from_backend(self, uids, expired=None):
        """Loads the cuds object from the simulation engine"""
        for uid in uids:
            if uid in self._registry:
                yield self._registry.get(uid)
            else:
                yield None              
    
    # OVERRIDE
    def _apply_added(self, root_obj, buffer):
        simulation=root_obj.get(oclass=onto["Simulation"])
        for isim in simulation:
            if not isim.is_completed and not self._initialized:
                #TODO: further distinguish between "continue" and "exit"
                self._initialize_engine(isim)
        for cuds_object in buffer.values():
            if cuds_object.is_a(onto["Obstacle"]):
                self._add_obstacle(cuds_object)              

    # OVERRIDE
    def _apply_updated(self, root_obj, buffer):
        for cuds_object in buffer.values():
            if cuds_object.is_a(onto.Obstacle):
                self._update_obstacle(cuds_object)

    # OVERRIDE
    def _apply_deleted(self, root_obj, buffer):
        for cuds_object in buffer:
            if cuds_object.is_a(onto.Obstacle):
                self._remove_obstacle(cuds_object)      

    def _initialize_engine(self, simulation):
        self._process_input_data(simulation)
        for proc in ["blockMesh", "setFields", "PUFoam"]:
            cmd=f"/bin/bash -c  \"source $HOME/.bashrc && {proc}\""
            self._ofi_process=subprocess.Popen(cmd, 
                                               shell=True, 
                                               cwd=self._case_dir)
            time.sleep(1)
        self._ofi = Controller()
        self._initialized = True

    def _process_input_data(self, simulation):
        self._case_dir = os.path.join(os.getcwd(), 
                                      f"simulation-{simulation.uid}")
        shutil.copytree(self._case_files, self._case_dir)
        inputdata=simulation.get(oclass=onto["InputData"])[0]
        for dict_data in inputdata.iter():
            if dict_data.oclass in onto["InputData"].direct_subclasses:
                location, filename = self._get_file_location(dict_data)
                foam_file=dict_data.get(oclass=onto["FoamFileContent"])[0]
                self._write_foam_file(foam_file, location, filename)

    def _write_foam_file(self, foam_file, location, filename):
        file_path = os.path.join(location, filename)
        if not os.path.exists(file_path):
            os.remove(file_path)
        with open(file_path, "w") as dict_file:
            print(foam_file.foam_chunk, file=dict_file)

    def _get_file_location(self, data_dict):
        for subclass in data_dict.iter():
            if "FoamFile" in subclass.get_attributes().values():
                metadata = subclass
        for subclass in metadata.iter():
            subclass_attrs = subclass.get_attributes()
            if "location" in subclass_attrs.values():
                folder=subclass_attrs[onto["FoamValue"]]
            elif "object" in subclass_attrs.values():
                filename=subclass_attrs[onto["FoamValue"]]
        location=os.path.join(self._case_dir, folder)
        return location, filename
        
    def _get_ofi_args(self, simulation, namespace, data_dict):
        inputdata = simulation.get(oclass=onto["InputData"]).pop()
        found_cuds = CudsFinder(inputdata, data_dict, namespace)
        attrs = found_cuds.get_attributes()
        common_key = [
            key for key in attrs.keys() \
                if key in onto["Physical_foam_quantity"].attributes.keys()
        ]
        return attrs[common_key.pop()]

    def _get_current_simulation(self, root_cuds_object):
        simulation=root_cuds_object.get(oclass=onto["Simulation"])
        for element in simulation:
            if not element.is_completed:
                return element

    def _add_obstacle(self, obstacle):
        """Adds an obstacle"""
        width, height, depth = self._extract_dimensions(obstacle)
        position = self._extract_position(obstacle)
        # Add the obstacle
        self._ofi.updateObstacle(
            str(obstacle.uid), width, height, depth, position
        )

    def _update_obstacle(self, obstacle):
        """Updates the properties of an existing obstacle"""
        if not obstacle.get(rel=onto["IsPartOf"]):
            self._remove_obstacle(obstacle)
        # Extract obstacle properties
        width, height, depth = self._extract_dimensions(obstacle)
        position = self._extract_position(obstacle)
        # Update an existing obstacle
        self._ofi.updateObstacle(
            str(obstacle.uid), width, height, depth, position
        )

    def _remove_obstacle(self, obstacle):
        """Removes an existing obstacle"""
        self._ofi.removeObstacle(str(obstacle.uid)) 

    def _extract_dimensions(self, cuds_object):
        """Extracts width, depth and height from a CUDS object;
           default dimension value of 1 is set otherwise"""
        width = depth = height = 1
        # Get objects's dimensions
        if cuds_object.get(oclass=onto.Width):
            width = cuds_object.get(oclass=onto.Width)[0].value
        if cuds_object.get(oclass=onto.Height):
            height = cuds_object.get(oclass=onto.Height)[0].value
        if cuds_object.get(oclass=onto.Depth):
            depth = cuds_object.get(oclass=onto.Depth)[0].value
        return width, height, depth

    def _extract_position(self, cuds_object):
        """Extract a 3D position from a CUDS object;
           default position of (0,0,0) is set otherwise"""
        position = [0, 0, 0]
        # Get object's position
        if cuds_object.get(oclass=onto.Position):
            position[0] = cuds_object.get(oclass=onto.Position)[0].vector[0]
            position[1] = cuds_object.get(oclass=onto.Position)[0].vector[1]
            position[2] = cuds_object.get(oclass=onto.Position)[0].vector[2]
        return position

    def _gather_output(self, simulation):
        FoamDir=onto["FoamDirectory"]
        FoamFileName=onto["FoamFileName"]
        output=onto["OutputData"]()
        for entity in onto["OutputData"].direct_subclasses:
            attrs=entity.attributes
            if FoamFileName in attrs.keys():
                path=os.path.join(
                    self._case_dir,
                    attrs[FoamDir],
                    attrs[FoamFileName]
                )
                with open(path, "r") as outputfile:
                    filecontent=''
                    for line in outputfile:
                        filecontent+=line
                outputfile_instance=entity(
                    foam_chunk=filecontent
                )
                output.add(
                    outputfile_instance, 
                    rel=onto["HasPart"]
                )
        simulation.add(output, rel=onto["HasPart"])
