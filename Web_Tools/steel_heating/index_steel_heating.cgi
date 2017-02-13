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
os.environ['HOME'] = '/home/koverholt/webapps/koverholt/cgi-media/steel_heating'

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
SCRIPT_NAME = '/cgi-bin/steel_heating/index_steel_heating.cgi'
form = cgi.FieldStorage()

global resolution
resolution = ''

# Writes out html page templates and form fields
def print_html_header():
    HTML_TEMPLATE_HEAD = """<!DOCTYPE HTML>
    <html><head><title>Calculator for Transient Steel Heating Under Fire Conditions</title>
    <meta http-equiv="Content-Type" content="text/html; charset=iso-8859-1">

    <script type="text/javascript" src="../../cgi-media/jquery.js"></script>

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
    HTML_XDIM = """<br/>
    Simulation time <input class="input-small" name="sel_time_value" type="text" size="4" value="3"> hours<br/><br/>

    <b>Steel parameters</b><br/><br/>

    <blockquote>
    <label>Section factor </label>
    <input class="input-small" name="sel_FV_value" type="text" size="4" value="200"> 1/m <br/>
    <label>Density </label>
    <input class="input-small" name="sel_rho_s_value" type="text" size="4" value="7850"> kg/m<sup>3</sup><br/>
    <label>Specific heat </label>
    <input class="input-small" name="sel_c_s_value" type="text" size="4" value="600"> J/kg-K<br/>
    <label>Emissivity </label>
    <input class="input-small" name="sel_eps_value" type="text" size="4" value="0.6">
    </blockquote>

    <b>Fire parameters</b><br/><br/>

    <blockquote>
    <label>Fire curve </label>
    <select name="sel_fire_curve">
    <option value="1">ISO 834</option>
    <option value="2">ASTM E119</option>
    </select>

    <br/>

    <label>Heat transfer coefficent </label>
    <input class="input-small" name="sel_h_value" type="text" size="4" value="25"> W/m<sup>2</sup>-K
    </blockquote>

    <b>Insulation</b><br/><br/>

    <blockquote>
    <label>Steel protection? </label>
    <select name="sel_insulated_value">
    <option value="1">Unprotected</option>
    <option value="2">Protected</option>
    </select>

    <br/><br/>

    <div id="prot">

    If protected steel, then input the following:<br/><br/>

    <label>Thickness </label>
    <input class="input-small" name="sel_d_i_value" type="text" size="6" value="0.050"> m<br/>
    <label>Thermal conductivity </label>
    <input class="input-small" name="sel_k_i_value" type="text" size="6" value="0.2"> W/m-K<br/>
    <label>Density </label>
    <input class="input-small" name="sel_rho_i_value" type="text" size="6" value="150"> kg/m<sup>3</sup><br/>
    <label>Specific heat </label>
    <input class="input-small" name="sel_c_i_value" type="text" size="6" value="1200"> J/kg-K</div>

    </blockquote>"""

    DSTAR_INPUT = """<table border=0>
    <tr><td colspan=3 align='right'><br/><input class="btn btn-large btn-primary" name="submit" type="submit" value="Calculate transient steel temperature"></td></td></table><br/><br/>
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
        sel_FV_value = form["sel_FV_value"].value
        sel_rho_s_value = form["sel_rho_s_value"].value
        sel_c_s_value = form["sel_c_s_value"].value
        sel_eps_value = form["sel_eps_value"].value
        sel_fire_curve = form["sel_fire_curve"].value
        sel_h_value = form["sel_h_value"].value
        sel_insulated_value = form["sel_insulated_value"].value
        sel_d_i_value = form["sel_d_i_value"].value
        sel_k_i_value = form["sel_k_i_value"].value
        sel_rho_i_value = form["sel_rho_i_value"].value
        sel_c_i_value = form["sel_c_i_value"].value
        sel_time_value = form["sel_time_value"].value
    except:
        print_html_footer()
        sys.exit()

    # Writes fields and values to lists for input looping
    global input_fields
    global input_values
    input_fields = ("sel_FV_value", "sel_rho_s_value", "sel_c_s_value", "sel_eps_value", "sel_fire_curve", "sel_h_value", "sel_insulated_value", "sel_d_i_value", "sel_k_i_value", "sel_rho_i_value", "sel_c_i_value", "sel_time_value")
    input_values = (sel_FV_value, sel_rho_s_value, sel_c_s_value, sel_eps_value, sel_fire_curve, sel_h_value, sel_insulated_value, sel_d_i_value, sel_k_i_value, sel_rho_i_value, sel_c_i_value, sel_time_value)

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

    sel_FV_value = float(sel_FV_value)
    sel_rho_s_value = float(sel_rho_s_value)
    sel_c_s_value = float(sel_c_s_value)
    sel_eps_value = float(sel_eps_value)
    sel_fire_curve = float(sel_fire_curve)
    sel_h_value = float(sel_h_value)
    sel_insulated_value = float(sel_insulated_value)
    sel_d_i_value = float(sel_d_i_value)
    sel_k_i_value = float(sel_k_i_value)
    sel_rho_i_value = float(sel_rho_i_value)
    sel_c_i_value = float(sel_c_i_value)
    sel_time_value = float(sel_time_value)

    if sel_time_value >= 1000:
        print """<h2><font color="red">Simulation time must be less than 1,000 hours</font></h2><br/>"""
        fill_previous_values()
        sys.exit()
        count += 1

    # Choose fire time-temperature curve
    # 1 = ISO 834 curve
    # 2 = ASTM E119 curve
    fire_curve = sel_fire_curve

    # Input parameters
    t_end = sel_time_value # hours
    dt = 1/120 # hours

    # Input properties
    FV = sel_FV_value # 1/m
    rho_s = sel_rho_s_value # kg/m^3
    c_s = sel_c_s_value # J/kg-K
    h = sel_h_value # W/m^2-K
    sigma = 0.0000000567 # W/m^2-K^4
    epsilon = sel_eps_value # -

    # Insulation properties
    d_i = sel_d_i_value
    k_i = sel_k_i_value
    rho_i = sel_rho_i_value
    c_i = sel_c_i_value

    t = np.arange(0,t_end+dt,dt)

    t_half = t+dt/2

    T_steel = np.zeros(len(t)+1)
    dT_steel = np.zeros(len(t))
    T_steel[0] = 20

    T_steel_protected = np.zeros(len(t)+1)
    dT_steel_protected = np.zeros(len(t))
    T_steel_protected[0] = 20

    if fire_curve == 1:
        T_fire_half = 20 + 345 * np.log10(8*(t_half*60)+1)
        # print t_half*60, T_fire_half

    if fire_curve == 2:
        T_0 = 20
        T_fire_half = 750 * (1-np.exp(-3.79553*np.sqrt(t_half))) + 170.41*(np.sqrt(t_half)) + T_0
        # print t_half*60, T_fire_half

    # dT = np.array([])
    # dT = T_fire_half - T_steel

    for i in range(0,len(t)):
        dT_steel[i] = FV * 1/(rho_s * c_s) * (h*(T_fire_half[i] - T_steel[i]) + epsilon*sigma*((T_fire_half[i]+273)**4 - (T_steel[i]+273)**4)) * (dt*3600)
        T_steel[i+1] = T_steel[i] + dT_steel[i]

    if sel_insulated_value == 2:
        for i in range(0,len(t)):
            dT_steel_protected[i] = FV * (k_i/(d_i*rho_s*c_s)) * (rho_s*c_s / (rho_s*c_s + (FV*d_i*rho_i*c_i) / 2)) * (T_fire_half[i] - T_steel_protected[i]) * (dt*3600)
            T_steel_protected[i+1] = T_steel_protected[i] + dT_steel_protected[i]

    # print dT_steel

    figure()

    if sel_insulated_value == 2:
        plot(t, T_steel_protected[:-1], 'b-', lw=2, label="Protected")
        plot(t, T_steel[:-1], 'r--', lw=2, label="Unprotected")
        legend(loc=0)
    else:
        plot(t, T_steel[:-1], 'r-' ,lw=2)

    axhline(y=600, color='black', ls='--')
    title('Steel temperature vs. time', fontsize=18)
    xlabel('Time (hours)', fontsize=18)
    ylabel('Temperature ($^\circ$C)', fontsize=18)
    grid(True)
    ax = gca()
    for xlabel_i in ax.get_xticklabels():
        xlabel_i.set_fontsize(14)
    for ylabel_i in ax.get_yticklabels():
        ylabel_i.set_fontsize(14)
    savestring = "../../cgi-media/steel_heating/steel%i.png" % np.random.randint(10000000)
    savefig(savestring, dpi=80)

    print "<img src='%s'><br/>" % savestring

    # if sel_print_info == "1":

    if sel_insulated_value == 1:
        print "<br/>"
        print "Unprotected steel temperatures:<br/><br/>"
        print "<table>"
        print "<tr><td><b>Time (min) </b></td><td> <b>Temp (&deg;C)</b></td></tr>"
        for i in range(0,len(t)):
            print "<tr><td>%0.1f </td><td> %0.2f</td></tr>" % (t[i]*60, T_steel[i])
        print "</table>"

    if sel_insulated_value == 2:
        print "<br/>"
        print "Unprotected vs. protected steel temperatures:<br/><br/>"
        print "<table>"
        print "<tr><td>Time (min) </td><td> Unprotected Temp. (&deg;C)</td><td> Protected Temp. (&deg;C)</td></tr>"
        for i in range(0,len(t)):
            print "<tr><td>%0.1f </td><td> %0.2f</td><td> %0.2f</td></tr>" % (t[i]*60, T_steel[i], T_steel_protected[i])
        print "</table>"
        print "<br/><br/>"

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
    path = '../../cgi-media/steel_heating'
    now = time.time()
    for f in os.listdir(path):
        fullpath = path + "/" + f
        if 'steel' and '.png' in f:
            if os.stat(fullpath).st_mtime < now - 3600:
                if os.path.isfile(fullpath):
                    os.remove(fullpath)

###############################################################
#  Actual start of execution of script using above functions  #
###############################################################

print_html_header()

print_html_body()

check_input_fields()

js_form_textbox_red = """<script type="text/javascript">
document.getElementById("x0_dim").style.color="red";
</script>"""

js_form_textbox_red_2 = """<script type="text/javascript">
x0_dim.style.backgroundColor = "#FF0000";
</script>"""

print js_form_textbox_red_2
# print_output_results()

fill_previous_values()

print_html_footer()
