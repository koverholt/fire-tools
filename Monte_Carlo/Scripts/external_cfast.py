#!/usr/bin/env python

"""Module for CFAST functions"""

import numpy as np
import platform
import subprocess

# Detect operating system
op_sys = platform.system()


def gen_input(x, y, z, tmp_a, hoc, time_ramp, hrr_ramp, wall,
              simulation_time, dt_data):
    """
    Generate CFAST input file and initialize HRR arrays

    Keyword arguments:
    x -- x dimension of compartment
    y -- y dimension of compartment
    z -- z dimension of compartment
    t_a -- ambient temperature (C)
    hoc -- heat of combustion (kJ/kg)
    time_ramp -- time portion of HRR curve of fire (s)
    hrr_ramp -- heat release rate portion of HRR curve (kW)
    wall -- wall material (string)
    simulation_time -- length of time to run the simulation (s)
    dt_data -- Data sampling rate and CFAST output frequency (s)
    """

    #  =============================
    #  = CFAST input file template =
    #  =============================

    # Original time and HRR ramp for Switchgear room case
    # TIME,0,72,144,216,288,360,432,504,576,648,720,1200,1920,1930
    # HRR,0,4640,18560,41760,74240.01,116000,167040,227360,296960,375840,464000,464000,0,0

    template = """VERSN,6,CFAST Simulation
!!
!!Scenario Configuration Keywords
!!
TIMES,%(simulation_time)s,-300,0,10,%(dt_data)s
EAMB,%(t_ambient)s,101300,0
TAMB,%(t_ambient)s,101300,0,50
CJET,WALLS
WIND,0,10,0.16
!!
!!Material Properties
!!
MATL,CABSWConcrete,1.6,750,2400,0.5,0.9,Cabinet Switchgear Concrete Floor (user's guide)
MATL,CABSWPVC,0.2,1500,2264,0.015,0.9,Cabinet Switchgear PVC-PE Cable (NUREG 1824)
MATL,CABSWSteel,48,559,7854,0.0015,0.9,Cabinet Switchgear Steel Cabinet (user's guide)
MATL,THIEF,0.2,1500,2150,0.015,0.8,Thief Cable (per NUREG CR 6931)
!!
!!Compartment keywords
!!
COMPA,Switchgear Room,%(x)s,%(y)s,%(z)s,0,0,0,%(wall_matl)s
!!
!!Vent keywords
!!
HVENT,1,2,1,1.0922,0.013,0,1,15.0114,15.0114,4,1
MVENT,2,1,1,H,5.6,0.3,H,5.6,0.3,0.472,200,300,1
MVENT,2,1,2,H,5.6,0.3,H,5.6,0.3,0.472,200,300,1
MVENT,2,1,3,H,5.6,0.3,H,5.6,0.3,0.472,200,300,1
MVENT,1,2,4,H,5.6,0.3,H,5.6,0.3,0.472,200,300,1
MVENT,1,2,5,H,5.6,0.3,H,5.6,0.3,0.472,200,300,1
MVENT,1,2,6,H,5.6,0.3,H,5.6,0.3,0.472,200,300,1
!!
!!Fire keywords
!!
!!PE_PVC
FIRE,1,8.3,9.5,2.4,1,1,0,0,0,1,PE_PVC
CHEMI,1,4,0,0,0,0.49,%(hoc)s,CABSWPVC
TIME,%(time_ramp)s
HRR,%(hrr_ramp)s
SOOT,0.11,0.11,0.11,0.11,0.11,0.11,0.11,0.11,0.11,0.11,0.11,0.11,0.11,0.11
CO,0.11,0.11,0.11,0.11,0.11,0.11,0.11,0.11,0.11,0.11,0.11,0.11,0.11,0.11
TRACE,0,0,0,0,0,0,0,0,0,0,0,0,0,0
AREA,0.18,0.18,0.18,0.18,0.18,0.18,0.18,0.18,0.18,0.18,0.18,0.18,0.18,0.18
HEIGH,0,0,0,0,0,0,0,0,0,0,0,0,0,0
!!
!!Target and detector keywords
!!
TARGET,1,8.3,7,2.4,0,1,0,CABSWSteel,EXPLICIT,PDE,0.5
TARGET,1,8.3,12,2.4,0,-1,0,CABSWSteel,IMPLICIT,PDE,0.5
TARGET,1,8.3,9.5,3.9,0,0,-1,THIEF,EXPLICIT,CYL,0.2
TARGET,1,8.3,9.5,4.4,0,0,-1,THIEF,EXPLICIT,CYL,0.2
TARGET,1,8.3,9.5,4.9,0,0,-1,THIEF,EXPLICIT,CYL,0.2
"""

    # Convert HRR from kW to W
    hrr_w = hrr_ramp * 1000

    # Format arrays as comma separated lists for CFAST input file
    times_to_print = ','.join([str(i) for i in time_ramp])
    hrrs_to_print = ','.join([str(i) for i in hrr_w])

    #  ==================================================
    #  = Generate CFAST input file and fire object file =
    #  ==================================================

    if wall == 'CABSWConcrete':
        wall_matl = 'CABSWConcrete,CABSWConcrete,CABSWConcrete'

    outcase = template % {'simulation_time':simulation_time,
                          'dt_data':dt_data, 't_ambient': tmp_a+273.15,
                          'x':x, 'y':y, 'z':z, 'wall_matl':wall_matl,
                          'hoc':hoc*1000, 'time_ramp':times_to_print,
                          'hrr_ramp':hrrs_to_print}

    #  =====================
    #  = Write CFAST files =
    #  =====================

    casename = 'Cabinet Fire in Switchgear'
    filename = '../CFAST_Model/' + casename + '.in'

    # Opens a new file, writes the CFAST input file, and closes the file
    f = open(filename, 'w')
    f.write(outcase)
    f.close()

    return casename


def run_cfast(casename):
    """Run CFAST on case file."""

    # Run appropriate executable depending on operating system
    if op_sys == 'Linux':
        p = subprocess.Popen(['../CFAST_Model/cfast6_linux_64', '../CFAST_Model/' + casename])
        p.wait()
    if op_sys == 'Darwin':
        p = subprocess.Popen(['../CFAST_Model/cfast6_osx_64', '../CFAST_Model/' + casename])
        p.wait()
    if op_sys == 'Windows':
        p = subprocess.Popen(['../CFAST_Model/cfast6_win_64.exe', '../CFAST_Model/' + casename])
        p.wait()


def read_cfast(casename):
    """Read in CFAST output."""

    # CFAST filename - contents
    # casename_f.csv - flow data
    # casename_n.csv - fire effects
    # casename_s.csv - species
    # casename_w.csv - wall temperatures

    temperature_file = '../CFAST_Model/' + casename + '_n.csv'
    temps = np.genfromtxt(temperature_file, delimiter=',', skip_header=3)

    output_file = '../CFAST_Model/' + casename + '.out'
    outfile = open(output_file)

    return temps, outfile


def run_case(x, y, z, tmp_a, hoc, time_ramp, hrr_ramp, wall,
             simulation_time, dt_data):
    """
    Generate CFAST input file and call other functions
    """

    casename = gen_input(x, y, z, tmp_a, hoc, time_ramp, hrr_ramp, wall,
                         simulation_time, dt_data)

    run_cfast(casename)
    temps, outfile = read_cfast(casename)
    outfile.close()
    # Get final HGL temperature
    hgl = temps[:,1][-1]

    return(hgl)

