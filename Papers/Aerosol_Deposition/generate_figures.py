#!/usr/bin/env python

from __future__ import division

import matplotlib
matplotlib.use("Agg")

import numpy as np
from pylab import *

from matplotlib import rcParams
rcParams.update({'figure.autolayout': True})

#  =======================================
#  = Sippola aerosol deposition velocity =
#  =======================================

# Read in exp. data for each test
data_exp_1 = np.genfromtxt((
    '/Users/koverholt/FDS-SMV/Validation/Sippola_Aerosol_Deposition/'
    'Experimental_Data/Sippola_deposition_velocity.csv'),
    delimiter=',', names=True,
    usecols=(0, 1, 2, 3, 4, 5, 6, 7, 8))

# Read in exp. data for each test
data_exp_2 = np.genfromtxt((
    '/Users/koverholt/FDS-SMV/Validation/Sippola_Aerosol_Deposition/'
    'Experimental_Data/Sippola_deposition_velocity.csv'),
    delimiter=',', names=True, skip_footer=1,
    usecols=(9,  10, 11, 12, 13, 14, 15, 16, 17,
             18, 19, 20, 21, 22, 23, 24, 25, 26,
             27, 28, 29, 30, 31, 32, 33, 34, 35,
             36, 37, 38, 39, 40, 41, 42, 43, 44,
             45, 46, 47, 48, 49))

# Read in FDS data
data_FDS_1 = np.genfromtxt((
    '/Users/koverholt/FDS-SMV/Validation/Sippola_Aerosol_Deposition/'
    'FDS_Output_Files/Sippola_All_Tests.csv'),
    delimiter=',', names=True,
    usecols=(0, 1, 2, 3, 4, 5, 6, 7, 8))

# Read in FDS data
data_FDS_2 = np.genfromtxt((
    '/Users/koverholt/FDS-SMV/Validation/Sippola_Aerosol_Deposition/'
    'FDS_Output_Files/Sippola_All_Tests.csv'),
    delimiter=',', names=True, skip_footer=1,
    usecols=(9,  10, 11, 12, 13, 14, 15, 16, 17,
             18, 19, 20, 21, 22, 23, 24, 25, 26,
             27, 28, 29, 30, 31, 32, 33, 34, 35,
             36, 37, 38, 39, 40, 41, 42, 43, 44))

#  ====================================
#  = Sippola Aerosol Deposition Plots =
#  ====================================

##############
fig = figure()
ax = fig.add_subplot(111)

semilogy(data_exp_1['Air_Velocity_1_um_ms'],
         data_exp_1['Ceiling_Deposition_Velocity_1_um_ms'],
         'ko', ms=7, mec='k', mew=1.5)

semilogy(data_exp_2['Air_Velocity_3_um_ms'],
         data_exp_2['Ceiling_Deposition_Velocity_3_um_ms'],
         'rs', ms=7, mec='r', mew=1.5)

semilogy(data_exp_2['Air_Velocity_5_um_ms'],
         data_exp_2['Ceiling_Deposition_Velocity_5_um_ms'],
         'g^', ms=7, mec='g', mew=1.5)

semilogy(data_exp_2['Air_Velocity_9_um_ms'],
         data_exp_2['Ceiling_Deposition_Velocity_9_um_ms'],
         'bD', ms=7, mec='b', mew=1.5)

semilogy(data_exp_2['Air_Velocity_16_um_ms'],
         data_exp_2['Ceiling_Deposition_Velocity_16_um_ms'],
         'cv', ms=7, mec='c', mew=1.5)

semilogy(data_FDS_1['Air_Velocity_1_um_ms'],
         data_FDS_1['Ceiling_Deposition_Velocity_1_um_ms'],
         'wo', ms=7, mec='k', mew=1.5)

semilogy(data_FDS_2['Air_Velocity_3_um_ms'],
         data_FDS_2['Ceiling_Deposition_Velocity_3_um_ms'],
         'ws', ms=7, mec='r', mew=1.5)

semilogy(data_FDS_2['Air_Velocity_5_um_ms'],
         data_FDS_2['Ceiling_Deposition_Velocity_5_um_ms'],
         'w^', ms=7, mec='g', mew=1.5)

semilogy(data_FDS_2['Air_Velocity_9_um_ms'],
         data_FDS_2['Ceiling_Deposition_Velocity_9_um_ms'],
         'wD', ms=7, mec='b', mew=1.5)

semilogy(data_FDS_2['Air_Velocity_16_um_ms'],
         data_FDS_2['Ceiling_Deposition_Velocity_16_um_ms'],
         'wv', ms=7, mec='c', mew=1.5)

