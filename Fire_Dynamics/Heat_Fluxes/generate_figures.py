#!/usr/bin/env python

from __future__ import division

import matplotlib
matplotlib.use("Agg")

import numpy as np
from pylab import *

# Read in exp. data for each test
fds = np.genfromtxt('FDS_Files/heat_flux_devc.csv', delimiter=',', names=True, skip_header=1)

fig = figure()
plot(fds['Time'], fds['INERTNET'], label='Net Heat Flux')
plot(fds['Time'], fds['INERTCONV'], label='Convective Heat Flux')
plot(fds['Time'], fds['INERTRAD'], label='Radiative Heat Flux')
plot(fds['Time'], fds['INERTINC'], label='Incident Heat Flux')
plot(fds['Time'], fds['INERTGAUGE'], label='Gauge Heat Flux')
plot(fds['Time'], fds['INERTRADIO'], label='Radiometer')
ylim([-1, 25])
xlabel('Time (s)', fontsize=20)
ylabel('Heat Flux (kW/m$^2$)', fontsize=20)
grid(True)
xticks(fontsize=16)
yticks(fontsize=16)
legend(loc=0)
savefig('Figures/heat_flux_inert.pdf')

fig = figure()
plot(fds['Time'], fds['GYPSUMNET'], label='Net Heat Flux')
plot(fds['Time'], fds['GYPSUMCONV'], label='Convective Heat Flux')
plot(fds['Time'], fds['GYPSUMRAD'], label='Radiative Heat Flux')
plot(fds['Time'], fds['GYPSUMINC'], label='Incident Heat Flux')
plot(fds['Time'], fds['GYPSUMGAUGE'], label='Gauge Heat Flux')
plot(fds['Time'], fds['GYPSUMRADIO'], label='Radiometer')
xlabel('Time (s)', fontsize=20)
ylabel('Heat Flux (kW/m$^2$)', fontsize=20)
ylim([-1, 25])
grid(True)
xticks(fontsize=16)
yticks(fontsize=16)
legend(loc=0)
savefig('Figures/heat_flux_gypsum.pdf')