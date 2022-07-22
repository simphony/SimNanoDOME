#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Wed Nov 17 14:27:04 2021

@author: sim
"""

import matplotlib.pyplot as plt

import simple_reactor_engine as engine

eng = engine.simple_reactor_engine()

nn = 50

eng.set_domain(nn,1.,0.025)

cs = [0.] * nn

t = 0.
dt = 0.1*eng.deltax/eng.get_U(0.)

while (t < 1e-2):

    cs,U,T,p,dt = eng.run(t,cs)

    t += dt


plt.plot(eng.pos[1:-1],cs)
plt.xlabel('Distance (m)')
plt.ylabel('Molar fraction (#)')
plt.show()

print(cs)
