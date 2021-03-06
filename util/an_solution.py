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

"""
All functions output the analytical solution in kcal/mol
"""
from numpy import *
from scipy import special
from scipy.special import lpmv
from scipy.misc import factorial
from math import gamma
from scipy.linalg import solve

def an_spherical(q, xq, E_1, E_2, E_0, R, N):
        
    PHI = zeros(len(q))
    for K in range(len(q)):
        rho = sqrt(sum(xq[K]**2))
        zenit = arccos(xq[K,2]/rho)
        azim  = arctan2(xq[K,1],xq[K,0])

        phi = 0.+0.*1j
        for n in range(N):
            for m in range(-n,n+1):
                sph1 = special.sph_harm(m,n,zenit,azim)
                cons1 = rho**n/(E_1*E_0*R**(2*n+1))*(E_1-E_2)*(n+1)/(E_1*n+E_2*(n+1))
                cons2 = 4*pi/(2*n+1)

                for k in range(len(q)):
                    rho_k   = sqrt(sum(xq[k]**2))
                    zenit_k = arccos(xq[k,2]/rho_k)
                    azim_k  = arctan2(xq[k,1],xq[k,0])
                    sph2 = conj(special.sph_harm(m,n,zenit_k,azim_k))
                    phi += cons1*cons2*q[K]*rho_k**n*sph1*sph2
        
        PHI[K] = real(phi)/(4*pi)

    return PHI

def get_K(x,n):

    K = 0.
    n_fact = factorial(n)
    n_fact2 = factorial(2*n)
    for s in range(n+1):
        K += 2**s*n_fact*factorial(2*n-s)/(factorial(s)*n_fact2*factorial(n-s)) * x**s

    return K


def an_P(q, xq, E_1, E_2, R, kappa, a, N):

    qe = 1.60217646e-19
    Na = 6.0221415e23
    E_0 = 8.854187818e-12
    cal2J = 4.184 

    PHI = zeros(len(q))
    for K in range(len(q)):
        rho = sqrt(sum(xq[K]**2))
        zenit = arccos(xq[K,2]/rho)
        azim  = arctan2(xq[K,1],xq[K,0])

        phi = 0.+0.*1j
        for n in range(N):
            for m in range(-n,n+1):
                P1 = lpmv(abs(m),n,cos(zenit))

                Enm = 0.
                for k in range(len(q)):
                    rho_k   = sqrt(sum(xq[k]**2))
                    zenit_k = arccos(xq[k,2]/rho_k)
                    azim_k  = arctan2(xq[k,1],xq[k,0])
                    P2 = lpmv(abs(m),n,cos(zenit_k))

                    Enm += q[k]*rho_k**n*factorial(n-abs(m))/factorial(n+abs(m))*P2*exp(-1j*m*azim_k)
    
                C2 = (kappa*a)**2*get_K(kappa*a,n-1)/(get_K(kappa*a,n+1) + 
                        n*(E_2-E_1)/((n+1)*E_2+n*E_1)*(R/a)**(2*n+1)*(kappa*a)**2*get_K(kappa*a,n-1)/((2*n-1)*(2*n+1)))
                C1 = Enm/(E_2*E_0*a**(2*n+1)) * (2*n+1)/(2*n-1) * (E_2/((n+1)*E_2+n*E_1))**2

                if n==0 and m==0:
                    Bnm = Enm/(E_0*R)*(1/E_2-1/E_1) - Enm*kappa*a/(E_0*E_2*a*(1+kappa*a))
                else:
                    Bnm = 1./(E_1*E_0*R**(2*n+1)) * (E_1-E_2)*(n+1)/(E_1*n+E_2*(n+1)) * Enm - C1*C2

                phi += Bnm*rho**n*P1*exp(1j*m*azim)

        PHI[K] = real(phi)/(4*pi)

    C0 = qe**2*Na*1e-3*1e10/(cal2J)
    E_P = 0.5*C0*sum(q*PHI)

    return E_P

def two_sphere_KimSong(a, R, kappa, E_1, E_2, q):

    E_hat = E_2/E_1
    qe = 1.60217646e-19
    Na = 6.0221415e23
    E_0 = 8.854187818e-12
    cal2J = 4.184 

    C0 = -q/(a*a*E_hat*kappa*E_1)
    k0a = exp(-kappa*a)/(kappa*a)
    k0R = exp(-kappa*R)/(kappa*R)
    k1a = -k0a - k0a/(kappa*a)
    i0 = sinh(kappa*a)/(kappa*a)
    i1 = cosh(kappa*a)/(kappa*a) - i0/(kappa*a)

    CC0 = qe**2*Na*1e-3*1e10/(cal2J*E_0*4*pi)

    Einter = 0.5*q*C0*CC0*( (k0a+k0R*i0)/(k1a+k0R*i1) - k0a/k1a)
    E1sphere = 0.5*q*C0*CC0*(k0a/k1a) - 0.5*CC0*q**2/(a*E_1)
    E2sphere = 0.5*q*C0*CC0*(k0a+k0R*i0)/(k1a+k0R*i1) - 0.5*CC0*q**2/(a*E_1)

    return Einter, E1sphere, E2sphere

