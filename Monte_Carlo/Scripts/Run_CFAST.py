#!/usr/bin/env python

"""Module for CFAST functions"""

from functools import wraps
import numpy as np
import platform
import subprocess
import os
import errno
import signal

# Detect operating system
op_sys = platform.system()

# ===========================================================
# = Timeout structure for CFAST runs that hang (UNIX) only  =
# ===========================================================


class TimeoutError(Exception):
    pass


def timeout(seconds=5, error_message=os.strerror(errno.ETIME)):
    """Check for CFAST timeout (stalled run)."""
    def decorator(func):
        def _handle_timeout(signum, frame):
            raise TimeoutError(error_message)

        def wrapper(*args, **kwargs):
            signal.signal(signal.SIGALRM, _handle_timeout)
            signal.setitimer(signal.ITIMER_REAL, seconds)
            try:
                result = func(*args, **kwargs)
            finally:
                signal.alarm(0)
            return result

        return wraps(func)(wrapper)

    return decorator


def gen_input(x, y, z, door_height, door_width,
              t_amb, HoC, time_ramp, hrr_ramp,
              num, door, wall, simulation_time, dt_data):
    """
    Generate CFAST input file and initialize HRR arrays

    Keyword arguments:
    x -- x dimension of compartment
    y -- y dimension of compartment
    z -- z dimension of compartment
    time_ramp -- time portion of HRR curve of fire
    hrr_ramp -- heat release rate portion of HRR curve
    num -- number index (ID) of fire in CFAST, 1 for a single fire
    door -- status of door, Open or Closed
    simulation_time -- length of time to run the simulation
    dt_data -- Data sampling rate and CFAST output frequency
    """

    #  =============================
    #  = CFAST input file template =
    #  =============================

    template = """VERSN,6,CFAST Simulation
!!
!!Scenario Configuration Keywords
!!
TIMES,%(simulation_time)s,-50,0,10,%(dt_data)s
EAMB,%(t_ambient)s,101300,0
TAMB,%(t_ambient)s,101300,0,50
CJET,WALLS
WIND,0,10,0.16
!!
!!Material Properties
!!
MATL,FIBERBRD,0.041,2090,229,0.016,0.9,Fiber Insulating Board
MATL,GYPSUM,0.16,900,790,0.016,0.9,Gypsum Board (5/8 in)
MATL,METHANE,0.07,1090,930,0.0127,0.04,"Methane, a transparent gas (CH4)"
!!
!!Compartment keywords
!!
COMPA,Compartment 1,%(x)s,%(y)s,%(z)s,0,0,0,%(wall_matl)s
!!
%(door_open)s!!Fire keywords
!!fire
FIRE,%(num)s,1.8,1.2,0,1,1,0,0,0,1,fire
CHEMI,6,10,5,0,0,0.37,%(HoC)s,METHANE
TIME,%(time_ramp)s
HRR,%(hrr_ramp)s
SOOT,0.015,0.015,0.015,0.015,0.015,0.015,0.015,0.015,0.015,0.015,0.015,0.015,0.015,0.015,0.015,0.015,0.015,0.015,0.015,0.015
CO,0.006171682,0.006171682,0.006171682,0.006171682,0.006171682,0.006171682,0.006171682,0.006171682,0.006171682,0.006171682,0.006171682,0.006171682,0.006171682,0.006171682,0.006171682,0.006171682,0.006171682,0.006171682,0.006171682,0.006171682
TRACE,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0
AREA,0.5,0.5,0.5,0.5,0.5,0.5,0.5,0.5,0.5,0.5,0.5,0.5,0.5,0.5,0.5,0.5,0.5,0.5,0.5,0.5
HEIGH,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0
"""

    # Convert HRR from kW to W
    hrr_w = hrr_ramp * 1000

    # Format arrays as comma separated lists for CFAST input file
    times_to_print = ','.join([str(i) for i in time_ramp])
    hrrs_to_print = ','.join([str(i) for i in hrr_w])

    #  ==================================================
    #  = Generate CFAST input file and fire object file =
    #  ==================================================

    if wall == 'gypsum':
        wall_matl = 'GYPSUM,OFF,GYPSUM'
    elif wall == 'fiberboard':
        wall_matl = 'FIBERBRD,OFF,FIBERBRD'
    door_vent = """!!Vent keywords
!!
HVENT,1,2,1,%(door_width)s,%(door_height)s,0,1,0,0,1,1
""" % {'door_height':door_height, 'door_width':door_width}

    if door == 'Closed':
        outcase = template % {'simulation_time':simulation_time,
                              'dt_data':dt_data, 't_ambient': t_amb+273.15,
                              'x':x, 'y':y, 'z':z, 'wall_matl':wall_matl,
                              'num':num, 'door_open':'', 'HoC':HoC*1000,
                              'time_ramp':times_to_print,
                              'hrr_ramp':hrrs_to_print}
    elif door == 'Open':
        outcase = template % {'simulation_time':simulation_time,
                              'dt_data':dt_data, 't_ambient': t_amb+273.15,
                              'x':x, 'y':y, 'z':z, 'wall_matl':wall_matl,
                              'num':num, 'door_open':door_vent, 'HoC':HoC*1000,
                              'time_ramp':times_to_print,
                              'hrr_ramp':hrrs_to_print}

    #  =====================
    #  = Write CFAST files =
    #  =====================

    casename = 'case'
    filename = '../../../CFAST_Model/' + casename + '.in'

    # Opens a new file, writes the CFAST input file, and closes the file
    f = open(filename, 'w')
    f.write(outcase)
    f.close()

    return casename


@timeout(5)
def run_cfast(casename):
    """Run CFAST on case file."""
    global hangerror

    # Run appropriate executable depending on operating system
    try:
        if op_sys == 'Linux':
            p = subprocess.Popen(['../../../CFAST_Model/cfast6_linux_64', '../../../CFAST_Model/' + casename])
            p.wait()
        if op_sys == 'Darwin':
            p = subprocess.Popen(['../../../CFAST_Model/cfast6_osx_64', '../../../CFAST_Model/' + casename])
            p.wait()
        if op_sys == 'Windows':
            p = subprocess.Popen(['../../../CFAST_Model/cfast6_win.exe', '../../../CFAST_Model/' + casename])
            p.wait()
    except Exception:
        hangerror = 1
        p.kill()
        print "CFAST has hung up!"


def read_cfast(casename):
    """Read in CFAST output."""

    # CFAST filename - contents
    # casename_f.csv - flow data
    # casename_n.csv - fire effects
    # casename_s.csv - species
    # casename_w.csv - wall temperatures

    temperature_file = '../../../CFAST_Model/' + casename + '_n.csv'
    temps = np.genfromtxt(temperature_file, delimiter=',', skip_header=3)

    output_file = '../../../CFAST_Model/' + casename + '.out'
    outfile = open(output_file)

    return temps, outfile


def run_multiple_cases(x, y, z, door_height, door_width, t_amb,
                       HoC, time_ramp, hrr_ramp, num, door, wall,
                       simulation_time, dt_data):
    """
    Generate multiple CFAST input files and calls other functions
    """

    resulting_temps = np.array([])

    for i in range(len(door_width)):
        casename = gen_input(x, y, z, door_height[i], door_width[i],
                  t_amb[i], HoC, time_ramp, hrr_ramp, num, door,
                  wall, simulation_time, dt_data)

        run_cfast(casename)
        temps, outfile = read_cfast(casename)
        outfile.close()
        hgl = temps[:,1]
        resulting_temps = np.append(hgl[-1], resulting_temps)

    return(resulting_temps)

