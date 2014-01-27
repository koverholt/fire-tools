#!/usr/bin/env python

from __future__ import division

import matplotlib
matplotlib.use("Agg")

import numpy as np
from pylab import *

# Read in exp. data for each test
fds = np.genfromtxt('FDS_Files/heat_flux_devc.csv', delimiter=',', names=True, skip_header=1)

fig = figure()
plot(fds['Time'], fds['INERTNET'], 'k-', marker='o', lw=2, label='Net Heat Flux', markevery=1)
plot(fds['Time'], fds['INERTCONV'], 'r-', marker='^', lw=2, label='Convective Heat Flux', markevery=7)
plot(fds['Time'], fds['INERTRAD'], 'g-', marker='d', lw=2, label='Radiative Heat Flux', markevery=5)
plot(fds['Time'], fds['INERTINC'], 'b-', marker='s', lw=2, label='Incident Heat Flux', markevery=7)
plot(fds['Time'], fds['INERTGAUGE'], 'c-', marker='v', lw=2, label='Gauge Heat Flux', markevery=9)
plot(fds['Time'], fds['INERTRADIO'], 'm-', marker='*', lw=2, label='Radiometer', markevery=11)
ylim([-1, 30])
xlabel('Time (s)', fontsize=20)
ylabel('Heat Flux (kW/m$^2$)', fontsize=20)
grid(True)
xticks(fontsize=16)
yticks(fontsize=16)
legend(loc=0)
savefig('Figures/heat_flux_inert.png')

fig = figure()
plot(fds['Time'], fds['GYPSUMNET'], 'k-', marker='o', lw=2, label='Net Heat Flux', markevery=1)
plot(fds['Time'], fds['GYPSUMCONV'], 'r-', marker='^', lw=2, label='Convective Heat Flux', markevery=7)
plot(fds['Time'], fds['GYPSUMRAD'], 'g-', marker='d', lw=2, label='Radiative Heat Flux', markevery=5)
plot(fds['Time'], fds['GYPSUMINC'], 'b-', marker='s', lw=2, label='Incident Heat Flux', markevery=7)
plot(fds['Time'], fds['GYPSUMGAUGE'], 'c-', marker='v', lw=2, label='Gauge Heat Flux', markevery=9)
plot(fds['Time'], fds['GYPSUMRADIO'], 'm-', marker='*', lw=2, label='Radiometer', markevery=11)
xlabel('Time (s)', fontsize=20)
ylabel('Heat Flux (kW/m$^2$)', fontsize=20)
ylim([-1, 30])
grid(True)
xticks(fontsize=16)
yticks(fontsize=16)
legend(loc=0)
savefig('Figures/heat_flux_gypsum.png')

