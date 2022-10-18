"""
@author: Giorgio La Civita, UNIBO DIN
"""

import os
import numpy as np

from scipy import integrate as integrate
from scipy import io as io

def _density(T,data):
    "Interpolates density datas on T"
    res = []
    if np.isscalar(T):
        res.append(np.interp(T,data[:,1],data[:,2]))
    else:
        for tt in T:
            if tt > 30000:
                Tt = 30000
            elif tt < 300:
                Tt = 300
            else:
                Tt = tt
            res.append(np.interp(Tt,data[:,1],data[:,2]))
    return np.asarray(res)

def _elec_cond(T,data):
    "Interpolates elec cond datas on T"
    res = []
    if np.isscalar(T):
        res.append(np.interp(T,data[:,1],data[:,4]))
    else:
        for tt in T:
            if tt > 30000:
                Tt = 30000
            elif tt < 300:
                Tt = 300
            else:
                Tt = tt
            res.append(np.interp(Tt,data[:,1],data[:,4]))
    return np.asarray(res)

def _thermal_cond(T,data):
    "Interpolates thermal cond datas on T"
    res = []
    if np.isscalar(T):
        res.append(np.interp(T,data[:,1],data[:,3]))
    else:
        for tt in T:
            if tt > 30000:
                Tt = 30000
            elif tt < 300:
                Tt = 300
            else:
                Tt = tt
            res.append(np.interp(Tt,data[:,1],data[:,3]))
    return np.asarray(res)

def _viscosity(T,data):
    "Interpolates viscosity datas on T"
    res = []
    if np.isscalar(T):
        res.append(np.interp(T,data[:,1],data[:,2]))
    else:
        for tt in T:
            if tt > 30000:
                Tt = 30000
            elif tt < 300:
                Tt = 300
            else:
                Tt = tt
            res.append(np.interp(Tt,data[:,1],data[:,2]))
    return np.asarray(res)

def _rad_h2(T):
    "Interpolates H2 radiation losses datas on T"
    t = np.append(np.arange(5000,30000,1000),30000)
    nec = 1e+6*np.array([8.000E-05, \
        1.000E-03,2.840E-02,3.900E-01,3.030E+00,1.310E+01,5.340E+01, \
        1.360E+02,3.430E+02,5.450E+02,8.640E+02,1.000E+03,1.110E+03, \
        1.160e+03,1.160e+03,1.020e+03,8.450e+02,7.780e+02,6.720e+02, \
        6.380e+02,6.110e+02,5.860e+02,5.010e+02,4.760e+02,4.450e+02,4.160e+02]) #(W/m3)
    res = []
    if np.isscalar(T):
        res.append(np.interp(T,t,nec))
    else:
        for tt in T:
            if tt > 30000:
                Tt = 30000
            elif tt < 5000:
                Tt = 5000
            else:
                Tt = tt
            res.append(np.interp(Tt,t,nec))
    return np.asarray(res)

def _rad_n2(T):
    "Interpolates N2 radiation losses datas on T"
    t = np.append(np.arange(5000,30000,1000),30000)
    nec = 1e+6*np.array([3.692E-06, \
         4.647E-04,2.443E-02,4.154E-01,3.111E+00,7.440E+01,5.727E+02, \
         9.949e+02,1.922e+03,3.021e+03,4.156e+03,5.151e+03,6.024e+03, \
         6.554e+03,6.924e+03,7.509e+03,8.488e+03,9.712e+03,1.086e+04, \
         1.213e+04,1.364e+04,1.507e+04,1.607e+04,1.725e+04,1.883e+04, \
         2.008e+04]) #(W/m3)
    res = []
    if np.isscalar(T):
        res.append(np.interp(T,t,nec))
    else:
        for tt in T:
            if tt > 30000:
                Tt = 30000
            elif tt < 5000:
                Tt = 5000
            else:
                Tt = tt
            res.append(np.interp(Tt,t,nec))
    return np.asarray(res)

def _rad_o2(T):
    "Interpolates O2 radiation losses datas on T"
    t = np.append(np.arange(5000,30000,1000),30000)
    nec = 1e+6*np.array([1.670e-04, \
        1.000E-02,2.490E-01,2.260e+00,1.520e+01,6.270e+01,1.940e+02, \
        4.120e+02,7.740e+02,1.410e+03,1.940e+03,2.350e+03,2.430e+03, \
        2.150e+03,2.120e+03,2.120e+03,2.150e+03,2.430e+03,2.980e+03, \
        4.120e+03,4.640e+03,6.200e+03,8.360e+03,1.190e+04,1.790e+04, \
        2.510e+04]) #(W/m3)
    res = []
    if np.isscalar(T):
        res.append(np.interp(T,t,nec))
    else:
        for tt in T:
            if tt > 30000:
                Tt = 30000
            elif tt < 5000:
                Tt = 5000
            else:
                Tt = tt
            res.append(np.interp(Tt,t,nec))
    return np.asarray(res)