def two_sphere(a, R, kappa, E_1, E_2, q):

    N = 20 # Number of terms in expansion

    qe = 1.60217646e-19
    Na = 6.0221415e23
    E_0 = 8.854187818e-12
    cal2J = 4.184 

    index2 = arange(N+1, dtype=float) + 0.5
    index  = index2[0:-1]

    K1 = special.kv(index2, kappa*a)
    K1p = index/(kappa*a)*K1[0:-1] - K1[1:]
    
    k1 = special.kv(index, kappa*a)*sqrt(pi/(2*kappa*a))
    k1p = -sqrt(pi/2)*1/(2*(kappa*a)**(3/2.))*special.kv(index, kappa*a) + sqrt(pi/(2*kappa*a))*K1p

    I1 = special.iv(index2, kappa*a)
    I1p = index/(kappa*a)*I1[0:-1] + I1[1:]
    i1 = special.iv(index, kappa*a)*sqrt(pi/(2*kappa*a))
    i1p = -sqrt(pi/2)*1/(2*(kappa*a)**(3/2.))*special.iv(index, kappa*a) + sqrt(pi/(2*kappa*a))*I1p

    B = zeros((N,N), dtype=float)

    for n in range(N):
        for m in range(N):
            for nu in range(N):
                if n>=nu and m>=nu:
                    g1 = gamma(n-nu+0.5)
                    g2 = gamma(m-nu+0.5)
                    g3 = gamma(nu+0.5)
                    g4 = gamma(m+n-nu+1.5)
                    f1 = factorial(n+m-nu)
                    f2 = factorial(n-nu)
                    f3 = factorial(m-nu)
                    f4 = factorial(nu)
                    Anm = g1*g2*g3*f1*(n+m-2*nu+0.5)/(pi*g4*f2*f3*f4)
                    kB = special.kv(n+m-2*nu+0.5,kappa*R)*sqrt(pi/(2*kappa*R))
                    B[n,m] += Anm*kB 

    M = zeros((N,N), float)
    E_hat = E_1/E_2
    for i in range(N):
        for j in range(N):
            M[i,j] = (2*i+1)*B[i,j]*(kappa*i1p[i] - E_hat*i*i1[i]/a)
            if i==j:
                M[i,j] += kappa*k1p[i] - E_hat*i*k1[i]/a

    RHS = zeros(N)
    RHS[0] = -E_hat*q/(4*pi*E_1*a*a)

    a_coeff = solve(M,RHS)

    a0 = a_coeff[0] 
    a0_inf = -E_hat*q/(4*pi*E_1*a*a)*1/(kappa*k1p[0])
   
    phi_2 = a0*k1[0] + i1[0]*sum(a_coeff*B[:,0]) - q/(4*pi*E_1*a)
    phi_1 = a0_inf*k1[0] - q/(4*pi*E_1*a)
    phi_inter = phi_2-phi_1 

    CC0 = qe**2*Na*1e-3*1e10/(cal2J*E_0)

    Einter = 0.5*CC0*q*phi_inter
    E1sphere = 0.5*CC0*q*phi_1
    E2sphere = 0.5*CC0*q*phi_2

    return Einter, E1sphere, E2sphere


def constant_potential_single_point(phi0, a, r, kappa):
    phi = a/r * phi0 * exp(kappa*(a-r))
    return phi

def constant_charge_single_point(sigma0, a, r, kappa, epsilon):
    dphi0 = -sigma0/epsilon
    phi = -dphi0 * a*a/(1+kappa*a) * exp(kappa*(a-r))/r 
    return phi

def constant_potential_single_charge(phi0, radius, kappa, epsilon):
    dphi = -phi0*((1.+kappa*radius)/radius)
    sigma = -epsilon*dphi # Surface charge
    return sigma

def constant_charge_single_potential(sigma0, radius, kappa, epsilon):
    dphi = -sigma0/epsilon 
    phi = -dphi * radius/(1.+kappa*radius) # Surface potential
    return phi

def constant_charge_twosphere_HsuLiu(sigma01, sigma02, r1, r2, R, kappa, epsilon):
    
    gamma1 = -0.5*(1/(kappa*r1) - (1 + 1/(kappa*r1))*exp(-2*kappa*r1))
    gamma2 = -0.5*(1/(kappa*r2) - (1 + 1/(kappa*r2))*exp(-2*kappa*r2))

    qe = 1.60217646e-19
    Na = 6.0221415e23
    E_0 = 8.854187818e-12
    cal2J = 4.184 

    f1 = (0.5+gamma1)/(0.5-gamma1)
    f2 = (0.5+gamma2)/(0.5-gamma2)

    if f1*f2<0:
        A = arctan(sqrt(abs(f1*f2))*exp(-kappa*(R-r1-r2)))
    else:
        A = arctanh(sqrt(f1*f2)*exp(-kappa*(R-r1-r2)))

    phi01 = constant_charge_single_potential(sigma01, r1, kappa, epsilon)
    phi02 = constant_charge_single_potential(sigma02, r2, kappa, epsilon)

    C0 = pi*epsilon*r1*r2/R
    C1 = (f2*phi01*phi01 + f1*phi02*phi02)/(f1*f2) * log(1-f1*f2*exp(-2*kappa*(R-r1-r2)))
    C2 = 4*phi01*phi02/sqrt(abs(f1*f2)) * A

    CC0 = qe**2*Na*1e-3*1e10/(cal2J*E_0)

    E_inter = CC0*C0*(C1 + C2)

    return E_inter