text(0.05, 0.90, 'Sippola Aerosol Deposition, Ceiling',
     transform=ax.transAxes,
     size=16)

xlim([0, 10])
ylim([1e-7, 1e-1])
xlabel('Air Velocity (m/s)', fontsize=20)
ylabel('Deposition Velocity (m/s)', fontsize=20)
grid(True)
xticks(fontsize=16)
yticks(fontsize=16)
savefig('Fig_Sippola_Aerosol_Ceiling_Deposition.pdf')

##############
fig = figure()
ax = fig.add_subplot(111)

semilogy(data_exp_1['Air_Velocity_1_um_ms'],
         data_exp_1['Wall_Deposition_Velocity_1_um_ms'],
         'ko', ms=7, mec='k', mew=1.5)

semilogy(data_exp_2['Air_Velocity_3_um_ms'],
         data_exp_2['Wall_Deposition_Velocity_3_um_ms'],
         'rs', ms=7, mec='r', mew=1.5)

semilogy(data_exp_2['Air_Velocity_5_um_ms'],
         data_exp_2['Wall_Deposition_Velocity_5_um_ms'],
         'g^', ms=7, mec='g', mew=1.5)

semilogy(data_exp_2['Air_Velocity_9_um_ms'],
         data_exp_2['Wall_Deposition_Velocity_9_um_ms'],
         'bD', ms=7, mec='b', mew=1.5)

semilogy(data_exp_2['Air_Velocity_16_um_ms'],
         data_exp_2['Wall_Deposition_Velocity_16_um_ms'],
         'cv', ms=7, mec='c', mew=1.5)

semilogy(data_FDS_1['Air_Velocity_1_um_ms'],
         data_FDS_1['Wall_Deposition_Velocity_1_um_ms'],
         'wo', ms=7, mec='k', mew=1.5)

semilogy(data_FDS_2['Air_Velocity_3_um_ms'],
         data_FDS_2['Wall_Deposition_Velocity_3_um_ms'],
         'ws', ms=7, mec='r', mew=1.5)

semilogy(data_FDS_2['Air_Velocity_5_um_ms'],
         data_FDS_2['Wall_Deposition_Velocity_5_um_ms'],
         'w^', ms=7, mec='g', mew=1.5)

semilogy(data_FDS_2['Air_Velocity_9_um_ms'],
         data_FDS_2['Wall_Deposition_Velocity_9_um_ms'],
         'wD', ms=7, mec='b', mew=1.5)

semilogy(data_FDS_2['Air_Velocity_16_um_ms'],
         data_FDS_2['Wall_Deposition_Velocity_16_um_ms'],
         'wv', ms=7, mec='c', mew=1.5)

text(0.05, 0.90, 'Sippola Aerosol Deposition, Wall',
     transform=ax.transAxes,
     size=16)

xlim([0, 10])
ylim([1e-7, 1e-1])
xlabel('Air Velocity (m/s)', fontsize=20)
ylabel('Deposition Velocity (m/s)', fontsize=20)
grid(True)
xticks(fontsize=16)
yticks(fontsize=16)
savefig('Fig_Sippola_Aerosol_Wall_Deposition.pdf')

##############
fig = figure()
ax = fig.add_subplot(111)

semilogy(data_exp_1['Air_Velocity_1_um_ms'],
         data_exp_1['Floor_Deposition_Velocity_1_um_ms'],
         'ko', ms=7, mec='k', mew=1.5)

semilogy(data_exp_2['Air_Velocity_3_um_ms'],
         data_exp_2['Floor_Deposition_Velocity_3_um_ms'],
         'rs', ms=7, mec='r', mew=1.5)

semilogy(data_exp_2['Air_Velocity_5_um_ms'],
         data_exp_2['Floor_Deposition_Velocity_5_um_ms'],
         'g^', ms=7, mec='g', mew=1.5)

semilogy(data_exp_2['Air_Velocity_9_um_ms'],
         data_exp_2['Floor_Deposition_Velocity_9_um_ms'],
         'bD', ms=7, mec='b', mew=1.5)

semilogy(data_exp_2['Air_Velocity_16_um_ms'],
         data_exp_2['Floor_Deposition_Velocity_16_um_ms'],
         'cv', ms=7, mec='c', mew=1.5)

semilogy(data_FDS_1['Air_Velocity_1_um_ms'],
         data_FDS_1['Floor_Deposition_Velocity_1_um_ms'],
         'wo', ms=7, mec='k', mew=1.5)

