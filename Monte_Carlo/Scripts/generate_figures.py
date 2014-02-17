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
histogram_bins = 1000

# x-axis limits for output PDF/CDF plots
x_lower = 0
x_upper = 180

# Upper y-axis limit for output PDF plots
y_pdf_upper = 0.03

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

# Initialize point value and parameter distribution
hrr_lower = hrr - (hrr * variation)
hrr_upper = hrr + (hrr * variation)
hrr_point = hrr

#  =======================
#  = Read data from disk =
#  =======================

mu_point = np.loadtxt(
        results_dir + 'mu_point.txt.gz')

sigma_point = np.loadtxt(
        results_dir + 'sigma_point.txt.gz')

hrr_uniform = np.loadtxt(
        results_dir + 'hrr_uniform.txt.gz')

output_hgl_temps = np.loadtxt(
        results_dir + 'output_hgl_temps.txt.gz')

output_hgl_temps_adjusted = np.loadtxt(
        results_dir + 'output_hgl_temps_adjusted.txt.gz')

#  ============================
#  = Plot input distributions =
#  ============================

hrr_range = np.arange(hrr_lower, hrr_upper, 0.01)

figure()
hist(np.array([hrr_point]), bins=1, normed=1, color='k', lw=2)
xlabel('HRR (kW)', fontsize=20)
ylabel('Probability Density Function', fontsize=20)
grid(True)
xlim([0, 1000])
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
xlim([0, 1000])
ax = gca()
for xlabel_i in ax.get_xticklabels():
    xlabel_i.set_fontsize(font_size)
for ylabel_i in ax.get_yticklabels():
    ylabel_i.set_fontsize(font_size)
gcf().subplots_adjust(left=0.15, bottom=0.11)
savefig(figures_dir + 'input_CDF_point.pdf')

figure()
hist(hrr_range, bins=1,
     normed=1, color='0.7')
xlabel('HRR (kW)', fontsize=20)
ylabel('Probability Density Function', fontsize=20)
grid(True)
xlim([0, 1000])
ax = gca()
for xlabel_i in ax.get_xticklabels():
    xlabel_i.set_fontsize(font_size)
for ylabel_i in ax.get_yticklabels():
    ylabel_i.set_fontsize(font_size)
gcf().subplots_adjust(left=0.15, bottom=0.11)
savefig(figures_dir + 'input_PDF.pdf')

figure()
hist(hrr_range, bins=histogram_bins,
     normed=1, histtype='step', cumulative=True, color='k', lw=2)
xlabel('HRR (kW)', fontsize=20)
ylabel('Cumulative Density Function', fontsize=20)
ylim([0, 1])
grid(True)
xlim([0, 1000])
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

case1_range = np.arange(x_lower, x_upper, 0.001)

figure()
fill(case1_range, sp.stats.norm.pdf(case1_range, mu_point, sigma_point),
     ec='k', color='0.7')
axvline(100, color='k', lw=3)
xlabel(r'HGL Temperature ($^\circ$C)', fontsize=20)
ylabel('Probability Density Function', fontsize=20)
grid(True)
xlim([x_lower, x_upper])
ylim([0, y_pdf_upper])
ax = gca()
for xlabel_i in ax.get_xticklabels():
    xlabel_i.set_fontsize(font_size)
for ylabel_i in ax.get_yticklabels():
    ylabel_i.set_fontsize(font_size)
gcf().subplots_adjust(left=0.15, bottom=0.11)
savefig(figures_dir + 'output_PDF_1_model.pdf')

figure()
hist(output_hgl_temps, bins=histogram_bins/125, normed=1, color='0.7')
axvline(100, color='k', lw=3)
xlabel(r'HGL Temperature ($^\circ$C)', fontsize=20)
ylabel('Probability Density Function', fontsize=20)
grid(True)
xlim([x_lower, x_upper])
ax = gca()
for xlabel_i in ax.get_xticklabels():
    xlabel_i.set_fontsize(font_size)
for ylabel_i in ax.get_yticklabels():
    ylabel_i.set_fontsize(font_size)
gcf().subplots_adjust(left=0.15, bottom=0.11)
savefig(figures_dir + 'output_PDF_2_input.pdf')

figure()
hist(output_hgl_temps_adjusted, bins=histogram_bins/25, normed=1, color='0.7')
axvline(100, color='k', lw=3)
xlabel(r'HGL Temperature ($^\circ$C)', fontsize=20)
ylabel('Probability Density Function', fontsize=20)
grid(True)
xlim([x_lower, x_upper])
ylim([0, y_pdf_upper])
ax = gca()
for xlabel_i in ax.get_xticklabels():
    xlabel_i.set_fontsize(font_size)
for ylabel_i in ax.get_yticklabels():
    ylabel_i.set_fontsize(font_size)
gcf().subplots_adjust(left=0.15, bottom=0.11)
savefig(figures_dir + 'output_PDF_3_combined.pdf')

figure()
plot(case1_range, sp.stats.norm.cdf(case1_range, mu_point, sigma_point),
     color='k', lw=2)
xlabel(r'HGL Temperature ($^\circ$C)', fontsize=20)
ylabel('Cumulative Density Function', fontsize=20)
xlim([x_lower, x_upper])
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
hist(output_hgl_temps, bins=histogram_bins/5,
     normed=1, histtype='step', cumulative=True, color='k', lw=2)
xlabel(r'HGL Temperature ($^\circ$C)', fontsize=20)
ylabel('Cumulative Density Function', fontsize=20)
xlim([x_lower, x_upper])
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
hist(output_hgl_temps_adjusted,
     bins=histogram_bins, normed=1, histtype='step', cumulative=True,
     color='k', lw=2)
xlabel(r'HGL Temperature ($^\circ$C)', fontsize=20)
ylabel('Cumulative Density Function', fontsize=20)
xlim([x_lower, x_upper])
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
