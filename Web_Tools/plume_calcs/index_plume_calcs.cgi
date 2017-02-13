#!/home/koverholt/anaconda/bin/python

# LICENSE
#
# Copyright (c) 2012 Kristopher Overholt
#
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in
# all copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN
# THE SOFTWARE.

from __future__ import division

import os
os.environ['HOME'] = '/home/koverholt/webapps/koverholt/cgi-media/plume_calcs'

import numpy as np
from decimal import *
from math import sqrt
import cgi, sys, time

import matplotlib
matplotlib.use("Agg")
from pylab import *

import cgitb
cgitb.enable()

# Variables to script path and that gather form fields
SCRIPT_NAME = '/cgi-bin/plume_calcs/index_plume_calcs.cgi'
form = cgi.FieldStorage()

global resolution
resolution = ''

# Writes out html page templates and form fields
def print_html_header():
    HTML_TEMPLATE_HEAD = """<!DOCTYPE HTML>
    <html><head><title>Flame Height and Plume Centerline Temperature Calculator</title>
    <meta http-equiv="Content-Type" content="text/html; charset=iso-8859-1">

    <!-- Le styles -->
    <link href="../bootstrap/css/bootstrap.css" rel="stylesheet">
    <style type="text/css">
      body {
        padding-top: 60px;
        padding-bottom: 40px;
      }
    </style>
    <link href="../bootstrap/css/bootstrap-responsive.css" rel="stylesheet">

    <!-- Le HTML5 shim, for IE6-8 support of HTML5 elements -->
    <!--[if lt IE 9]>
      <script src="http://html5shim.googlecode.com/svn/trunk/html5.js"></script>
    <![endif]-->

    </head><body>
    <h3><FONT FACE="Arial, Helvetica, Geneva"><font color="darkred">Enter the input parameters </font></h3>
    <form action="%(SCRIPT_NAME)s" method="POST" enctype="multipart/form-data">"""
    print "Content-type: text/html\n"
    print HTML_TEMPLATE_HEAD % {'SCRIPT_NAME':SCRIPT_NAME}


def print_html_body():
    HTML_XDIM = """<br/><b>Fire parameters</b><br/><br/>

    <label>Fire size </label>
    <input class="input-small" name="sel_q_value" type="text" size="4" value="400"> kW <br/><br/>

    <label>Fire diameter </label>
    <input class="input-small" name="sel_D_value" type="text" size="4" value="1"> m <br/><br/>

    <label>Radiative fraction </label>
    <input class="input-small" name="sel_X_r_value" type="text" size="4" value="0.3"> -
    """

    DSTAR_INPUT = """<table border=0>
    <tr><td colspan=3 align='right'><br/><input class="btn btn-large btn-primary" name="submit" type="submit" value="Calculate plume characteristics"></td></td></table><br/>
    """

    print HTML_XDIM
    print DSTAR_INPUT

def print_html_footer():
    HTML_TEMPLATE_FOOT = """</font>
    </form>
    </body>
    </html>"""
    print HTML_TEMPLATE_FOOT

