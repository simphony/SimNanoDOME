#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Wed Jun 22 13:26:02 2022

@author: sim
"""

import libontodome as nn
import numpy as np

def get_prec_mass(spec):
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

def get_gas_mass(spec):
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

def get_bulk_liquid(spec):

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

def get_bulk_solid(spec):

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

def get_melting_point(spec):

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


sss = ["Si","Ar","H2","N2","O2"]

vals = []
units = []

AMU = 1.660538921e-27 #[kg]
K_BOL = 1.380650524e-23 #[J/K]

gas = nn.GasMixture()

vals.append(nn.Real(0.))
units.append(nn.Unit("s"))
t = nn.Time(vals[-1],units[-1])
gas.create_relation_to(t)

vals.append(nn.Real(1e-10))
units.append(nn.Unit("s"))
dt = nn.Time(vals[-1],units[-1])

vals.append(nn.Real(101325.))
units.append(nn.Unit("Pa"))
p_start = nn.Pressure(vals[-1],units[-1])

vals.append(nn.Real(0.))
units.append(nn.Unit("Pa/s"))
dpdt = nn.PressureTimeDerivative(vals[-1],units[-1])

gas.create_relation_to(p_start)
gas.create_relation_to(dpdt)

mols = []
species = []
for sp in sss:
    vals.append(nn.Real(0.))
    units.append(nn.Unit("#"))
    mols.append(nn.MolarFraction(vals[-1],units[-1]))
    species.append(nn.SingleComponentComposition(mols[-1],sp))
    species[-1].create_relation_to(mols[-1])
    gas.create_relation_to(species[-1])

vals.append(nn.Real(-1e7))
units.append(nn.Unit("K/s"))
dTdt = nn.TemperatureTimeDerivative(vals[-1],units[-1])

vals.append(nn.Real(3000))
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
species[0].get_related_objects(st)[0].get_related_objects(stmr)[0].run()

sapm = nn.SaturationPressurePolynomialSoftwareModel()
samr = nn.SaturationPressureMaterialRelation()
vals.append(nn.Real(0.))
units.append(nn.Unit("Pa"))
sa = nn.SaturationPressure(vals[-1],units[-1])
samr.create_relation_to(sapm)
sa.create_relation_to(samr)
species[0].create_relation_to(sa)
species[0].get_related_objects(sa)[0].get_related_objects(samr)[0].run()

masses = []
# Prec properties
vals.append(nn.Real(28.085*AMU))
units.append(nn.Unit("kg"))
masses.append(nn.Mass(vals[-1],units[-1]))
species[0].create_relation_to(masses[-1])

vals.append(nn.Real(2570.))
units.append(nn.Unit("kg/m3"))
sibl = nn.BulkDensityLiquid(vals[-1],units[-1])
species[0].create_relation_to(sibl)

vals.append(nn.Real(2329.))
units.append(nn.Unit("kg/m3"))
sibs = nn.BulkDensitySolid(vals[-1],units[-1])
species[0].create_relation_to(sibs)

vals.append(nn.Real(1687.))
units.append(nn.Unit("K"))
melp = nn.MeltingPoint(vals[-1],units[-1])
species[0].create_relation_to(melp)

MM = 0.
ggg = [1.0,0.0,0.0,0.0]
for idx,gas_m in enumerate(ggg,start = 1):
    MM += gas_m*get_gas_mass(sss[idx])
    masses.append(nn.Mass(nn.Real(get_gas_mass(sss[idx])), nn.Unit("kg")))
    species[idx].create_relation_to(masses[-1])

nm_prec = 400/1000/3600/(get_prec_mass(sss[0])/AMU)
nm_gas = 0.

nm_gases = []
for idx,gf in enumerate(ggg,start=1):
    val = (gf*get_gas_mass(sss[idx])/AMU/(MM/AMU))*40.*1./60000.
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

iter = 0

# Overall end time
tf = 7e-4

t_end = tf #1.8; #tf;

SAVE_EVERY = 1000

part = nn.ConstrainedLangevinParticlePhase(9e-18)
part.create_relation_to(species[0])

T_stop = 520.
T_melt = get_melting_point("Si")
bliq = get_bulk_liquid("Si")
bsol = get_bulk_solid("Si")

while (t.value <= t_end):

    d_min = part.get_particles_smallest_diameter()

    prec_bulk = (bsol if (T_start.value < T_melt) else bliq)

    dt_max_lang = d_min * prec_bulk / gp.get_gas_flux()

    dt_max_coll = np.sqrt(np.pi*prec_bulk*np.power(d_min,5) / (24*3*K_BOL*T_start.value))

    if (part.get_aggregates_number() >= 1):
        dt.value = np.amin([dt_max_coll,dt_max_lang])
        if (dt.value >1e-10):
            dt.value = 1e-10

    g_prec = part.timestep(dt.value)

    gp.timestep(dt.value, [-g_prec,0.,0.,0.,0.])

    print("t = ",t.value)
    print("d_mean = ", part.get_aggregates_mean_spherical_diameter())

    iter += 1
    t.value += dt.value
