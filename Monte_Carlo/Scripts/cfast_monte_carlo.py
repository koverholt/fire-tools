#!/usr/bin/env python

"""
Run CFAST Monte Carlo Simulation

Case 1: Only model bias/uncertainty
Case 2: Only input uncertainty
Case 3: Combined model bias/uncertainty and input uncertainty
"""

import numpy as np
import external_cfast

#  =====================
#  = BEGIN USER INPUTS =
#  =====================

#  ==========================
#  = Monte Carlo parameters =
#  ==========================

# Number of Monte Carlo iterations to run
mc_iterations = 100

### Gamma distribution parameters for HRR ###
# NUREG 6850, Volume 2, Table G-1
# Vertical cabinets w/ unqualified cable, more than one bundle, open doors
# HRR (75th percentile): 232 kW
# HRR (98th percentile): 1002 kW
hrr_gamma_parameters = np.array([0.46, 386])

# HRR point estimate, kW
hrr_point = 1002

#  ====================
#  = Fixed parameters =
#  ====================

# x, y, z compartment dimensions, m
x = 26.5
y = 18.5
z = 6.1

# Ambient temperature, C
tmp_a = 20

# Simulation time and data dump frequency, s
simulation_time = 3600
dt_data = 10

# Gas phase heat of combustion, kJ/kg
hoc = 20900

# Wall material
wall = 'concrete'

#  ================================
#  = Model Bias and Uncertainty   =
#  = from NUREG 1824 Supplement 1 =
#  ================================

# HGL Temperature Rise, Forced Ventilation (CFAST)
delta = 1.15
sigma_m = 0.20

#  ==============
#  = File Paths =
#  ==============

results_dir = '../Model_Output/'

#  ======================
#  = END OF USER INPUTS =
#  ======================

#  =====================
#  = Varied parameters =
#  =====================

# Fixed value          - np.repeat(value, size)
# Uniform distribution - np.random.uniform(lower, upper, size)
# Normal distribution  - np.random.normal(mean, std, size)
# Gamma distribution   - np.random.gamma(shape, scale, size)

# Initialize input parameter distribution
hrr_distribution = np.random.gamma(hrr_gamma_parameters[0],
                                   hrr_gamma_parameters[1],
                                   mc_iterations)

#  =====================
#  = Single simulation =
#  =      Case 1       =
#  =====================

### For Case 1 ###
# Time and HRR ramp, s, kW
time_ramp = np.array([0, simulation_time])
hrr_ramp = np.array([hrr_point, hrr_point])
hgl_temp_point = external_cfast.run_case(x=x, y=y, z=z,
                                       hoc=hoc,
                                       tmp_a=tmp_a,
                                       time_ramp=time_ramp,
                                       hrr_ramp=hrr_ramp,
                                       wall=wall,
                                       simulation_time=simulation_time,
                                       dt_data=dt_data)

# Case 1 - Adjust for model bias and uncertainty
hgl_temp_rise = (hgl_temp_point - tmp_a)
mu_point = (hgl_temp_rise / delta) + tmp_a
sigma_point = sigma_m * hgl_temp_rise / delta

#  ==========================
#  = Monte Carlo simulation =
#  =     Cases 2 and 3      =
#  ==========================

output_hgl_temps = np.array([])
output_hgl_temps_adjusted = np.array([])

for i in range(mc_iterations):
    # Time and HRR ramp, s, kW
    time_ramp = np.array([0, simulation_time])
    hrr_ramp = np.array([hrr_distribution[i], hrr_distribution[i]])
    
    hgl_temp = external_cfast.run_case(x=x, y=y, z=z,
                                       hoc=hoc,
                                       tmp_a=tmp_a,
                                       time_ramp=time_ramp,
                                       hrr_ramp=hrr_ramp,
                                       wall=wall,
                                       simulation_time=simulation_time,
                                       dt_data=dt_data)

    # Case 2 - only input uncertainty
    output_hgl_temps = np.append(hgl_temp, output_hgl_temps)

    # Case 3 - Adjust for model bias and uncertainty
    hgl_temp_rise = (hgl_temp - tmp_a)
    # Set zero temperature rise to small number to avoid problems
    if hgl_temp_rise == 0:
      hgl_temp_rise = 0.0001
    mu_star = (hgl_temp_rise / delta) + tmp_a
    sigma_star = sigma_m * hgl_temp_rise / delta
    hgl_temp_adjusted = np.random.normal(mu_star, sigma_star)
    output_hgl_temps_adjusted = np.append(hgl_temp_adjusted,
                                          output_hgl_temps_adjusted)

#  ======================
#  = Write data to disk =
#  ======================

np.savetxt(results_dir + 'mu_point.txt.gz',
           np.array([mu_point]),
           fmt='%0.2f')

np.savetxt(results_dir + 'sigma_point.txt.gz',
           np.array([sigma_point]),
           fmt='%0.2f')

np.savetxt(results_dir + 'hrr_point.txt.gz',
           np.array([hrr_point]),
           fmt='%0.2f')

np.savetxt(results_dir + 'hrr_distribution.txt.gz',
           hrr_distribution,
           fmt='%0.2f')

np.savetxt(results_dir + 'output_hgl_temps.txt.gz',
           output_hgl_temps,
           fmt='%0.2f')

np.savetxt(results_dir + 'output_hgl_temps_adjusted.txt.gz',
           output_hgl_temps_adjusted,
           fmt='%0.2f')