def constant_charge_twosphere_bell(sigma01, sigma02, r1, r2, R, kappa, epsilon):

    E_inter = 4*pi/epsilon*(sigma01*r1*r1/(1+kappa*r1))*(sigma02*r2*r2/(1+kappa*r2))*exp(-kappa*(R-r1-r2))/R

    qe = 1.60217646e-19
    Na = 6.0221415e23
    E_0 = 8.854187818e-12
    cal2J = 4.184 
    CC0 = qe**2*Na*1e-3*1e10/(cal2J*E_0)

    return CC0*E_inter

def constant_potential_twosphere(phi01, phi02, r1, r2, R, kappa, epsilon):

    kT = 4.1419464e-21 # at 300K
    qe = 1.60217646e-19
    Na = 6.0221415e23
    E_0 = 8.854187818e-12
    cal2J = 4.184 
    C0 = kT/qe

    phi01 /= C0
    phi02 /= C0

    k1 = special.kv(0.5,kappa*r1)*sqrt(pi/(2*kappa*r1))
    k2 = special.kv(0.5,kappa*r2)*sqrt(pi/(2*kappa*r2))
    B00 = special.kv(0.5,kappa*R)*sqrt(pi/(2*kappa*R))
#    k1 = special.kv(0.5,kappa*r1)*sqrt(2/(pi*kappa*r1))
#    k2 = special.kv(0.5,kappa*r2)*sqrt(2/(pi*kappa*r2))
#    B00 = special.kv(0.5,kappa*R)*sqrt(2/(pi*kappa*R))

    i1 = special.iv(0.5,kappa*r1)*sqrt(pi/(2*kappa*r1))
    i2 = special.iv(0.5,kappa*r2)*sqrt(pi/(2*kappa*r2))

    a0 = (phi02*B00*i1 - phi01*k2)/(B00*B00*i2*i1 - k1*k2)
    b0 = (phi02*k1 - phi01*B00*i2)/(k2*k1 - B00*B00*i1*i2)

    U1 = 2*pi*phi01*(phi01*exp(kappa*r1)*(kappa*r1)*(kappa*r1)/sinh(kappa*r1) - pi*a0/(2*i1))
    U2 = 2*pi*phi02*(phi02*exp(kappa*r2)*(kappa*r2)*(kappa*r2)/sinh(kappa*r2) - pi*b0/(2*i2))

    print 'U1: %f'%U1
    print 'U2: %f'%U2
    print 'E: %f'%(U1 + U2) 
    C1 = C0*C0*epsilon/kappa
    u1 = U1*C1
    u2 = U2*C1

    CC0 = qe**2*Na*1e-3*1e10/(cal2J*E_0)

    E_inter = CC0*(u1+u2)

    return E_inter

def constant_potential_twosphere_2(phi01, phi02, r1, r2, R, kappa, epsilon):

    kT = 4.1419464e-21 # at 300K
    qe = 1.60217646e-19
    Na = 6.0221415e23
    E_0 = 8.854187818e-12
    cal2J = 4.184 
    h = R-r1-r2
#    E_inter = r1*r2*epsilon/(4*R) * ( (phi01+phi02)**2 * log(1+exp(-kappa*h)) + (phi01-phi02)**2*log(1-exp(-kappa*h)) )
#    E_inter = epsilon*r1*phi01**2/2 * log(1+exp(-kappa*h))
    E_inter = epsilon*r1*r2*(phi01**2+phi02**2)/(4*(r1+r2)) * ( (2*phi01*phi02)/(phi01**2+phi02**2) * log((1+exp(-kappa*h))/(1-exp(-kappa*h))) + log(1-exp(-2*kappa*h)) )

    CC0 = qe**2*Na*1e-3*1e10/(cal2J*E_0)
    E_inter *= CC0
    return E_inter

def constant_potential_single_energy(phi0, r1, kappa, epsilon):

    N = 1 # Number of terms in expansion
     
    qe = 1.60217646e-19
    Na = 6.0221415e23
    E_0 = 8.854187818e-12
    cal2J = 4.184 

    index2 = arange(N+1, dtype=float) + 0.5
    index  = index2[0:-1]

    K1 = special.kv(index2, kappa*r1)
    K1p = index/(kappa*r1)*K1[0:-1] - K1[1:]
    k1 = special.kv(index, kappa*r1)*sqrt(pi/(2*kappa*r1))
    k1p = -sqrt(pi/2)*1/(2*(kappa*r1)**(3/2.))*special.kv(index, kappa*r1) + sqrt(pi/(2*kappa*r1))*K1p

    a0_inf = phi0/k1[0]
    U1_inf = a0_inf*k1p[0]
 
    C1 = 2*pi*kappa*phi0*r1*r1*epsilon
    C0 = qe**2*Na*1e-3*1e10/(cal2J*E_0)
    E = C0*C1*U1_inf
    
    return E

