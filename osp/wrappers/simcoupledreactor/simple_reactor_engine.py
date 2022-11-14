"""
@author: Giorgio La Civita, UNIBO DIN
"""

import numpy as np, os

class simple_reactor_engine:

    def set_domain(self,n_cells,L,precursor_inlet_frac):

        self.AMU = 1.660538921e-27

        # data paths
        self.T_path = os.path.join(os.path.dirname(os.path.realpath(__file__)),"data/T.csv")
        self.U_path = os.path.join(os.path.dirname(os.path.realpath(__file__)),"data/U.csv")
        self.p_path = os.path.join(os.path.dirname(os.path.realpath(__file__)),"data/p.csv")

        # Set the parameters for the solver
        self.nodes = n_cells + 2
        self.deltax = L/(n_cells+1)
        self.t_old = 0.
        self.c_old = 0.
        self.cbnd = precursor_inlet_frac

        # Generate the mesh
        self.pos = []
        for i in range(self.nodes):
            self.pos.append(i*self.deltax)

        # Other outputs currently taken from an external reference simulation
        self.U = []
        self.T = []
        self.p = []
        x = self.deltax/2
        for i in range(0,self.nodes - 2):
            self.U.append(self.get_U(x))
            self.T.append(self.get_T(x))
            self.p.append(self.get_p(x))
            x += self.deltax

    def get_T(self,x):
        T = np.genfromtxt(self.T_path, delimiter=',', skip_header=1)
        return np.interp(x,T[:,0],T[:,1])

    def get_U(self,x):
        U = np.genfromtxt(self.U_path, delimiter=',', skip_header=1)
        return np.interp(x,U[:,0],U[:,1])

    def get_p(self,x):
        p = np.genfromtxt(self.p_path, delimiter=',', skip_header=1)
        return np.interp(x,p[:,0],p[:,1])

    def dt(self):
        # Co number is fixed at 0.1
        return (0.1*self.deltax)/np.amax(self.U)

    def get_molar_mass(self,name):

        masses = [ ["Si" , 28.085],
                   ["Ti" , 47.867],
                   ["Al" , 26.981],
                   ["Fe" , 55.845],
                   ["Ag" , 107.8682],
                   ["Cu" , 63.546],
                   ["N2" , 2*14.007],
                   ["O2", 2*15.999],
                   ["Ar" , 39.948],
                   ["H2" , 2.014] ]

        mass = 0.
        for el in masses:
            if el[0] == name:
                mass = el[1]
                break

        return mass

    def run(self,t,cs):

        # construct stiffnes matrix using finite difference method
        A = np.zeros((self.nodes, self.nodes))

        for i in range(self.nodes):
            if i == 0:
                A[i,i] = 1. # BND

            elif i == self.nodes - 1:

                coeff = (t - self.t_old) * self.get_U(i*self.deltax)/(self.deltax)
                A[i,i-1] = - coeff
                A[i,i] = 1. + coeff
                # A[i,i] = 1. # Dirichlet condition

            else:
                coeff = (t - self.t_old) * self.get_U(i*self.deltax)/(2*self.deltax)
                A[i,i-1] = - coeff
                A[i,i] = 1.
                A[i,i+1] = coeff

        # construct right hand side vector
        b = np.zeros(self.nodes)
        for i in range(self.nodes):

            if i == 0:

                b[i] = self.cbnd

            elif i == self.nodes - 1:

                b[i] = cs[-1]
                # b[i] = 0. # Dirichlet condition

            else:

                b[i] = cs[i-1]

        # solve the linear system
        cs = np.linalg.solve(A,b)

        # update the previous iterations values
        self.t_old = t
        self.c_old = cs

        # Generate the output

        # Numerically limit cs at the maximum value
        for i in range(1,len(cs)):

            if (cs[i] > self.cbnd):
                cs[i] = self.cbnd

        return cs[1:-1], self.U, self.T, self.p, self.dt()