def _rad_ar(T):
    "Interpolates Ar radiation losses datas on T"
    t = np.append(np.arange(5000,30000,1000),30000)
    nec = 4*np.pi*1e+6*np.array([1.494e-06, \
        1.539e-04,4.425e-03,6.063e-02,8.133e-01,1.038e+01,5.469e+01, \
        1.705e+02,3.877e+02,6.979e+02,9.637e+02,1.076e+03,1.098e+03, \
        1.074e+03,1.038e+03,1.046e+03,1.116e+03,1.279e+03,1.594e+03, \
        2.125e+03,2.938e+03,4.134e+03,5.750e+03,7.822e+03,1.050e+04,1.394e+04]) #(W/m3)
    res = []
    if np.isscalar(T):
        res.append(np.interp(T,t,nec))
    else:
        for tt in T:
            if tt > 30000:
                Tt = 30000
            elif tt < 5000:
                Tt = 5000
            else:
                Tt = tt
            res.append(np.interp(Tt,t,nec))
    return np.asarray(res)

def elen_run(elen_dict,prop_dir,out_dir):
        print("Running Elenbaas...")
        # Import simulation settings

        ar = elen_dict.get("Ar")
        h2 = elen_dict.get("H2")
        n2 = elen_dict.get("N2")
        o2 = elen_dict.get("O2")
        vfr0 = elen_dict.get("Flow Rate")
        Pow = elen_dict.get("Input Power") * 0.35 #reduced by 30% for ICP torches
        R = elen_dict.get("Inlet Radius")
        Twall = 500.
        PL = 6.5714*R

        # Load carriers properties
        properties_dict = io.loadmat(os.path.join(prop_dir,"properties.mat"))
        properties = list(properties_dict.items())
        a100thd = np.asarray(properties[3][1])
        a100tra = np.asarray(properties[4][1])
        h100thd = np.asarray(properties[5][1])
        h100tra = np.asarray(properties[6][1])
        n100thd = np.asarray(properties[7][1])
        n100tra = np.asarray(properties[8][1])
        o100thd = np.asarray(properties[9][1])
        o100tra = np.asarray(properties[10][1])

        # Calculate selected mixture properties
        data_tra = a100tra
        data_tra[:,2:] = ar*a100tra[:,2:] + h2*h100tra[:,2:] + \
                           n2*n100tra[:,2:] + o2*o100tra[:,2:]
        data_thd = a100thd
        data_thd[:,2:] = ar*a100thd[:,2:] + h2*h100thd[:,2:] + \
                           n2*n100thd[:,2:] + o2*o100thd[:,2:]

        ## SOLVER ##
        N = 201 # node numbers
        E = np.float64(800.) # [V/m] initial value of axial electric field
        dpdz = np.float64(500.) # [Pa/m] initial value of pressure gradient
        r = np.linspace(0,R,N) # radial discretization
        dr = R/(N-1)

        # initial values
        T0 = np.float64(18000.) # [K]
        V0 = np.float64(0.) # [m/s]
        Tref = np.float64(300.) # [K]
        T = T0*np.ones([N])
        V = V0*np.ones([N])
        tol = np.float64(1e-6)

        # Temperature equation solution
        I0 = Pow/40.0
        Perr = np.float64(1.0)
        while abs(Perr) >= 1e-4:
            err = np.float64(1)
            i = 0
            while (err >= tol) and (i < 500):
                # save previous iter field
                Told = T

                # coefficients calculation
                a = 0.25*(r[0:-1] + r[1:])*(np.asarray(_thermal_cond(T[0:-1],data_tra)) \
                                        + np.asarray(_thermal_cond(T[1:],data_tra)))/dr

                A = np.diag(a,k=1) + np.diag(a,k=-1) - np.diag( np.append( \
                                                np.insert(a[0:-1]+a[1:],0,a[0]),a[-1]))

                S = -dr*r*(_elec_cond(T,data_tra) * pow(E,2) - h2*_rad_h2(T) \
                           - ar*_rad_ar(T) - n2*_rad_n2(T) - o2*_rad_o2(T))
                S[0] /= 2

                # wall boundary conditions
                A[-1,-1] = 1
                A[-1,-2] = 0
                S[-1] = Twall

                # sistem solution with underrelaxation
                T = 0.025*np.linalg.solve(A,S) + 0.975*T

                # current evaluation
                I = np.sum(2*np.pi*dr*r*_elec_cond(T,data_tra)*E)

                # E changed to match current
                E *= I0/I

                # Relative error calculation
                if i > 1:
                    err = np.linalg.norm(T - Told)/np.linalg.norm(Told)
                i += 1

            ##Power evaluation
            Pt = PL*E*I
            Perr = (Pow-Pt)/Pow
            I0 *= (1+pow(Perr,1))

        # print('Calculated Power input:')
        # print(Pt, flush=True)
        # print("")

        # Momentum equation solution
        err = np.float64(1)
        i = 0
        while (err >= tol) and (i < 500):
            # save previous iter field
            Vold = V

            # coefficient calculation
            a = 0.25*(r[0:-1] + r[1:])*(np.asarray(_viscosity(T[0:-1],data_tra)) \
                                    + np.asarray(_viscosity(T[1:],data_tra)))/dr

            A = np.diag(a,k=1) + np.diag(a,k=-1) - np.diag( np.append( \
                                            np.insert(a[0:-1]+a[1:],0,a[0]),a[-1]))

            S = -dr*r*dpdz
            S[0] /= 2

            # velocity boundary condition
            A[-1,-1] = 1
            A[-1,-2] = 0
            S[-1] = V0

            # sistem solution with underrelaxation
            V = 0.05*np.linalg.solve(A,S) + 0.95*V

            # mass flow rate evalution
            mfr = np.sum(2*np.pi*r*dr*_density(T, data_thd)*V)
            vfr = 60000*mfr/_density(Tref, data_thd)

            # pressure gradient updated to match flow rate
            dpdz *=  (0.95 + 0.05* vfr0/vfr)

            # Relative error calculation
            if i > 1:
                err = np.linalg.norm(V - Vold)/np.linalg.norm(Vold)
            i = i + 1

        # Turbulence properties calculation
        Re = 2*R*V[:-1]/_viscosity(T[:-1], data_tra)
        II = 0.16*pow(Re,-1/8)
        LL = 0.07*2*R/pow(0.09,3/4)
        k = 1.5*pow(II*V[:-1],2)
        eps = pow(0.09,0.75)*pow(k,1.5)/LL

        # Thermophysical properties calculation
        T1 = data_thd[:,1]
        rho = data_thd[:,2]
        Cp = data_thd[:,6]
        H = data_thd[:,5]
        mu = data_tra[:,2]
        kappa = data_tra[:,3]
        sigmaE = data_tra[:,4]
        S = integrate.cumtrapz(Cp/T1,T1,initial=0)

        # Temperature derivatives calculation
        dCpdT = []
        dHdT = []
        dSdT = []

        for i in range(0,len(T1)):
            if i == 0:
                dCpdT.append((Cp[i+1]-Cp[i])/(T1[i+1]-T1[i]))
                dHdT.append((H[i+1]-H[i])/(T1[i+1]-T1[i]))
                dSdT.append((S[i+1]-S[i])/(T1[i+1]-T1[i]))
            elif i == len(T1)-1:
                dCpdT.append((Cp[i]-Cp[i-1])/(T1[i]-T1[i-1]))
                dHdT.append((H[i]-H[i-1])/(T1[i]-T1[i-1]))
                dSdT.append((S[i]-S[i-1])/(T1[i]-T1[i-1]))
            else:
                dCpdT.append((Cp[i+1]-Cp[i-1])/(T1[i+1]-T1[i-1]))
                dHdT.append((H[i+1]-H[i-1])/(T1[i+1]-T1[i-1]))
                dSdT.append((S[i+1]-S[i-1])/(T1[i+1]-T1[i-1]))

        # Radiation energy loss source for given mixture calculation
        Trad = np.arange(5000,30000,1000)
        Trad = np.append(Trad,30000)
        rad = ar*_rad_ar(Trad) + h2*_rad_h2(Trad) + \
                    n2*_rad_n2(Trad) + o2*_rad_o2(Trad)

        Trad = np.arange(3000,30000,1000)
        Trad = np.append(Trad,30000)
        rad = np.insert(rad,0,0)
        rad = np.insert(rad,0,0)

        ## Save data
        # Save all profile for boundary conditions and radiation sink
        np.savetxt(str(os.path.join(out_dir,'VR')),np.transpose((r,V)), delimiter=',') # velocity

        np.savetxt(str(os.path.join(out_dir,'TR')),np.transpose((r,T)), delimiter=',') # temperature

        np.savetxt(str(os.path.join(out_dir,'epsR')),np.transpose((r[:-1],eps)), delimiter=',') # epsilon

        np.savetxt(str(os.path.join(out_dir,'kR')),np.transpose((r[:-1],k)), delimiter=',') # k

        # Write radiation source file
        np.savetxt(str(os.path.join(out_dir,'radiation.rad')),np.c_[Trad,rad], delimiter = ',') # radiation

        # Save all thermophysical properties datas
        # rho
        np.savetxt(str(os.path.join(out_dir,'rho')),np.c_[T1,rho], delimiter = ',')

        # Cp
        np.savetxt(str(os.path.join(out_dir,'Cp')),np.c_[T1,Cp], delimiter = ',')

        # H
        np.savetxt(str(os.path.join(out_dir,'enthalpy')),np.c_[T1,H], delimiter = ',')

        # mu
        np.savetxt(str(os.path.join(out_dir,'mu')),np.c_[T1,mu], delimiter = ',')

        # kappa
        np.savetxt(str(os.path.join(out_dir,'kappa')),np.c_[T1,kappa], delimiter = ',')

        # sigma
        np.savetxt(str(os.path.join(out_dir,'sigmaE')),np.c_[T1,sigmaE], delimiter = ',')

        # S
        np.savetxt(str(os.path.join(out_dir,'entropy')),np.c_[T1,S], delimiter = ',')

        # Save reference density value for nanoDOME
        np.savetxt(str(os.path.join(out_dir,'densRef')), \
                   np.c_[Tref,_density(Tref, data_thd)], delimiter=' ')