def constant_charge_single_energy(phi0, r1, kappa, epsilon):

    N = 20 # Number of terms in expansion
     
    qe = 1.60217646e-19
    Na = 6.0221415e23
    E_0 = 8.854187818e-12
    cal2J = 4.184 

    index2 = arange(N+1, dtype=float) + 0.5
    index  = index2[0:-1]

    K1 = special.kv(index2, kappa*r1)
    K1p = index/(kappa*r1)*K1[0:-1] - K1[1:]
    k1 = special.kv(index, kappa*r1)*sqrt(pi/(2*kappa*r1))
    k1p = -sqrt(pi/2)*1/(2*(kappa*r1)**(3/2.))*special.kv(index, kappa*r1) + sqrt(pi/(2*kappa*r1))*K1p

    a0_inf = -phi0/(epsilon*kappa*k1p[0])
   
    U1_inf = a0_inf*k1[0]
 
    C1 = 2*pi*phi0*r1*r1
    C0 = qe**2*Na*1e-3*1e10/(cal2J*E_0)
    E_inter = C0*C1*U1_inf
    
    return E_inter

def constant_potential_twosphere_dissimilar(phi01, phi02, r1, r2, R, kappa, epsilon):

    N = 20 # Number of terms in expansion
     
    qe = 1.60217646e-19
    Na = 6.0221415e23
    E_0 = 8.854187818e-12
    cal2J = 4.184 

    index2 = arange(N+1, dtype=float) + 0.5
    index  = index2[0:-1]

    K1 = special.kv(index2, kappa*r1)
    K1p = index/(kappa*r1)*K1[0:-1] - K1[1:]
    k1 = special.kv(index, kappa*r1)*sqrt(pi/(2*kappa*r1))
    k1p = -sqrt(pi/2)*1/(2*(kappa*r1)**(3/2.))*special.kv(index, kappa*r1) + sqrt(pi/(2*kappa*r1))*K1p

    K2 = special.kv(index2, kappa*r2)
    K2p = index/(kappa*r2)*K2[0:-1] - K2[1:]
    k2 = special.kv(index, kappa*r2)*sqrt(pi/(2*kappa*r2))
    k2p = -sqrt(pi/2)*1/(2*(kappa*r2)**(3/2.))*special.kv(index, kappa*r2) + sqrt(pi/(2*kappa*r2))*K2p

    I1 = special.iv(index2, kappa*r1)
    I1p = index/(kappa*r1)*I1[0:-1] + I1[1:]
    i1 = special.iv(index, kappa*r1)*sqrt(pi/(2*kappa*r1))
    i1p = -sqrt(pi/2)*1/(2*(kappa*r1)**(3/2.))*special.iv(index, kappa*r1) + sqrt(pi/(2*kappa*r1))*I1p

    I2 = special.iv(index2, kappa*r2)
    I2p = index/(kappa*r2)*I2[0:-1] + I2[1:]
    i2 = special.iv(index, kappa*r2)*sqrt(pi/(2*kappa*r2))
    i2p = -sqrt(pi/2)*1/(2*(kappa*r2)**(3/2.))*special.iv(index, kappa*r2) + sqrt(pi/(2*kappa*r2))*I2p

    B = zeros((N,N), dtype=float)

    for n in range(N):
        for m in range(N):
            for nu in range(N):
                if n>=nu and m>=nu:
                    g1 = gamma(n-nu+0.5)
                    g2 = gamma(m-nu+0.5)
                    g3 = gamma(nu+0.5)
                    g4 = gamma(m+n-nu+1.5)
                    f1 = factorial(n+m-nu)
                    f2 = factorial(n-nu)
                    f3 = factorial(m-nu)
                    f4 = factorial(nu)
                    Anm = g1*g2*g3*f1*(n+m-2*nu+0.5)/(pi*g4*f2*f3*f4)
                    kB = special.kv(n+m-2*nu+0.5,kappa*R)*sqrt(pi/(2*kappa*R))
                    B[n,m] += Anm*kB 

    M = zeros((2*N,2*N), float)
    for j in range(N):
        for n in range(N):
            M[j,n+N] = (2*j+1)*B[j,n]*i1[j]/k2[n]
            M[j+N,n] = (2*j+1)*B[j,n]*i2[j]/k1[n]
            if n==j:
                M[j,n] = 1
                M[j+N,n+N] = 1

    RHS = zeros(2*N)
    RHS[0] = phi01
    RHS[N] = phi02

    coeff = solve(M,RHS)

    a = coeff[0:N]/k1
    b = coeff[N:2*N]/k2

    a0 = a[0] 
    a0_inf = phi01/k1[0]
    b0 = b[0] 
    b0_inf = phi02/k2[0]
   
    U1_inf = a0_inf*k1p[0]
    U1_h   = a0*k1p[0]+i1p[0]*sum(b*B[:,0])
 
    U2_inf = b0_inf*k2p[0]
    U2_h   = b0*k2p[0]+i2p[0]*sum(a*B[:,0])

    C1 = 2*pi*kappa*phi01*r1*r1*epsilon
    C2 = 2*pi*kappa*phi02*r2*r2*epsilon
    C0 = qe**2*Na*1e-3*1e10/(cal2J*E_0)
    E_inter = C0*(C1*(U1_h-U1_inf) + C2*(U2_h-U2_inf))
    
    return E_inter