semilogy(data_FDS_2['Air_Velocity_3_um_ms'],
         data_FDS_2['Floor_Deposition_Velocity_3_um_ms'],
         'ws', ms=7, mec='r', mew=1.5)

semilogy(data_FDS_2['Air_Velocity_5_um_ms'],
         data_FDS_2['Floor_Deposition_Velocity_5_um_ms'],
         'w^', ms=7, mec='g', mew=1.5)

semilogy(data_FDS_2['Air_Velocity_9_um_ms'],
         data_FDS_2['Floor_Deposition_Velocity_9_um_ms'],
         'wD', ms=7, mec='b', mew=1.5)

semilogy(data_FDS_2['Air_Velocity_16_um_ms'],
         data_FDS_2['Floor_Deposition_Velocity_16_um_ms'],
         'wv', ms=7, mec='c', mew=1.5)

text(0.05, 0.90, 'Sippola Aerosol Deposition, Floor',
     transform=ax.transAxes,
     size=16)

xlim([0, 10])
ylim([1e-7, 1e-1])
xlabel('Air Velocity (m/s)', fontsize=20)
ylabel('Deposition Velocity (m/s)', fontsize=20)
grid(True)
xticks(fontsize=16)
yticks(fontsize=16)
savefig('Fig_Sippola_Aerosol_Floor_Deposition.pdf')

#  ========================
#  = Sippola scatter plot =
#  ========================

fig = figure(figsize=(8,7))
ax = fig.add_subplot(111)

loglog(data_exp_1['Ceiling_Deposition_Velocity_1_um_ms'],
       data_FDS_1['Ceiling_Deposition_Velocity_1_um_ms'],
       'r^', ms=7, mec='r', label='Sippola, Ceiling')

loglog(data_exp_1['Wall_Deposition_Velocity_1_um_ms'],
       data_FDS_1['Wall_Deposition_Velocity_1_um_ms'],
       'ks', ms=7, mec='k', label='Sippola, Wall')

loglog(data_exp_1['Floor_Deposition_Velocity_1_um_ms'],
       data_FDS_1['Floor_Deposition_Velocity_1_um_ms'],
       'go', ms=7, mec='g', label='Sippola, Floor')

loglog(data_exp_2['Ceiling_Deposition_Velocity_3_um_ms'],
       data_FDS_2['Ceiling_Deposition_Velocity_3_um_ms'],
       'r^', ms=7, mec='r')

loglog(data_exp_2['Wall_Deposition_Velocity_3_um_ms'],
       data_FDS_2['Wall_Deposition_Velocity_3_um_ms'],
       'ks', ms=7, mec='k')

loglog(data_exp_2['Floor_Deposition_Velocity_3_um_ms'],
       data_FDS_2['Floor_Deposition_Velocity_3_um_ms'],
       'go', ms=7, mec='g')

loglog(data_exp_2['Ceiling_Deposition_Velocity_5_um_ms'],
       data_FDS_2['Ceiling_Deposition_Velocity_5_um_ms'],
       'r^', ms=7, mec='r')

loglog(data_exp_2['Wall_Deposition_Velocity_5_um_ms'],
       data_FDS_2['Wall_Deposition_Velocity_5_um_ms'],
       'ks', ms=7, mec='k')

loglog(data_exp_2['Floor_Deposition_Velocity_5_um_ms'],
       data_FDS_2['Floor_Deposition_Velocity_5_um_ms'],
       'go', ms=7, mec='g')

loglog(data_exp_2['Ceiling_Deposition_Velocity_9_um_ms'],
       data_FDS_2['Ceiling_Deposition_Velocity_9_um_ms'],
       'r^', ms=7, mec='r')

loglog(data_exp_2['Wall_Deposition_Velocity_9_um_ms'],
       data_FDS_2['Wall_Deposition_Velocity_9_um_ms'],
       'ks', ms=7, mec='k')

loglog(data_exp_2['Floor_Deposition_Velocity_9_um_ms'],
       data_FDS_2['Floor_Deposition_Velocity_9_um_ms'],
       'go', ms=7, mec='g')

loglog(data_exp_2['Ceiling_Deposition_Velocity_16_um_ms'],
       data_FDS_2['Ceiling_Deposition_Velocity_16_um_ms'],
       'r^', ms=7, mec='r')

loglog(data_exp_2['Wall_Deposition_Velocity_16_um_ms'],
       data_FDS_2['Wall_Deposition_Velocity_16_um_ms'],
       'ks', ms=7, mec='k')

