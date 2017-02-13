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
os.environ['HOME'] = '/home/koverholt/webapps/koverholt/cgi-media/hgl_temp'

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
SCRIPT_NAME = '/cgi-bin/hgl_temp/index_hgl_temp.cgi'
form = cgi.FieldStorage()

global resolution
resolution = ''

# Writes out html page templates and form fields
def print_html_header():
    HTML_TEMPLATE_HEAD = """<!DOCTYPE HTML>
    <html><head><title>Hot Gas Layer Temperature Calculator</title>
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
    HTML_XDIM = """<br/>
    <b>Fire parameters</b><br/><br/>

    <blockquote>
    <label>Maximum fire size </label>
    <input class="input-small" name="sel_q_value" type="text" size="4" value="300"> kW
    </blockquote>

    <b>Time parameters</b><br/><br/>

    <blockquote>
    <label>Time </label>
    <input class="input-small" name="sel_time" type="text" size="4" value="300"> s
    </blockquote>

    <b>Ventilation parameters</b><br/><br/>

    <blockquote>
    <label>Vent width </label>
    <input class="input-small" name="sel_vent_width" type="text" size="4" value="0.8"> m
    <br/><br/>
    <label>Vent height </label>
    <input class="input-small" name="sel_vent_height" type="text" size="4" value="2.0"> m
    </blockquote>

    <b>Compartment parameters</b><br/><br/>

    <blockquote>
    <label>Room length </label>
    <input class="input-small" name="sel_room_length" type="text" size="4" value="3.6"> m
    <br/><br/>
    <label>Room width </label>
    <input class="input-small" name="sel_room_width" type="text" size="4" value="2.4"> m
    <br/><br/>
    <label>Room height </label>
    <input class="input-small" name="sel_room_height" type="text" size="4" value="2.4"> m
    <br/><br/>
    <label>Ambient temperature </label>
    <input class="input-small" name="sel_T_amb" type="text" size="4" value="20"> &deg;C
    </blockquote>

    <b>Wall parameters</b><br/><br/>

    <blockquote>
    <label>Wall thickness </label>
    <input class="input-small" name="sel_wall_thickness" type="text" size="4" value="0.016"> m
    <br/><br/>
    <label>Wall thermal conductivity </label>
    <input class="input-small" name="sel_wall_k" type="text" size="4" value="0.48"> W/m-K
    <br/><br/>
    <label>Wall specific heat </label>
    <input class="input-small" name="sel_wall_cp" type="text" size="4" value="840"> J/kg-K
    <br/><br/>
    <label>Wall density </label>
    <input class="input-small" name="sel_wall_rho" type="text" size="4" value="1440"> kg/m<sup>3</sup>
    </blockquote>
    """

    DSTAR_INPUT = """<table border=0>
    <tr><td colspan=3 align='right'><br/><input class="btn btn-large btn-primary" name="submit" type="submit" value="Calculate HGL temperatures"></td></td></table><br/><br/>
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
        sel_vent_width = form["sel_vent_width"].value
        sel_vent_height = form["sel_vent_height"].value
        sel_room_length = form["sel_room_length"].value
        sel_room_width = form["sel_room_width"].value
        sel_room_height = form["sel_room_height"].value
        sel_T_amb = form["sel_T_amb"].value
        sel_wall_thickness = form["sel_wall_thickness"].value
        sel_wall_k = form["sel_wall_k"].value
        sel_wall_rho = form["sel_wall_rho"].value
        sel_wall_cp = form["sel_wall_cp"].value
        sel_time = form["sel_time"].value
    except:
        print_html_footer()
        sys.exit()

    # Writes fields and values to lists for input looping
    global input_fields
    global input_values
    input_fields = ("sel_q_value", "sel_vent_width", "sel_vent_height", "sel_room_length", "sel_room_width", "sel_room_height", "sel_T_amb", "sel_wall_thickness", "sel_wall_k", "sel_wall_rho", "sel_wall_cp", "sel_time")
    input_values = (sel_q_value, sel_vent_width, sel_vent_height, sel_room_length, sel_room_width, sel_room_height, sel_T_amb, sel_wall_thickness, sel_wall_k, sel_wall_rho, sel_wall_cp, sel_time)

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
    sel_vent_width = float(sel_vent_width)
    sel_vent_height = float(sel_vent_height)
    sel_room_length = float(sel_room_length)
    sel_room_width = float(sel_room_width)
    sel_room_height = float(sel_room_height)
    sel_T_amb = float(sel_T_amb)
    sel_wall_thickness = float(sel_wall_thickness)
    sel_wall_k = float(sel_wall_k)
    sel_wall_rho = float(sel_wall_rho)
    sel_wall_cp = float(sel_wall_cp)
    sel_time = float(sel_time)

    Q = float(sel_q_value)
    W_o = float(sel_vent_width)
    H_o = float(sel_vent_height)
    L = float(sel_room_length)
    W = float(sel_room_width)
    H = float(sel_room_height)
    T_inf = sel_T_amb
    delta = float(sel_wall_thickness)
    k = float(sel_wall_k)
    rho = float(sel_wall_rho)
    cp = float(sel_wall_cp)
    t = float(sel_time)

    hrrs = np.arange(Q + 1)

    # Calculate thermal diffusivity
    alpha = k / (rho * cp)

    # Calculate thermal penetration time
    t_p = delta**2 / (4 * alpha)

    # Calculate ventilation area (m2)
    A_o = W_o * H_o

    # Calculate effective heat transfer coefficient
    if t < t_p:
        h_k = np.sqrt(k * rho * cp / t) / 1000
    elif t >= t_p:
        h_k = (k / delta) / 1000

    A_T = (2 * L * W) + (2 * L * H) + (2 * W * H) - (A_o)

    Delta_T = 6.85 * (hrrs**2 / (A_o * np.sqrt(H_o) * h_k * A_T))**(1/3)

    T_g = Delta_T + T_inf

    print '<h3>Results:</h3><br/>'

    print 'Wall thermal penetration time: <b>%i s</b>' % t_p

    print '<br/>'

    if t < t_p:
        print 'Therefore, <b>t < t_p</b>'
    elif t >= t_p:
        print 'Therefore, <b>t >= t_p</b>'

    print '<br/>'

    print 'Effective heat transfer coefficient: <b>%0.4f kW/m<sup>2</sup>-K</b>' % h_k

    print '<br/>'

    print 'Total wall area: <b>%0.2f m<sup>2</sup></b>' % A_T

    print '<br/>'

    figure()
    plot(hrrs, T_g, lw=2)
    title('HGL temperature vs. HRR at %i seconds' % t, fontsize=14)
    # axhline(600, ls='--', color='black')
    xlabel('HRR (kW)', fontsize=16)
    ylabel('HGL Temperature ($^\circ$C)', fontsize=16)
    grid(True)
    ax = gca()
    for xlabel_i in ax.get_xticklabels():
        xlabel_i.set_fontsize(14)
    for ylabel_i in ax.get_yticklabels():
        ylabel_i.set_fontsize(14)
    savestring = "../../cgi-media/hgl_temp/hgl_tmps%i.png" % np.random.randint(10000000)
    savefig(savestring, dpi=80)

    print "<img src='%s'><br/>" % savestring

    print "<br/>"
    print "<table>"
    print "<tr><td><b>HRR (kW) </b></td><td><b> HGL Temperature (&deg;C)</b></td></tr>"
    for i in range(0, len(hrrs), 10):
        print "<tr><td>%i </td><td> %i</td></tr>" % (np.round(hrrs[i]), np.round(T_g[i]))
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
    path = '../../cgi-media/hgl_temp'
    now = time.time()
    for f in os.listdir(path):
        fullpath = path + "/" + f
        if 'hgl_tmps' and '.png' in f:
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
