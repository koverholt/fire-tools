#!/usr/bin/env python

"""Run CFAST Monte Carlo Simulation"""

import numpy as np
from pylab import *
import external_cfast

np.set_printoptions(precision=0)

#  ==========================
#  = Monte Carlo parameters =
#  ==========================

mc_iterations = 20

#  =====================
#  = Varied parameters =
#  =====================

# Fixed value          - np.repeat(value, size)
# Uniform distribution - np.random.uniform(lower, upper, size)
# Normal distribution  - np.random.normal(mean, std, size)

# x, y, z compartment dimensions, m
x = np.repeat(26.5, mc_iterations)
y = np.repeat(18.5, mc_iterations)
z = np.repeat(6.1, mc_iterations)

# Gas phase heat of combustion, kJ/kg
hoc = np.repeat(20900, mc_iterations)

# Fire size, kW
hrr = np.random.normal(500, 50, mc_iterations)

#  ====================
#  = Fixed parameters =
#  ====================

# Ambient temperature, C
tmp_a = 20

# Simulation time and data dump frequency, s
simulation_time = 3600
dt_data = 10

# Wall material
wall = 'concrete'

#  ============================
#  = Plot input distributions =
#  ============================

figure()
hist(hrr, bins=20, normed=1)
xlabel('HRR (kW)', fontsize=20)
ylabel('PDF', fontsize=20)
grid(True)
ax = gca()
for xlabel_i in ax.get_xticklabels():
    xlabel_i.set_fontsize(16)
for ylabel_i in ax.get_yticklabels():
    ylabel_i.set_fontsize(16)
gcf().subplots_adjust(left=0.15, bottom=0.11)
savefig('../Figures/input_hrr_PDF.pdf')

figure()
hist(hrr, bins=20, normed=1, histtype='step', cumulative=True)
xlabel('HRR (kW)', fontsize=20)
ylabel('CDF', fontsize=20)
ylim([0, 1])
grid(True)
ax = gca()
for xlabel_i in ax.get_xticklabels():
    xlabel_i.set_fontsize(16)
for ylabel_i in ax.get_yticklabels():
    ylabel_i.set_fontsize(16)
gcf().subplots_adjust(left=0.15, bottom=0.11)
savefig('../Figures/input_hrr_CDF.pdf')

#  ==========================
#  = Monte Carlo simulation =
#  ==========================

output_hgl_temps = np.array([])

for i in range(mc_iterations):

    # Time and HRR ramp, s, kW
    time_ramp = np.array([0, simulation_time])
    hrr_ramp = np.array([hrr[i], hrr[i]])
    
    hgl_temp = external_cfast.run_case(x=x[i], y=y[i], z=z[i],
                                       hoc=hoc[i],
                                       tmp_a=tmp_a,
                                       time_ramp=time_ramp,
                                       hrr_ramp=hrr_ramp,
                                       wall=wall,
                                       simulation_time=simulation_time,
                                       dt_data=dt_data)
    output_hgl_temps = np.append(hgl_temp, output_hgl_temps)

#  =============================
#  = Plot output distributions =
#  =============================

figure()
hist(output_hgl_temps, bins=20, normed=1)
xlabel(r'HGL Temperature ($^\circ$C)', fontsize=20)
ylabel('PDF', fontsize=20)
grid(True)
ax = gca()
for xlabel_i in ax.get_xticklabels():
    xlabel_i.set_fontsize(16)
for ylabel_i in ax.get_yticklabels():
    ylabel_i.set_fontsize(16)
gcf().subplots_adjust(left=0.15, bottom=0.11)
savefig('../Figures/output_hgl_temps_PDF.pdf')

figure()
hist(output_hgl_temps, bins=20, normed=1, histtype='step', cumulative=True)
xlabel(r'HGL Temperature ($^\circ$C)', fontsize=20)
ylabel('CDF', fontsize=20)
ylim([0, 1])
grid(True)
ax = gca()
for xlabel_i in ax.get_xticklabels():
    xlabel_i.set_fontsize(16)
for ylabel_i in ax.get_yticklabels():
    ylabel_i.set_fontsize(16)
gcf().subplots_adjust(left=0.15, bottom=0.11)
savefig('../Figures/output_hgl_temps_CDF.pdf')

#  =================
#  = Print results =
#  =================

print 'HGL Temperatures:'
print output_hgl_temps
print
print 'Minimum, Median, Mean, and Maximum HGL Temperatures:'
print np.array([np.min(output_hgl_temps), np.median(output_hgl_temps), np.mean(output_hgl_temps), np.max(output_hgl_temps)])