loglog(data_exp_2['Floor_Deposition_Velocity_16_um_ms'],
       data_FDS_2['Floor_Deposition_Velocity_16_um_ms'],
       'go', ms=7, mec='g')

loglog(np.arange(1e-7, 1e-1, .001), np.arange(1e-7, 1e-1, .001), 'k-', lw=1)

text(0.05, 0.90, 'Aerosol Deposition Velocity',
     transform=ax.transAxes,
     size=16)

legend(loc='lower right', numpoints=1)
xlim([1e-7, 1e-1])
ylim([1e-7, 1e-1])
xlabel('Measured Deposition Velocity (m/s)', fontsize=20)
ylabel('Predicted Deposition Velocity (m/s)', fontsize=20)
grid(True)
xticks(fontsize=16)
yticks(fontsize=16)
savefig('Fig_Sippola_Aerosol_Deposition_Velocity_Scatter.pdf')

#  ====================================================================
#  = Sippola aerosol deposition velocity - conc. gradients downstream =
#  ====================================================================

data_FDS = {}

test_names = (['01', '02', '03', '04', '05', '06', '07', '08',
               '09', '10', '11', '12', '13', '14', '15', '16'])

for test in test_names:
    # Read in FDS data for each test
    data_FDS[test] = np.genfromtxt((
        'Sippola_Aerosol_Deposition/Downstream_Concentration_Gradients/Sippola_Test_' + test + '_line.csv'),
        delimiter=',', names=True, skip_header=1)


fig = figure()
ax = fig.add_subplot(111)

for test in test_names:
    if test in ['01', '06', '07', '12']:
        plot(data_FDS[test]['Soot_Concentrationx'],
             data_FDS[test]['Soot_Concentration']*1e6,
             'k-', marker='o', markevery=6, lw=2, label='1 $\mu$ m particles')

    # if test in ['02', '08', '13']:
        # plot(data_FDS[test]['Soot_Concentrationx'],
             # data_FDS[test]['Soot_Concentration']*1e6,
             # 'r-', lw=2, label='3 $\mu$ m particles')

    if test in ['03', '09', '14']:
        plot(data_FDS[test]['Soot_Concentrationx'],
             data_FDS[test]['Soot_Concentration']*1e6,
             'g-', marker='s', markevery=6, lw=2, label='5 $\mu$ m particles')

    # if test in ['04', '10', '15']:
        # plot(data_FDS[test]['Soot_Concentrationx'],
             # data_FDS[test]['Soot_Concentration']*1e6,
             # 'b-', lw=2, label='9 $\mu$ m particles')

    if test in ['05', '11', '16']:
        plot(data_FDS[test]['Soot_Concentrationx'],
             data_FDS[test]['Soot_Concentration']*1e6,
             'c-', marker='D', markevery=6, lw=2, label='16 $\mu$ m particles')

xlim([0, 1.5])
xlabel('x Distance (m)', fontsize=20)
ylabel('Soot Concentration (mg/m$^3$)', fontsize=20)
grid(True)
xticks(fontsize=16)
yticks(fontsize=16)
savefig('Fig_Sippola_Aerosol_Deposition_Soot_Concentration_All.pdf')

#  ============================================================
#  = Sippola aerosol deposition velocity transverse gradients =
#  ============================================================

# Read in FDS data
data_FDS_1_um = np.genfromtxt((
    'Sippola_Aerosol_Deposition/Traverse_Concentration/' +
    'Sippola_Test_01_devc.csv'),
    delimiter=',', names=True, skip_header=1)

# Read in FDS data
data_FDS_16_um = np.genfromtxt((
    'Sippola_Aerosol_Deposition/Traverse_Concentration/' +
    'Sippola_Test_16_devc.csv'),
    delimiter=',', names=True, skip_header=1)

text(0.05, 0.90, 'Aerosol Deposition Velocity',
     transform=ax.transAxes,
     size=16)

z = np.arange(0.005, 0.155, 0.01)
vel_1_um = np.array([data_FDS_1_um['Vel_1'][-1],
                     data_FDS_1_um['Vel_2'][-1],
                     data_FDS_1_um['Vel_3'][-1],
                     data_FDS_1_um['Vel_4'][-1],
                     data_FDS_1_um['Vel_5'][-1],
                     data_FDS_1_um['Vel_6'][-1],
                     data_FDS_1_um['Vel_7'][-1],
                     data_FDS_1_um['Vel_8'][-1],
                     data_FDS_1_um['Vel_9'][-1],
                     data_FDS_1_um['Vel_10'][-1],
                     data_FDS_1_um['Vel_11'][-1],
                     data_FDS_1_um['Vel_12'][-1],
                     data_FDS_1_um['Vel_13'][-1],
                     data_FDS_1_um['Vel_14'][-1],
                     data_FDS_1_um['Vel_15'][-1]])