def constant_charge_twosphere_dissimilar(phi01, phi02, r1, r2, R, kappa, epsilon):

    N = 20 # Number of terms in expansion
     
    qe = 1.60217646e-19
    Na = 6.0221415e23
    E_0 = 8.854187818e-12
    cal2J = 4.184 

    index2 = arange(N+1, dtype=float) + 0.5
    index  = index2[0:-1]

    K1 = special.kv(index2, kappa*r1)
    K1p = index/(kappa*r1)*K1[0:-1] - K1[1:]
    k1 = special.kv(index, kappa*r1)*sqrt(pi/(2*kappa*r1))
    k1p = -sqrt(pi/2)*1/(2*(kappa*r1)**(3/2.))*special.kv(index, kappa*r1) + sqrt(pi/(2*kappa*r1))*K1p

    K2 = special.kv(index2, kappa*r2)
    K2p = index/(kappa*r2)*K2[0:-1] - K2[1:]
    k2 = special.kv(index, kappa*r2)*sqrt(pi/(2*kappa*r2))
    k2p = -sqrt(pi/2)*1/(2*(kappa*r2)**(3/2.))*special.kv(index, kappa*r2) + sqrt(pi/(2*kappa*r2))*K2p

    I1 = special.iv(index2, kappa*r1)
    I1p = index/(kappa*r1)*I1[0:-1] + I1[1:]
    i1 = special.iv(index, kappa*r1)*sqrt(pi/(2*kappa*r1))
    i1p = -sqrt(pi/2)*1/(2*(kappa*r1)**(3/2.))*special.iv(index, kappa*r1) + sqrt(pi/(2*kappa*r1))*I1p

    I2 = special.iv(index2, kappa*r2)
    I2p = index/(kappa*r2)*I2[0:-1] + I2[1:]
    i2 = special.iv(index, kappa*r2)*sqrt(pi/(2*kappa*r2))
    i2p = -sqrt(pi/2)*1/(2*(kappa*r2)**(3/2.))*special.iv(index, kappa*r2) + sqrt(pi/(2*kappa*r2))*I2p

    B = zeros((N,N), dtype=float)

    for n in range(N):
        for m in range(N):
            for nu in range(N):
                if n>=nu and m>=nu:
                    g1 = gamma(n-nu+0.5)
                    g2 = gamma(m-nu+0.5)
                    g3 = gamma(nu+0.5)
                    g4 = gamma(m+n-nu+1.5)
                    f1 = factorial(n+m-nu)
                    f2 = factorial(n-nu)
                    f3 = factorial(m-nu)
                    f4 = factorial(nu)
                    Anm = g1*g2*g3*f1*(n+m-2*nu+0.5)/(pi*g4*f2*f3*f4)
                    kB = special.kv(n+m-2*nu+0.5,kappa*R)*sqrt(pi/(2*kappa*R))
                    B[n,m] += Anm*kB 

    M = zeros((2*N,2*N), float)
    for j in range(N):
        for n in range(N):
            M[j,n+N] = (2*j+1)*B[j,n]*r1*i1p[j]/(r2*k2p[n])
            M[j+N,n] = (2*j+1)*B[j,n]*r2*i2p[j]/(r1*k1p[n])
            if n==j:
                M[j,n] = 1
                M[j+N,n+N] = 1

    RHS = zeros(2*N)
    RHS[0] = phi01*r1/epsilon
    RHS[N] = phi02*r2/epsilon

    coeff = solve(M,RHS)

    a = coeff[0:N]/(-r1*kappa*k1p)
    b = coeff[N:2*N]/(-r2*kappa*k2p)

    a0 = a[0] 
    a0_inf = -phi01/(epsilon*kappa*k1p[0])
    b0 = b[0] 
    b0_inf = -phi02/(epsilon*kappa*k2p[0])
   
    U1_inf = a0_inf*k1[0]
    U1_h   = a0*k1[0]+i1[0]*sum(b*B[:,0])
 
    U2_inf = b0_inf*k2[0]
    U2_h   = b0*k2[0]+i2[0]*sum(a*B[:,0])

    C1 = 2*pi*phi01*r1*r1
    C2 = 2*pi*phi02*r2*r2
    C0 = qe**2*Na*1e-3*1e10/(cal2J*E_0)
    E_inter = C0*(C1*(U1_h-U1_inf) + C2*(U2_h-U2_inf))
    
    return E_inter

