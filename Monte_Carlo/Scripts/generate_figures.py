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

np.set_printoptions(precision=0)

#  =====================
#  = BEGIN USER INPUTS =
#  =====================

#  =======================
#  = Analysis parameters =
#  =======================

### Gamma distribution parameters for HRR ###
# NUREG 6850, Volume 2, Table G-1
# Vertical cabinets w/ unqualified cable, more than one bundle, open doors
# HRR (75th percentile): 232 kW
# HRR (98th percentile): 1002 kW
hrr_gamma_parameters = np.array([0.46, 386])

# Threshold HGL temperature for probability calculation, degrees C
threshold_hgl_temp = 100

#  ====================
#  = Plotting options =
#  ====================

# Upper and lower HRR bounds for plots
hrr_lower = 0
hrr_upper = 1200

# Number of bins to use in PDF/CDF plots
histogram_bins = 1000

# x-axis and y-axis limits for input/ouput PDF/CDF plots
x_upper_input = 2000
y_upper_input = 0.01
x_upper_output = 150
y_upper_output = 0.12

# Font size
font_size = 16

#  ==============
#  = File Paths =
#  ==============

results_dir = '../Model_Output/'

figures_dir = '../Figures/'

#  =====================
#  = END USER INPUTS =
#  =====================

#  =======================
#  = Read data from disk =
#  =======================

mu_point = np.loadtxt(
        results_dir + 'mu_point.txt.gz')

sigma_point = np.loadtxt(
        results_dir + 'sigma_point.txt.gz')

hrr_point = np.loadtxt(
        results_dir + 'hrr_point.txt.gz')

hrr_distribution = np.loadtxt(
        results_dir + 'hrr_distribution.txt.gz')

output_hgl_temps = np.loadtxt(
        results_dir + 'output_hgl_temps.txt.gz')

output_hgl_temps_adjusted = np.loadtxt(
        results_dir + 'output_hgl_temps_adjusted.txt.gz')

#  ============================
#  = Plot input distributions =
#  ============================

plot_range = np.arange(0, x_upper_input, 0.1)

figure()
hist(np.array([hrr_point]), bins=1, normed=1, color='k', lw=2)
xlabel('HRR (kW)', fontsize=20)
ylabel('Probability Density Function', fontsize=20)
grid(True)
xlim([0, x_upper_input])
ax = gca()
for xlabel_i in ax.get_xticklabels():
    xlabel_i.set_fontsize(font_size)
for ylabel_i in ax.get_yticklabels():
    ylabel_i.set_fontsize(font_size)
gcf().subplots_adjust(left=0.15, bottom=0.11)
savefig(figures_dir + 'input_PDF_point.pdf')

figure()
hist(np.array([hrr_point]), bins=1,
     normed=1, histtype='step', cumulative=True, color='k', lw=2)
xlabel('HRR (kW)', fontsize=20)
ylabel('Cumulative Density Function', fontsize=20)
ylim([0, 1])
grid(True)
xlim([0, x_upper_input])
ax = gca()
for xlabel_i in ax.get_xticklabels():
    xlabel_i.set_fontsize(font_size)
for ylabel_i in ax.get_yticklabels():
    ylabel_i.set_fontsize(font_size)
gcf().subplots_adjust(left=0.15, bottom=0.11)
savefig(figures_dir + 'input_CDF_point.pdf')

figure()
plot(plot_range, sp.stats.gamma.pdf(plot_range,
                                   hrr_gamma_parameters[0],
                                   scale=hrr_gamma_parameters[1]),
     lw=2, color='k')
xlabel('HRR (kW)', fontsize=20)
ylabel('Probability Density Function', fontsize=20)
grid(True)
xlim([0, x_upper_input])
ylim([0, y_upper_input])
ax = gca()
for xlabel_i in ax.get_xticklabels():
    xlabel_i.set_fontsize(font_size)
for ylabel_i in ax.get_yticklabels():
    ylabel_i.set_fontsize(font_size)
gcf().subplots_adjust(left=0.15, bottom=0.11)
savefig(figures_dir + 'input_PDF.pdf')

figure()
plot(plot_range, sp.stats.gamma.cdf(plot_range,
                                   hrr_gamma_parameters[0],
                                   scale=hrr_gamma_parameters[1]),
     lw=2, color='k')
xlabel('HRR (kW)', fontsize=20)
ylabel('Cumulative Density Function', fontsize=20)
ylim([0, 1])
grid(True)
xlim([0, x_upper_input])
ax = gca()
for xlabel_i in ax.get_xticklabels():
    xlabel_i.set_fontsize(font_size)
for ylabel_i in ax.get_yticklabels():
    ylabel_i.set_fontsize(font_size)
