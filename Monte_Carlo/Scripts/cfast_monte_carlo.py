#!/usr/bin/env python

"""
Run CFAST Monte Carlo Simulation

Case 1: Only model bias/uncertainty
Case 2: Only input uncertainty
Case 3: Combined model bias/uncertainty and input uncertainty
"""

import matplotlib
matplotlib.use("Agg")
from pylab import *

import numpy as np
import scipy as sp
from scipy import stats
import external_cfast

np.set_printoptions(precision=0)

#  =====================
#  = BEGIN USER INPUTS =
#  =====================

#  ==========================
#  = Monte Carlo parameters =
#  ==========================

# Number of Monte Carlo iterations to run
mc_iterations = 10000

# Nominal HRR, kW
hrr = 500

# +/- percent to vary HRR
variation = 0.20

# Threshold HGL temperature for probability calculation, degrees C
threshold_hgl_temp = 100

#  ====================
#  = Plotting options =
#  ====================

# Number of bins to use in PDF/CDF plots
histogram_bins = 50

# Upper y-axis limit for PDF plots
y_pdf_upper = 0.05

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

#  ======================
#  = END OF USER INPUTS =
#  ======================

#  =====================
#  = Varied parameters =
#  =====================

# Fixed value          - np.repeat(value, size)
# Uniform distribution - np.random.uniform(lower, upper, size)
# Normal distribution  - np.random.normal(mean, std, size)

# Initialize point value and parameter distribution
hrr_lower = hrr - (hrr * variation)
hrr_upper = hrr + (hrr * variation)
hrr_point = hrr
hrr_uniform = np.random.uniform(hrr_lower, hrr_upper, mc_iterations)

#  ============================
#  = Plot input distributions =
#  ============================

figure()
hist(hrr_uniform, bins=histogram_bins, normed=1)
xlabel('HRR (kW)', fontsize=20)
ylabel('PDF', fontsize=20)
grid(True)
ax = gca()
for xlabel_i in ax.get_xticklabels():
    xlabel_i.set_fontsize(16)
for ylabel_i in ax.get_yticklabels():
    ylabel_i.set_fontsize(16)
gcf().subplots_adjust(left=0.15, bottom=0.11)
savefig('../Figures/input_PDF.pdf')

figure()
hist(hrr_uniform, bins=histogram_bins, normed=1, histtype='step', cumulative=True)
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
savefig('../Figures/input_CDF.pdf')

#  =====================
#  = Single simulation =
#  =      Case 1       =
#  =====================

### For Case 1 ###
# Time and HRR ramp, s, kW
time_ramp = np.array([0, simulation_time])
hrr_ramp = np.array([hrr, hrr])
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
    hrr_ramp = np.array([hrr_uniform[i], hrr_uniform[i]])
    
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
    mu_star = (hgl_temp_rise / delta) + tmp_a
    sigma_star = sigma_m * hgl_temp_rise / delta
    hgl_temp_adjusted = np.random.normal(mu_star, sigma_star)
    output_hgl_temps_adjusted = np.append(hgl_temp_adjusted,
                                          output_hgl_temps_adjusted)

#  =============================
#  = Plot output distributions =
#  =============================

# Initialize plotting variables
lower = mu_point - 4*sigma_point
upper = mu_point + 4*sigma_point
case1_range = np.arange(lower, upper, 0.001)

figure()
plot(case1_range, sp.stats.norm.pdf(case1_range, mu_point, sigma_point))
xlabel(r'HGL Temperature ($^\circ$C)', fontsize=20)
ylabel('PDF', fontsize=20)
grid(True)
xlim([lower, upper])
ylim([0, y_pdf_upper])
ax = gca()
for xlabel_i in ax.get_xticklabels():
    xlabel_i.set_fontsize(16)
for ylabel_i in ax.get_yticklabels():
    ylabel_i.set_fontsize(16)
gcf().subplots_adjust(left=0.15, bottom=0.11)
savefig('../Figures/output_PDF_1_model.pdf')

figure()
hist(output_hgl_temps, bins=histogram_bins, normed=1)
xlabel(r'HGL Temperature ($^\circ$C)', fontsize=20)
ylabel('PDF', fontsize=20)
grid(True)
xlim([lower, upper])
ax = gca()
for xlabel_i in ax.get_xticklabels():
    xlabel_i.set_fontsize(16)
