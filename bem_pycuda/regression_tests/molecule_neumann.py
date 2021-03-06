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

import os
import numpy
from matplotlib import *
from matplotlib.pyplot import *
from matplotlib.backends.backend_pdf import PdfFile, PdfPages, FigureCanvasPdf
import sys
import math
sys.path.append('../util')
from an_solution import *

def scanOutput(filename):
    
    flag = 0
    for line in file(filename):
        line = line.split()
        if len(line)>0:
            if line[0]=='Converged':
                iterations = int(line[2])
            if line[0]=='Total' and line[1]=='elements':
                N = int(line[-1])
            if line[0]=='Totals:':
                flag = 1
            if line[0]=='Esolv' and flag==1:
                Esolv = float(line[2])
            if line[0]=='Esurf' and flag==1:
                Esurf = float(line[2])
            if line[0]=='Ecoul' and flag==1:
                Ecoul = float(line[2])
            if line[0]=='Time' and flag==1:
                Time = float(line[2])

    return N, iterations, Esolv, Esurf, Ecoul, Time
            

mesh = numpy.array(['500','2K','8K','32K','130K'])

comm = './main.py regression_tests/input_files/sphere_fine.param regression_tests/input_files/molecule_neumann_'
out = 'regression_tests/output_aux'

print 'Runs for molecule + set phi/dphi surface'
N = numpy.zeros(len(mesh))
iterations = numpy.zeros(len(mesh))
Esolv = numpy.zeros(len(mesh))
Esurf = numpy.zeros(len(mesh))
Ecoul = numpy.zeros(len(mesh))
Time = numpy.zeros(len(mesh))
for i in range(len(mesh)):
    print 'Start run for mesh '+mesh[i]
    cmd = comm + mesh[i] + '.config > ' + out
    os.system(cmd)
    print 'Scan output file'
    N[i],iterations[i],Esolv[i],Esurf[i],Ecoul[i],Time[i] = scanOutput(out)
    

print 'Runs for isolated molecule'

comm = './main.py regression_tests/input_files/sphere_fine.param regression_tests/input_files/molecule_single_center_'
out = 'regression_tests/output_aux'

N_mol = numpy.zeros(len(mesh))
iterations_mol = numpy.zeros(len(mesh))
Esolv_mol = numpy.zeros(len(mesh))
Esurf_mol = numpy.zeros(len(mesh))
Ecoul_mol = numpy.zeros(len(mesh))
Time_mol = numpy.zeros(len(mesh))
for i in range(len(mesh)):
    print 'Start run for mesh '+mesh[i]
    cmd = comm + mesh[i] + '.config > ' + out 
    os.system(cmd)
    print 'Scan output file'
    N_mol[i],iterations_mol[i],Esolv_mol[i],Esurf_mol[i],Ecoul_mol[i],Time_mol[i] = scanOutput(out)


print 'Runs for isolated surface'

comm = './main.py regression_tests/input_files/sphere_fine.param regression_tests/input_files/neumann_surface'
out = 'regression_tests/output_aux'

N_surf = numpy.zeros(len(mesh))
iterations_surf = numpy.zeros(len(mesh))
Esolv_surf = numpy.zeros(len(mesh))
Esurf_surf = numpy.zeros(len(mesh))
Ecoul_surf = numpy.zeros(len(mesh))
Time_surf = numpy.zeros(len(mesh))
for i in range(len(mesh)):
    print 'Start run for mesh '+mesh[i]
    cmd = comm + mesh[i] + '.config > ' + out
    os.system(cmd)
    print 'Scan output file'
    N_surf[i],iterations_surf[i],Esolv_surf[i],Esurf_surf[i],Ecoul_surf[i],Time_surf[i] = scanOutput(out)

Einter = Esolv + Esurf + Ecoul - Esolv_surf - Esurf_mol - Ecoul_mol - Esolv_mol - Esurf_surf - Ecoul_surf
total_time = Time+Time_mol+Time_surf

analytical = molecule_constant_charge(1., -80*1., 5., 4., 12., 0.125, 4., 80.)  

error = abs(Einter-analytical)/abs(analytical)

print '\nNumber of elements : '+str(N)
print 'Number of iteration: '+str(iterations)
print 'Interaction energy : '+str(Einter)
print 'Analytical solution: %f kcal/mol'%analytical
print 'Error              : '+str(error)
print 'Total time         : '+str(total_time)


flag = 0
for i in range(len(error)-1):
    rate = error[i]/error[i+1]
    if abs(rate-4)>0.6:
        flag = 1
        print 'Bad convergence for mesh %i to %i, with rate %f'%(i,i+1,rate)

if flag==0:
    print '\nPassed convergence test!'


font = {'family':'serif','size':10}
fig = Figure(figsize=(3,2), dpi=80)
ax = fig.add_subplot(111)
asymp = N[0]*error[0]/N
ax.loglog(N, error, c='k', marker='o',ls=' ', mfc='w', ms=5, label='')
ax.loglog(N, asymp, c='k', marker='None', ls=':', lw=0.8, label=None)
rc('font',**font)
loc = (3*N[0]+N[1])/4
tex_loc = array((loc,N[0]*error[0]/loc))
tex_angle = math.atan2(log(abs(asymp[-1]-asymp[0])),log(abs(N[-1]-N[0])))*180/math.pi
ax.text(tex_loc[0], tex_loc[1],r'N$^{-1}$',fontsize=8,rotation=tex_angle,rotation_mode='anchor')
ax.set_ylabel('Relative error', fontsize=10)
ax.set_xlabel('Number of elements', fontsize=10)
fig.subplots_adjust(left=0.185, bottom=0.21, right=0.965, top=0.95)
canvas = FigureCanvasPdf(fig)
canvas.print_figure('regression_tests/figs/error_energy_molecule_neumann.pdf',dpi=80)

fig = Figure(figsize=(3,2), dpi=80)
ax = fig.add_subplot(111)
asymp = N*log(N)*total_time[0]/(N[0]*log(N[0]))
ax.loglog(N, total_time, c='k', marker='o',ls=' ', mfc='w', ms=5, label='')
ax.loglog(N, asymp,c='k',marker='None',ls=':', lw=0.8, label=None)
loc = (3*N[0]+N[1])/4
tex_loc = array((loc, loc*log(loc)*total_time[0]/(N[0]*log(N[0]))))
tex_angle = math.atan2(log(abs(asymp[-1]-asymp[0])),log(abs(N[-1]-N[0])))*180/math.pi
ax.text(tex_loc[0], tex_loc[1], 'NlogN', fontsize=8,rotation=tex_angle, rotation_mode='anchor')
rc('font',**font)
ax.set_ylabel('Total time [s]', fontsize=10)
ax.set_xlabel('Number of elements', fontsize=10)
fig.subplots_adjust(left=0.185, bottom=0.21, right=0.965, top=0.95)
canvas = FigureCanvasPdf(fig)
canvas.print_figure('regression_tests/figs/total_time_molecule_neumann.pdf',dpi=80)

fig = Figure(figsize=(3,2), dpi=80)
ax = fig.add_subplot(111)
ax.semilogx(N, iterations, c='k', marker='o',ls=' ', mfc='w', ms=5, label='')
rc('font',**font)
ax.set_ylabel('Iterations', fontsize=10)
ax.set_xlabel('Number of elements', fontsize=10)
fig.subplots_adjust(left=0.185, bottom=0.21, right=0.965, top=0.95)
canvas = FigureCanvasPdf(fig)
canvas.print_figure('regression_tests/figs/iterations_molecule_neumann.pdf',dpi=80)