gcf().subplots_adjust(left=0.15, bottom=0.11)
savefig(figures_dir + 'input_CDF.pdf')

#  =============================
#  = Plot output distributions =
#  =============================

figure()
fill(plot_range, sp.stats.norm.pdf(plot_range, mu_point, sigma_point),
     ec='k', color='0.7')
axvline(threshold_hgl_temp, color='k', lw=3)
xlabel(r'HGL Temperature ($^\circ$C)', fontsize=20)
ylabel('Probability Density Function', fontsize=20)
grid(True)
xlim([0, x_upper_output])
ylim([0, y_upper_output])
ax = gca()
for xlabel_i in ax.get_xticklabels():
    xlabel_i.set_fontsize(font_size)
for ylabel_i in ax.get_yticklabels():
    ylabel_i.set_fontsize(font_size)
gcf().subplots_adjust(left=0.15, bottom=0.11)
savefig(figures_dir + 'output_PDF_1_model.pdf')

figure()
hist(output_hgl_temps, bins=histogram_bins/25, normed=1, color='0.7')
axvline(threshold_hgl_temp, color='k', lw=3)
xlabel(r'HGL Temperature ($^\circ$C)', fontsize=20)
ylabel('Probability Density Function', fontsize=20)
grid(True)
xlim([0, x_upper_output])
ylim([0, y_upper_output])
ax = gca()
for xlabel_i in ax.get_xticklabels():
    xlabel_i.set_fontsize(font_size)
for ylabel_i in ax.get_yticklabels():
    ylabel_i.set_fontsize(font_size)
gcf().subplots_adjust(left=0.15, bottom=0.11)
savefig(figures_dir + 'output_PDF_2_input.pdf')

figure()
hist(output_hgl_temps_adjusted, bins=histogram_bins/22, normed=1, color='0.7')
axvline(threshold_hgl_temp, color='k', lw=3)
xlabel(r'HGL Temperature ($^\circ$C)', fontsize=20)
ylabel('Probability Density Function', fontsize=20)
grid(True)
xlim([0, x_upper_output])
ylim([0, y_upper_output])
ax = gca()
for xlabel_i in ax.get_xticklabels():
    xlabel_i.set_fontsize(font_size)
for ylabel_i in ax.get_yticklabels():
    ylabel_i.set_fontsize(font_size)
gcf().subplots_adjust(left=0.15, bottom=0.11)
savefig(figures_dir + 'output_PDF_3_combined.pdf')

figure()
plot(plot_range, sp.stats.norm.cdf(plot_range, mu_point, sigma_point),
     color='k', lw=2)
xlabel(r'HGL Temperature ($^\circ$C)', fontsize=20)
ylabel('Cumulative Density Function', fontsize=20)
xlim([0, x_upper_output])
ylim([0, 1])
grid(True)
ax = gca()
for xlabel_i in ax.get_xticklabels():
    xlabel_i.set_fontsize(font_size)
for ylabel_i in ax.get_yticklabels():
    ylabel_i.set_fontsize(font_size)
gcf().subplots_adjust(left=0.15, bottom=0.11)
savefig(figures_dir + 'output_CDF_1_model.pdf')

figure()
hist(output_hgl_temps, bins=histogram_bins,
     normed=1, histtype='step', cumulative=True, color='k', lw=2)
xlabel(r'HGL Temperature ($^\circ$C)', fontsize=20)
ylabel('Cumulative Density Function', fontsize=20)
xlim([0, x_upper_output])
ylim([0, 1])
grid(True)
ax = gca()
for xlabel_i in ax.get_xticklabels():
    xlabel_i.set_fontsize(font_size)
for ylabel_i in ax.get_yticklabels():
    ylabel_i.set_fontsize(font_size)
gcf().subplots_adjust(left=0.15, bottom=0.11)
savefig(figures_dir + 'output_CDF_2_input.pdf')

figure()
hist(output_hgl_temps_adjusted, bins=histogram_bins, 
     normed=1, histtype='step', cumulative=True,
     color='k', lw=2)
xlabel(r'HGL Temperature ($^\circ$C)', fontsize=20)
ylabel('Cumulative Density Function', fontsize=20)
xlim([0, x_upper_output])
ylim([0, 1])
grid(True)
ax = gca()
for xlabel_i in ax.get_xticklabels():
    xlabel_i.set_fontsize(font_size)
for ylabel_i in ax.get_yticklabels():
    ylabel_i.set_fontsize(font_size)
gcf().subplots_adjust(left=0.15, bottom=0.11)
savefig(figures_dir + 'output_CDF_3_combined.pdf')

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