vel_16_um = np.array([data_FDS_16_um['Vel_1'][-1],
                      data_FDS_16_um['Vel_2'][-1],
                      data_FDS_16_um['Vel_3'][-1],
                      data_FDS_16_um['Vel_4'][-1],
                      data_FDS_16_um['Vel_5'][-1],
                      data_FDS_16_um['Vel_6'][-1],
                      data_FDS_16_um['Vel_7'][-1],
                      data_FDS_16_um['Vel_8'][-1],
                      data_FDS_16_um['Vel_9'][-1],
                      data_FDS_16_um['Vel_10'][-1],
                      data_FDS_16_um['Vel_11'][-1],
                      data_FDS_16_um['Vel_12'][-1],
                      data_FDS_16_um['Vel_13'][-1],
                      data_FDS_16_um['Vel_14'][-1],
                      data_FDS_16_um['Vel_15'][-1]])

conc_1_um = np.array([data_FDS_1_um['Soot_1'][-1],
                      data_FDS_1_um['Soot_2'][-1],
                      data_FDS_1_um['Soot_3'][-1],
                      data_FDS_1_um['Soot_4'][-1],
                      data_FDS_1_um['Soot_5'][-1],
                      data_FDS_1_um['Soot_6'][-1],
                      data_FDS_1_um['Soot_7'][-1],
                      data_FDS_1_um['Soot_8'][-1],
                      data_FDS_1_um['Soot_9'][-1],
                      data_FDS_1_um['Soot_10'][-1],
                      data_FDS_1_um['Soot_11'][-1],
                      data_FDS_1_um['Soot_12'][-1],
                      data_FDS_1_um['Soot_13'][-1],
                      data_FDS_1_um['Soot_14'][-1],
                      data_FDS_1_um['Soot_15'][-1]])

conc_16_um = np.array([data_FDS_16_um['Soot_1'][-1],
                       data_FDS_16_um['Soot_2'][-1],
                       data_FDS_16_um['Soot_3'][-1],
                       data_FDS_16_um['Soot_4'][-1],
                       data_FDS_16_um['Soot_5'][-1],
                       data_FDS_16_um['Soot_6'][-1],
                       data_FDS_16_um['Soot_7'][-1],
                       data_FDS_16_um['Soot_8'][-1],
                       data_FDS_16_um['Soot_9'][-1],
                       data_FDS_16_um['Soot_10'][-1],
                       data_FDS_16_um['Soot_11'][-1],
                       data_FDS_16_um['Soot_12'][-1],
                       data_FDS_16_um['Soot_13'][-1],
                       data_FDS_16_um['Soot_14'][-1],
                       data_FDS_16_um['Soot_15'][-1]])

fig = figure()
plot(vel_1_um, z, 'k-', lw=2, label='FDS (1 um particles, u$_0$ = 2.2 m/s)')
plot(vel_16_um, z, 'r--', lw=2, label='FDS (16 um particles, u$_0$ = 9.1 m/s)')
# legend(loc='lower right', numpoints=1)
xlim([0, 12])
ylim([0, 0.15])
xlabel('Velocity (m/s)', fontsize=20)
ylabel('Duct Height (m)', fontsize=20)
grid(True)
xticks(fontsize=16)
yticks(fontsize=16)
ax = gca()
ax.yaxis.set_major_locator(MaxNLocator(12))
savefig('Fig_Sippola_Aerosol_Deposition_Transverse_Velocity.pdf')

fig = figure()
plot(conc_1_um*1e6, z, 'k-', lw=2, label='FDS (1 um particles, u$_0$ = 2.2 m/s)')
plot(conc_16_um*1e6, z, 'r--', lw=2, label='FDS (16 um particles, u$_0$ = 9.1 m/s)')
# legend(loc='lower right', numpoints=1)
xlim([0, 140])
ylim([0, 0.15])
xlabel('Aerosol Concentration (mg/m$^3$)', fontsize=20)
ylabel('Duct Height (m)', fontsize=20)
grid(True)
xticks(fontsize=16)
yticks(fontsize=16)
ax = gca()
ax.yaxis.set_major_locator(MaxNLocator(12))
savefig('Fig_Sippola_Aerosol_Deposition_Transverse_Concentration.pdf')