def molecule_constant_potential(q, phi02, r1, r2, R, kappa, E_1, E_2):

    N = 20 # Number of terms in expansion

    qe = 1.60217646e-19
    Na = 6.0221415e23
    E_0 = 8.854187818e-12
    cal2J = 4.184 

    index2 = arange(N+1, dtype=float) + 0.5
    index  = index2[0:-1]

    K1 = special.kv(index2, kappa*r1)
    K1p = index/(kappa*r1)*K1[0:-1] - K1[1:]
    k1 = special.kv(index, kappa*r1)*sqrt(pi/(2*kappa*r1))
    k1p = -sqrt(pi/2)*1/(2*(kappa*r1)**(3/2.))*special.kv(index, kappa*r1) + sqrt(pi/(2*kappa*r1))*K1p

    K2 = special.kv(index2, kappa*r2)
    K2p = index/(kappa*r2)*K2[0:-1] - K2[1:]
    k2 = special.kv(index, kappa*r2)*sqrt(pi/(2*kappa*r2))
    k2p = -sqrt(pi/2)*1/(2*(kappa*r2)**(3/2.))*special.kv(index, kappa*r2) + sqrt(pi/(2*kappa*r2))*K2p

    I1 = special.iv(index2, kappa*r1)
    I1p = index/(kappa*r1)*I1[0:-1] + I1[1:]
    i1 = special.iv(index, kappa*r1)*sqrt(pi/(2*kappa*r1))
    i1p = -sqrt(pi/2)*1/(2*(kappa*r1)**(3/2.))*special.iv(index, kappa*r1) + sqrt(pi/(2*kappa*r1))*I1p

    I2 = special.iv(index2, kappa*r2)
    I2p = index/(kappa*r2)*I2[0:-1] + I2[1:]
    i2 = special.iv(index, kappa*r2)*sqrt(pi/(2*kappa*r2))
    i2p = -sqrt(pi/2)*1/(2*(kappa*r2)**(3/2.))*special.iv(index, kappa*r2) + sqrt(pi/(2*kappa*r2))*I2p

    B = zeros((N,N), dtype=float)

    for n in range(N):
        for m in range(N):
            for nu in range(N):
                if n>=nu and m>=nu:
                    g1 = gamma(n-nu+0.5)
                    g2 = gamma(m-nu+0.5)
                    g3 = gamma(nu+0.5)
                    g4 = gamma(m+n-nu+1.5)
                    f1 = factorial(n+m-nu)
                    f2 = factorial(n-nu)
                    f3 = factorial(m-nu)
                    f4 = factorial(nu)
                    Anm = g1*g2*g3*f1*(n+m-2*nu+0.5)/(pi*g4*f2*f3*f4)
                    kB = special.kv(n+m-2*nu+0.5,kappa*R)*sqrt(pi/(2*kappa*R))
                    B[n,m] += Anm*kB 

    E_hat = E_1/E_2
    M = zeros((2*N,2*N), float)
    for j in range(N):
        for n in range(N):
            M[j,n+N] = (2*j+1)*B[j,n]*(kappa*i1p[j]/k2[n] - E_hat*j/r1*i1[j]/k2[n])
            M[j+N,n] = (2*j+1)*B[j,n]*i2[j] * 1/(kappa*k1p[n] - E_hat*n/r1*k1[n])
            if n==j:
                M[j,n] = 1
                M[j+N,n+N] = 1

    RHS = zeros(2*N)
    RHS[0] = -E_hat*q/(4*pi*E_1*r1*r1)
    RHS[N] = phi02

    coeff = solve(M,RHS)

    a = coeff[0:N]/(kappa*k1p - E_hat*arange(N)/r1*k1)
    b = coeff[N:2*N]/k2

    a0 = a[0] 
    a0_inf = -E_hat*q/(4*pi*E_1*r1*r1)*1/(kappa*k1p[0]) 
    b0 = b[0] 
    b0_inf = phi02/k2[0]
   
    phi_inf = a0_inf*k1[0] - q/(4*pi*E_1*r1)
    phi_h   = a0*k1[0] + i1[0]*sum(b*B[:,0]) - q/(4*pi*E_1*r1) 
    phi_inter = phi_h - phi_inf
 
    U_inf = b0_inf*k2p[0]
    U_h   = b0*k2p[0]+i2p[0]*sum(a*B[:,0])
    U_inter = U_h - U_inf

    C0 = qe**2*Na*1e-3*1e10/(cal2J*E_0)
    C1 = q * 0.5
    C2 = 2*pi*kappa*phi02*r2*r2*E_2
    E_inter = C0*(C1*phi_inter + C2*U_inter)
    
    return E_inter

