#!/usr/bin/env python

"""Run CFAST Monte Carlo Simulation"""

import numpy as np
import external_cfast

#  ==========================
#  = Monte Carlo parameters =
#  ==========================

mc_iterations = 10

#  =====================
#  = Varied parameters =
#  =====================

# Uniform distribution - np.random.uniform(lower, upper, size)
# Normal distribution - np.random.normal(mean, std, size)

# x, y, z compartment dimensions, m
x = np.random.uniform(2, 3, mc_iterations)
y = np.random.uniform(2, 3, mc_iterations)
z = np.random.uniform(2, 3, mc_iterations)

# Door height and width, m
door_height = np.random.uniform(1, 2, mc_iterations)
door_width = np.random.uniform(0.3, 1, mc_iterations)

# Gas phase heat of combustion, kJ/kg
HoC = np.random.normal(50000, 5000, mc_iterations)

# Fire size, kW
fire_size = np.random.normal(500, 50, mc_iterations)

#  ====================
#  = Fixed parameters =
#  ====================

# Ambient temperature, C
tmp_a = 20

# Simulation time and data dump frequency, s
simulation_time = 1800
dt_data = 10

# number index (ID) of fire in CFAST, 1 for a single fire
num = 1

# status of door, 'Open' or 'Closed'
door = 'Open'

# Wall material
wall = 'gypsum'

#  ============================
#  = Plot input distributions =
#  ============================

#  ==========================
#  = Monte Carlo simulation =
#  ==========================

output_hgl_temps = np.array([])

for i in range(mc_iterations):

    # Time and HRR ramp, s, kW
    time_ramp = np.array([0, simulation_time])
    hrr_ramp = np.array([fire_size[i], fire_size[i]])
    
    hgl_temp = external_cfast.run_case(x=x[i], y=y[i], z=z[i],
                                       door_height=door_height[i],
                                       door_width=door_width[i],
                                       HoC=HoC[i],
                                       tmp_a=tmp_a,
                                       time_ramp=time_ramp,
                                       hrr_ramp=hrr_ramp,
                                       num=num,
                                       door=door,
                                       wall=wall,
                                       simulation_time=simulation_time,
                                       dt_data=dt_data)
    output_hgl_temps = np.append(hgl_temp, output_hgl_temps)

#  =============================
#  = Plot output distributions =
#  =============================

#  =================
#  = Print results =
#  =================

print 'HGL Temperatures:'
print output_hgl_temps
print
print 'Minimum HGL Temperature:'
print np.min(output_hgl_temps)
print
print 'Maximum HGL Temperature:'
print np.max(output_hgl_temps)
print
print 'Mean HGL Temperature:'
print np.mean(output_hgl_temps)

