'''
  Copyright (C) 2013 by Christopher Cooper, Lorena Barba

  Permission is hereby granted, free of charge, to any person obtaining a copy
  of this software and associated documentation files (the "Software"), to deal
  in the Software without restriction, including without limitation the rights
  to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
  copies of the Software, and to permit persons to whom the Software is
  furnished to do so, subject to the following conditions:

  The above copyright notice and this permission notice shall be included in
  all copies or substantial portions of the Software.

  THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
  IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
  FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
  AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
  LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
  OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN
  THE SOFTWARE.
'''

from numpy import *
from GaussIntegration import gaussIntegration_fine


def calculate_phir(phi, dphi, s, xq, K_fine, eps, LorY, kappa):

    phir = 0
    for i in range(len(s.triangle)):
        panel = s.vertex[s.triangle[i]]

        K, V = gaussIntegration_fine(xq, panel, s.normal[i], s.Area[i], K_fine, kappa, LorY, eps)
        phir += (-K*phi[i] + V*dphi[i])/(4*pi)
        
    return phir

def solvationEnergy(surf_array, field_array, param):

    Esolv = []
    field_Esolv = []
    cal2J = 4.184
    C0 = param.qe**2*param.Na*1e-3*1e10/(cal2J*param.E_0)

    for i in range(len(field_array)):
        f = field_array[i]
        if len(f.xq)>0:
        
            phi_reac = 0

#           First look at child surfaces
            for cs in f.child:
                s = surf_array[cs]
                phi_aux = calculate_phir(s.phi, s.Ehat*s.dphi, s, f.xq, param.K_fine, param.eps, f.LorY, f.kappa)

                phi_reac -= phi_aux     # Minus accounts for normals pointing out
            
#           Now look at parent surface
            if len(f.parent)>0:
                ps = f.parent[0]
                s = surf_array[ps] 
                phi_aux = calculate_phir(s.phi, s.dphi, s, f.xq, param.K_fine, param.eps, f.LorY, f.kappa)
                
                phi_reac += phi_aux

            Esolv.append(0.5*C0*sum(f.q*phi_reac))
            field_Esolv.append(i)

    return Esolv, field_Esolv

def coulombicEnergy(field_array, param):

    Ecoul = []
    field_coul = []
    cal2J = 4.184
    C0 = param.qe**2*param.Na*1e-3*1e10/(cal2J*param.E_0)
    for i in range(len(field_array)):
        f = field_array[i]
        if f.coul==1:
            Nq = len(f.xq)
            x = f.xq[:,0]
            y = f.xq[:,1]
            z = f.xq[:,2]
            
            dx = transpose(ones(Nq,Nq)*x) - x
            dy = transpose(ones(Nq,Nq)*y) - y
            dz = transpose(ones(Nq,Nq)*z) - z

            r = sqrt(dx*dx+dy*dy+dz*dz)

            M = 1/(f.E*r)

            phi_q = dot(M,f.q)

            Ecoul.append(0.5*C0*sum(phi_q*f.q))
            field_coul.append(i)

    return Ecoul, field_coul

    


def surfaceEnergy(surf_array, param):

    Esurf = []
    surf_Esurf = []
    cal2J = 4.184
    C0 = param.qe**2*param.Na*1e-3*1e10/(cal2J*param.E_0)

    for i in range(len(surf_array)):
        s = surf_array[i]

        if s.surf_type == 'dirichlet_surface':
            surf_Esurf.append(i)
            Esurf_aux = -sum(-s.Eout*s.dphi*s.phi*s.Area)
            Esurf.append(0.5*C0*Esurf_aux)
            
        elif s.surf_type == 'neumann_surface':
            surf_Esurf.append(i)
            Esurf_aux = sum(-s.Eout*s.dphi*s.phi*s.Area)
            Esurf.append(0.5*C0*Esurf_aux)

    return Esurf, surf_Esurf

def fill_phi(phi, surf_array):
# Places the result vector on surf structure 

    s_start = 0 
    for i in range(len(surf_array)):
        s_size = len(surf_array[i].xi)
        if surf_array[i].surf_type=='dirichlet_surface':
            surf_array[i].phi = surf_array[i].phi0
            surf_array[i].dphi = phi[s_start:s_start+s_size]
            s_start += s_size
        elif surf_array[i].surf_type=='neumann_surface':
            surf_array[i].dphi = surf_array[i].phi0
            surf_array[i].phi  = phi[s_start:s_start+s_size]
            s_start += s_size
        else:
            surf_array[i].phi  = phi[s_start:s_start+s_size]
            surf_array[i].dphi = phi[s_start+s_size:s_start+2*s_size]
            s_start += 2*s_size