def molecule_constant_charge(q, phi02, r1, r2, R, kappa, E_1, E_2):

    N = 20 # Number of terms in expansion
     
    qe = 1.60217646e-19
    Na = 6.0221415e23
    E_0 = 8.854187818e-12
    cal2J = 4.184 

    index2 = arange(N+1, dtype=float) + 0.5
    index  = index2[0:-1]

    K1 = special.kv(index2, kappa*r1)
    K1p = index/(kappa*r1)*K1[0:-1] - K1[1:]
    k1 = special.kv(index, kappa*r1)*sqrt(pi/(2*kappa*r1))
    k1p = -sqrt(pi/2)*1/(2*(kappa*r1)**(3/2.))*special.kv(index, kappa*r1) + sqrt(pi/(2*kappa*r1))*K1p

    K2 = special.kv(index2, kappa*r2)
    K2p = index/(kappa*r2)*K2[0:-1] - K2[1:]
    k2 = special.kv(index, kappa*r2)*sqrt(pi/(2*kappa*r2))
    k2p = -sqrt(pi/2)*1/(2*(kappa*r2)**(3/2.))*special.kv(index, kappa*r2) + sqrt(pi/(2*kappa*r2))*K2p

    I1 = special.iv(index2, kappa*r1)
    I1p = index/(kappa*r1)*I1[0:-1] + I1[1:]
    i1 = special.iv(index, kappa*r1)*sqrt(pi/(2*kappa*r1))
    i1p = -sqrt(pi/2)*1/(2*(kappa*r1)**(3/2.))*special.iv(index, kappa*r1) + sqrt(pi/(2*kappa*r1))*I1p

    I2 = special.iv(index2, kappa*r2)
    I2p = index/(kappa*r2)*I2[0:-1] + I2[1:]
    i2 = special.iv(index, kappa*r2)*sqrt(pi/(2*kappa*r2))
    i2p = -sqrt(pi/2)*1/(2*(kappa*r2)**(3/2.))*special.iv(index, kappa*r2) + sqrt(pi/(2*kappa*r2))*I2p

    B = zeros((N,N), dtype=float)

    for n in range(N):
        for m in range(N):
            for nu in range(N):
                if n>=nu and m>=nu:
                    g1 = gamma(n-nu+0.5)
                    g2 = gamma(m-nu+0.5)
                    g3 = gamma(nu+0.5)
                    g4 = gamma(m+n-nu+1.5)
                    f1 = factorial(n+m-nu)
                    f2 = factorial(n-nu)
                    f3 = factorial(m-nu)
                    f4 = factorial(nu)
                    Anm = g1*g2*g3*f1*(n+m-2*nu+0.5)/(pi*g4*f2*f3*f4)
                    kB = special.kv(n+m-2*nu+0.5,kappa*R)*sqrt(pi/(2*kappa*R))
                    B[n,m] += Anm*kB 

    E_hat = E_1/E_2
    M = zeros((2*N,2*N), float)
    for j in range(N):
        for n in range(N):
            M[j,n+N] = (2*j+1)*B[j,n]*(i1p[j]/k2p[n] - E_hat*j/r1*i1[j]/(kappa*k2p[n]))
            M[j+N,n] = (2*j+1)*B[j,n]*i2p[j]*kappa * 1/(kappa*k1p[n] - E_hat*n/r1*k1[n])
            if n==j:
                M[j,n] = 1
                M[j+N,n+N] = 1

    RHS = zeros(2*N)
    RHS[0] = -E_hat*q/(4*pi*E_1*r1*r1)
    RHS[N] = -phi02/E_2

    coeff = solve(M,RHS)

    a = coeff[0:N]/(kappa*k1p - E_hat*arange(N)/r1*k1)
    b = coeff[N:2*N]/(kappa*k2p)

    a0 = a[0] 
    a0_inf = -E_hat*q/(4*pi*E_1*r1*r1)*1/(kappa*k1p[0]) 
    b0 = b[0] 
    b0_inf = -phi02/(E_2*kappa*k2p[0])
   
    phi_inf = a0_inf*k1[0] - q/(4*pi*E_1*r1)
    phi_h   = a0*k1[0] + i1[0]*sum(b*B[:,0]) - q/(4*pi*E_1*r1) 
    phi_inter = phi_h - phi_inf
 
    U_inf = b0_inf*k2[0]
    U_h   = b0*k2[0]+i2[0]*sum(a*B[:,0])
    U_inter = U_h - U_inf

    C0 = qe**2*Na*1e-3*1e10/(cal2J*E_0)
    C1 = q * 0.5
    C2 = 2*pi*phi02*r2*r2
    E_inter = C0*(C1*phi_inter + C2*U_inter)
    
    return E_inter


def constant_potential_twosphere_identical(phi01, phi02, r1, r2, R, kappa, epsilon):
#   From Carnie+Chan 1993

    N = 20 # Number of terms in expansion
    
    qe = 1.60217646e-19
    Na = 6.0221415e23
    E_0 = 8.854187818e-12
    cal2J = 4.184 

    index = arange(N, dtype=float) + 0.5

    k1 = special.kv(index, kappa*r1)*sqrt(pi/(2*kappa*r1))
    k2 = special.kv(index, kappa*r2)*sqrt(pi/(2*kappa*r2))

    i1 = special.iv(index, kappa*r1)*sqrt(pi/(2*kappa*r1))
    i2 = special.iv(index, kappa*r2)*sqrt(pi/(2*kappa*r2))

    B = zeros((N,N), dtype=float)

    for n in range(N):
        for m in range(N):
            for nu in range(N):
                if n>=nu and m>=nu:
                    g1 = gamma(n-nu+0.5)
                    g2 = gamma(m-nu+0.5)
                    g3 = gamma(nu+0.5)
                    g4 = gamma(m+n-nu+1.5)
                    f1 = factorial(n+m-nu)
                    f2 = factorial(n-nu)
                    f3 = factorial(m-nu)
                    f4 = factorial(nu)
                    Anm = g1*g2*g3*f1*(n+m-2*nu+0.5)/(pi*g4*f2*f3*f4)
                    kB = special.kv(n+m-2*nu+0.5,kappa*R)*sqrt(pi/(2*kappa*R))
                    B[n,m] += Anm*kB 

    M = zeros((N,N), float)
    for i in range(N):
        for j in range(N):
            M[i,j] = (2*i+1)*B[i,j]*i1[i]
            if i==j:
                M[i,j] += k1[i]

    RHS = zeros(N)
    RHS[0] = phi01

    a = solve(M,RHS)

    a0 = a[0] 
   
    U = 4*pi * ( -pi/2 * a0/phi01 * 1/sinh(kappa*r1) + kappa*r1 + kappa*r1/tanh(kappa*r1) )