def check_input_fields():

    try:
        sel_q_value = form["sel_q_value"].value
        sel_D_value = form["sel_D_value"].value
        sel_X_r_value = form["sel_X_r_value"].value
    except:
        print_html_footer()
        sys.exit()

    # Writes fields and values to lists for input looping
    global input_fields
    global input_values
    input_fields = ("sel_q_value", "sel_D_value", "sel_X_r_value")
    input_values = (sel_q_value, sel_D_value, sel_X_r_value)

    # Loops through input values to check for empty fields and returns an error if so
    count = 0
    for field in input_values:
        if field == "":
            print """<h2><font color="red">""" + input_fields[count] + """ was not specified</font></h2><br/>"""
            fill_previous_values()
            sys.exit()
        count += 1

    # Check to see if all inputs are valid numbers (by attempting to convert each one to a float)
    # If not, it will exit and fill the previous values
    count = 0
    # for field in input_values:
    try:
        for field in input_values:
            if field == "on":
                break
            float(field)
            count += 1
    except:
        print """<h2><font color="red">""" + input_fields[count] + """ is not a valid number</font></h2><br/>"""
        fill_previous_values()
        sys.exit()
        count += 1

    sel_q_value = float(sel_q_value)
    sel_D_value = float(sel_D_value)
    sel_X_r_value = float(sel_X_r_value)

    D = sel_D_value # m
    Q = sel_q_value # kW
    X_r = sel_X_r_value

    #  =================================
    #  = Plume temperature calculation =
    #  =================================

    Q_c = (1-X_r) * Q
    z_0 = 0.083 * Q**(2/5) -1.02 * D
    L = -1.02 * D + 0.235*(Q**(2/5))
    above_flame = 5*L

    z = np.arange(L+L*0.3,L+above_flame,(L+above_flame)/50)
    delta_T_0_hes = np.zeros(len(z))
    delta_T_0_mcc = np.zeros(len(z))

    for height in range(0,len(z)):
        delta_T_0_hes[height] = 25 * (Q_c**(2/5)/(z[height]-z_0))**(5/3) + 20

    for height in range(0,len(z)):
        delta_T_0_mcc[height] = 22.3 * (Q**(2/5)/(z[height]))**(5/3) + 20

    #  ======================
    #  = Q_star calculation =
    #  ======================

    # Density (kg/m3)
    rho = 1.204

    # Specific heat (kJ/kg-K)
    c_p = 1.005

    # Ambient temperature (K)
    T_inf = 293

    # Gravitational acceleration
    g = 9.81

    Q_star = Q / (rho * c_p * T_inf * np.sqrt(g*D) * D**2)

    #  =================
    #  = Print results =
    #  =================

    print "<h3>Nondimensional HRR:</h3><br/>"
    print "The characteristic fire size (Q<sup>*</sup>) is <b>" + str(np.round(Q_star, 3)) + "</b><br/><br/>"

    print "<h3>Heskestad Flame Height:</h3><br/>"
    print "&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;For a", int(Q), "kW fire with a diameter of", D, "m:<br/><br/>"
    print "&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;The flame height is <b>" + str(np.round(L,2)) + " m (" + str(np.round(L*3.28,2)) + " ft)</b><br/><br/>"

    print "<h3>Heskestad and McCaffrey Plume Centerline Temperatures:</h3>"
    figure()
    plot(z, delta_T_0_mcc, lw=2, label='McCaffrey')
    plot(z, delta_T_0_hes, lw=2, label='Heskestad')
    title('Plume centerline temperatures (above flame) vs. height', fontsize=14)
    axvline(L, ls='--', color='black')
    xlabel('Height (m)', fontsize=16)
    ylabel('Plume Centerline Temperature ($^\circ$C)', fontsize=16)
    xlim([0, L+above_flame])
    ylim([0, np.max([delta_T_0_hes[0], delta_T_0_mcc[0]]) + (50-np.max([delta_T_0_hes[0], delta_T_0_mcc[0]]) % 50)])
    legend()
    grid(True)
    ax = gca()
    for xlabel_i in ax.get_xticklabels():
        xlabel_i.set_fontsize(14)
    for ylabel_i in ax.get_yticklabels():
        ylabel_i.set_fontsize(14)
    savestring = "../../cgi-media/plume_calcs/cl_tmps%i.png" % np.random.randint(10000000)
    savefig(savestring, dpi=80)

    print "<img src='%s'><br/>" % savestring

    print "<br/>"
    print "Plume centerline temperatures (above flame):<br/><br/>"
    print "<table>"
    print "<tr><td><b>Height (m) </b></td><td><b> Heskestad Temp. (&deg;C)</b></td><td> <b>McCaffrey Temp. (&deg;C)</b></td></tr>"
    for i in range(0,len(z)):
        print "<tr><td>%0.2f </td><td> %0.0f</td><td> %0.0f</td></tr>" % (z[i], delta_T_0_hes[i], delta_T_0_mcc[i])
    print "</table>"

    delete_old_files()

def fill_previous_values():
    js_form_fill = """<script type="text/javascript">
          document.forms[0].%(FORM_ELEMENT_NAME)s.value = '%(FORM_VALUE)s';
          </script>"""
    # Loops through form fields and writes out a custom javascript line for each element
    # to keep the previously typed number in the form
    form_count = 0
    for field in input_values:
        print js_form_fill % {'FORM_ELEMENT_NAME':input_fields[form_count], 'FORM_VALUE':field}
        form_count += 1

def delete_old_files():
    ### Delete old plot files older than 1 hour ###
    path = '../../cgi-media/plume_calcs'
    now = time.time()
    for f in os.listdir(path):
        fullpath = path + "/" + f
        if 'cl_tmps' and '.png' in f:
            if os.stat(fullpath).st_mtime < now - 3600:
                if os.path.isfile(fullpath):
                    os.remove(fullpath)


###############################################################
#  Actual start of execution of script using above functions  #
###############################################################

print_html_header()

print_html_body()

check_input_fields()

fill_previous_values()

js_form_textbox_red = """<script type="text/javascript">
document.getElementById("x0_dim").style.color="red";
</script>"""

js_form_textbox_red_2 = """<script type="text/javascript">
x0_dim.style.backgroundColor = "#FF0000";
</script>"""

print js_form_textbox_red_2
# print_output_results()

print_html_footer()