for ylabel_i in ax.get_yticklabels():
    ylabel_i.set_fontsize(16)
gcf().subplots_adjust(left=0.15, bottom=0.11)
savefig('../Figures/output_PDF_2_input.pdf')

figure()
hist(output_hgl_temps_adjusted, bins=histogram_bins, normed=1)
xlabel(r'HGL Temperature ($^\circ$C)', fontsize=20)
ylabel('PDF', fontsize=20)
grid(True)
xlim([lower, upper])
ylim([0, y_pdf_upper])
ax = gca()
for xlabel_i in ax.get_xticklabels():
    xlabel_i.set_fontsize(16)
for ylabel_i in ax.get_yticklabels():
    ylabel_i.set_fontsize(16)
gcf().subplots_adjust(left=0.15, bottom=0.11)
savefig('../Figures/output_PDF_3_combined.pdf')

figure()
plot(case1_range, sp.stats.norm.cdf(case1_range, mu_point, sigma_point))
xlabel(r'HGL Temperature ($^\circ$C)', fontsize=20)
ylabel('CDF', fontsize=20)
ylim([0, 1])
grid(True)
xlim([lower, upper])
ax = gca()
for xlabel_i in ax.get_xticklabels():
    xlabel_i.set_fontsize(16)
for ylabel_i in ax.get_yticklabels():
    ylabel_i.set_fontsize(16)
gcf().subplots_adjust(left=0.15, bottom=0.11)
savefig('../Figures/output_CDF_1_model.pdf')

figure()
hist(output_hgl_temps, bins=histogram_bins,
     normed=1, histtype='step', cumulative=True)
xlabel(r'HGL Temperature ($^\circ$C)', fontsize=20)
ylabel('CDF', fontsize=20)
ylim([0, 1])
grid(True)
xlim([lower, upper])
ax = gca()
for xlabel_i in ax.get_xticklabels():
    xlabel_i.set_fontsize(16)
for ylabel_i in ax.get_yticklabels():
    ylabel_i.set_fontsize(16)
gcf().subplots_adjust(left=0.15, bottom=0.11)
savefig('../Figures/output_CDF_2_input.pdf')

figure()
hist(output_hgl_temps_adjusted,
     bins=histogram_bins, normed=1, histtype='step', cumulative=True)
xlabel(r'HGL Temperature ($^\circ$C)', fontsize=20)
ylabel('CDF', fontsize=20)
ylim([0, 1])
grid(True)
xlim([lower, upper])
ax = gca()
for xlabel_i in ax.get_xticklabels():
    xlabel_i.set_fontsize(16)
for ylabel_i in ax.get_yticklabels():
    ylabel_i.set_fontsize(16)
gcf().subplots_adjust(left=0.15, bottom=0.11)
savefig('../Figures/output_CDF_3_combined.pdf')

#  =================
#  = Print results =
#  =================

print 'Mean HGL Temperature (Case 1):'
print mu_point
print 'Std. Dev. HGL Temperature (Case 1):'
print sigma_point
print
print 'HGL Temperatures (Case 2):'
print output_hgl_temps
print
print 'Minimum, Median, Mean, and Maximum HGL Temperatures:'
print np.array([np.min(output_hgl_temps), np.median(output_hgl_temps),
                np.mean(output_hgl_temps), np.max(output_hgl_temps)])
print
print 'HGL Temperatures (Case 3):'
print output_hgl_temps_adjusted
print
print 'Adjusted Minimum, Median, Mean, and Maximum HGL Temperatures:'
print np.array([np.min(output_hgl_temps_adjusted),
                np.median(output_hgl_temps_adjusted),
                np.mean(output_hgl_temps_adjusted),
                np.max(output_hgl_temps_adjusted)])
print
print 'Probability of exceeding threshold temperature.'
print 'Case 1 (Only model bias/uncertainty):'
print 0.5 * sp.special.erfc(
                (threshold_hgl_temp - mu_point) / (sigma_point * np.sqrt(2)))
print
print 'Case 2 (Only input uncertainty):'
print (100 - sp.stats.percentileofscore(
                 output_hgl_temps, threshold_hgl_temp)) / 100
print
print 'Case 3 (Combined model bias/uncertainty and input uncertainty):'
print (100 - sp.stats.percentileofscore(
                 output_hgl_temps_adjusted, threshold_hgl_temp)) / 100