#    print 'E: %f'%U
    C0 = qe**2*Na*1e-3*1e10/(cal2J*E_0)
    C1 = r1*epsilon*phi01*phi01
    E_inter = U*C1*C0
                            
    return E_inter

def constant_charge_twosphere_identical(sigma, a, R, kappa, epsilon):
#   From Carnie+Chan 1993

    N = 10 # Number of terms in expansion
    E_p = 0 # Permitivitty inside sphere
    
    qe = 1.60217646e-19
    Na = 6.0221415e23
    E_0 = 8.854187818e-12
    cal2J = 4.184 

    index2 = arange(N+1, dtype=float) + 0.5
    index  = index2[0:-1]

    K1 = special.kv(index2, kappa*a)
    K1p = index/(kappa*a)*K1[0:-1] - K1[1:]
    
    k1 = special.kv(index, kappa*a)*sqrt(pi/(2*kappa*a))
    k1p = -sqrt(pi/2)*1/(2*(kappa*a)**(3/2.))*special.kv(index, kappa*a) + sqrt(pi/(2*kappa*a))*K1p

    I1 = special.iv(index2, kappa*a)
    I1p = index/(kappa*a)*I1[0:-1] + I1[1:]
    i1 = special.iv(index, kappa*a)*sqrt(pi/(2*kappa*a))
    i1p = -sqrt(pi/2)*1/(2*(kappa*a)**(3/2.))*special.iv(index, kappa*a) + sqrt(pi/(2*kappa*a))*I1p


    B = zeros((N,N), dtype=float)

    for n in range(N):
        for m in range(N):
            for nu in range(N):
                if n>=nu and m>=nu:
                    g1 = gamma(n-nu+0.5)
                    g2 = gamma(m-nu+0.5)
                    g3 = gamma(nu+0.5)
                    g4 = gamma(m+n-nu+1.5)
                    f1 = factorial(n+m-nu)
                    f2 = factorial(n-nu)
                    f3 = factorial(m-nu)
                    f4 = factorial(nu)
                    Anm = g1*g2*g3*f1*(n+m-2*nu+0.5)/(pi*g4*f2*f3*f4)
                    kB = special.kv(n+m-2*nu+0.5,kappa*R)*sqrt(pi/(2*kappa*R))
                    B[n,m] += Anm*kB 

    M = zeros((N,N), float)
    for i in range(N):
        for j in range(N):
            M[i,j] = (2*i+1)*B[i,j]*(E_p/epsilon*i*i1[i] - a*kappa*i1p[i])
            if i==j:
                M[i,j] += (E_p/epsilon*i*k1[i] - a*kappa*k1p[i])

    RHS = zeros(N)
    RHS[0] = a*sigma/epsilon

    a_coeff = solve(M,RHS)

    a0 = a_coeff[0] 
   
    C0 = a*sigma/epsilon
    CC0 = qe**2*Na*1e-3*1e10/(cal2J*E_0)
    
    E_inter = 4*pi*a*epsilon*C0*C0*CC0( pi*a0/(2*C0*(kappa*a*cosh(kappa*a)-sinh(kappa*a))) - 1/(1+kappa*a) - 1/(kappa*a*1/tanh(kappa*a)-1) )

    return E_inter



'''
r1 = 1.
phi01 = 1.
r2 = 2.
phi02 = 2.

R = 5

kappa = 0.1
epsilon = 80.

E_inter = constant_potential_twosphere(phi01, phi02, r1, r2, R, kappa, epsilon)
print E_inter
'''

'''
q   = array([1.60217646e-19])
xq  = array([[1e-10,1e-10,0.]])
E_1 = 4.
E_2 = 80.
E_0 = 8.854187818e-12
R   = 1.
N   = 10
Q   = 1
Na  = 6.0221415e23
a   = R
kappa = 0.125

#PHI_sph = an_spherical(q, xq, E_1, E_2, E_0, R, N)
PHI_P = an_P(q, xq, E_1, E_2, E_0, R, kappa, a, N)

JtoCal = 4.184    
#E_solv_sph = 0.5*sum(q*PHI_sph)*Na*1e7/JtoCal
E_solv_P = 0.5*sum(q*PHI_P)*Na*1e7/JtoCal
#print 'With spherical harmonics: %f'%E_solv_sph
print 'With Legendre functions : %f'%E_solv_P
'''
