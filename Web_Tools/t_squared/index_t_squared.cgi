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
os.environ['HOME'] = '/home/koverholt/webapps/koverholt/cgi-media/t_squared'

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
SCRIPT_NAME = '/cgi-bin/t_squared/index_t_squared.cgi'
form = cgi.FieldStorage()

global resolution
resolution = ''

# Writes out html page templates and form fields
def print_html_header():
    HTML_TEMPLATE_HEAD = """<!DOCTYPE HTML>
    <html><head><title>t-squared Fire Ramp Calculator</title>
    <meta http-equiv="Content-Type" content="text/html; charset=iso-8859-1">

    <script type="text/javascript" src="../../cgi-media/jquery.js"></script>

    <style type="text/css">
    .table1 {
        padding-left: 20px
    }
    </style>

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
    <h3><FONT FACE="Arial, Helvetica, Geneva"><font color="darkred">Select input parameters </font></h3>
    <form action="%(SCRIPT_NAME)s" method="POST" enctype="multipart/form-data">"""
    print "Content-type: text/html\n"
    print HTML_TEMPLATE_HEAD % {'SCRIPT_NAME':SCRIPT_NAME}


def print_html_body():
    HTML_XDIM = """<br/><b>Fire growth coefficient</b><br/><br/>

    <blockquote>
    <label><input type="radio" name="sel_alpha_value" value="option1" id="option1" checked>&nbsp;Slow: 0.00293 kW/s<sup>2</sup></label>
    <label><input type="radio" name="sel_alpha_value" value="option2" id="option2">&nbsp;Medium: 0.01172 kW/s<sup>2</sup></label>
    <label><input type="radio" name="sel_alpha_value" value="option3" id="option3">&nbsp;Fast: 0.0469 kW/s<sup>2</sup></label>
    <label><input type="radio" name="sel_alpha_value" value="option4" id="option4">&nbsp;Ultrafast: 0.1876 kW/s<sup>2</sup></label>
    <label><input type="radio" name="sel_alpha_value" value="other" id="other">&nbsp;Custom:</label>
    <label><input class="input-small" type="text" name="sel_custom_alpha_value" size="10"> kW/s<sup>2</sup></label>
    </blockquote>

    <br/>

    <b>Fire parameters</b><br/><br/>

    <blockquote>Select when the t-squared fire ramp should stop:

    <br/><br/>

    <label><input type="radio" name="sel_stopping_value" value="opt1" id="opt1" checked>
    &nbsp;Maximum HRR:&nbsp;</label><input class="input-small" type="text" name="sel_hrr_value" size="10" value="300">
     kW
    <label><input type="radio" name="sel_stopping_value" value="opt2" id="opt2">
    &nbsp;Maximum time:&nbsp;</label><input class="input-small" type="text" name="sel_time_value" size="10" value="320">
     s
    </blockquote>

    <br/>

    <b>Additional output parameters (optional)</b><br/><br/>

    <blockquote>
    Select additional outputs:

    <br/><br/>

    <label><input type="checkbox" name="sel_save1_value" value="save1" id="save1">
    &nbsp;Downloadable CSV file </label>
    <label><input type="checkbox" name="sel_save2_value" value="save2" id="save2">
    &nbsp;FDS HRR ramp text </label>
    &nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;FDS HRR vent size:
    <input class="input-small" type="text" name="sel_fds_1" size="4" value="1"> m x
    <input class="input-small" type="text" name="sel_fds_2" size="4" value="1"> m
    </blockquote>
    """

    DSTAR_INPUT = """<table border=0>
    <tr><td colspan=3 align='right'><br/><input class="btn btn-large btn-primary" name="submit" type="submit" value="Calculate t-squared fire ramp"></td></td></table><br/><br/>
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

    global sel_alpha_value, sel_stopping_value

    try:
        sel_alpha_value = form["sel_alpha_value"].value
        sel_custom_alpha_value = form["sel_custom_alpha_value"].value
        sel_stopping_value = form["sel_stopping_value"].value
        sel_hrr_value = form["sel_hrr_value"].value
        sel_time_value = form["sel_time_value"].value
        sel_fds_1 = form["sel_fds_1"].value
        sel_fds_2 = form["sel_fds_2"].value
    except:
        print_html_footer()
        sys.exit()

    # Writes fields and values to lists for input looping
    global input_fields
    global input_values
    input_fields = ("sel_alpha_value", "sel_custom_alpha_value", "sel_stopping_value", "sel_hrr_value", "sel_time_value", "sel_fds_1", "sel_fds_2")
    input_values = (sel_alpha_value, sel_custom_alpha_value, sel_stopping_value, sel_hrr_value, sel_time_value, sel_fds_1, sel_fds_2)

    if sel_alpha_value == "":
        print """<h2><font color="red">Please select a fire growth coefficient</font></h2><br/>"""
        fill_previous_values()
        sys.exit()

    if sel_stopping_value == "":
        print """<h2><font color="red">Please select a stopping criteria</font></h2><br/>"""
        fill_previous_values()
        sys.exit()

    # ==================
    # = Error checking =
    # ==================

    if sel_stopping_value == 'opt1':
        try:
            float(sel_hrr_value)
        except ValueError:
            print """<h2><font color="red">Please input a valid maximum HRR</font></h2><br/>"""
            fill_previous_values()
            sys.exit()

    if sel_stopping_value == 'opt2':
        try:
            float(sel_time_value)
        except ValueError:
            print """<h2><font color="red">Please input a valid maximum time</font></h2><br/>"""
            fill_previous_values()
            sys.exit()


    if sel_alpha_value == 'other':
        try:
            float(sel_custom_alpha_value)
        except ValueError:
            print """<h2><font color="red">Please input a valid custom alpha parameter</font></h2><br/>"""
            fill_previous_values()
            sys.exit()

    try:
        form["sel_save2_value"].value

        try:
            float(sel_fds_1)
            float(sel_fds_2)
        except ValueError:
            print """<h2><font color="red">Please input valid FDS fire vent dimensions</font></h2><br/>"""
            fill_previous_values()
            sys.exit()

        sel_fds_1 = float(sel_fds_1)
        sel_fds_2 = float(sel_fds_2)

        fds_fire_ramp_area = sel_fds_1 * sel_fds_2
    except KeyError:
        pass

    if sel_hrr_value != "":
        sel_hrr_value = float(sel_hrr_value)
    if sel_time_value != "":
        sel_time_value = float(sel_time_value)
    if sel_custom_alpha_value != "":
        sel_custom_alpha_value = float(sel_custom_alpha_value)

    # Set maximum bounds
    if sel_time_value > 99999.0:
        sel_time_value = 99999.0
    if sel_hrr_value > 99999.0:
        sel_hrr_value = 99999.0

    # ==============
    # = Set values =
    # ==============

    if sel_alpha_value == "option1":
        alpha = 0.00293
        title_alpha = "(slow growth)"
    if sel_alpha_value == "option2":
        alpha = 0.01172
        title_alpha = "(medium growth)"
    if sel_alpha_value == "option3":
        alpha = 0.0469
        title_alpha = "(fast growth)"
    if sel_alpha_value == "option4":
        alpha = 0.1876
        title_alpha = "(ultrafast growth)"
    if sel_alpha_value == "other":
        alpha = sel_custom_alpha_value
        title_alpha = r"($\alpha$ = %0.4f kW/s$^2$)" % alpha

    # ============================
    # = Calculate t-squared ramp =
    # ============================

    if sel_stopping_value == "opt1":
        max_time = np.ceil(np.sqrt(sel_hrr_value / alpha))
        time = np.arange(max_time + 1)
        hrr = alpha * time**2

        print "<h2>Results:</h2><br/>"
        print "<h3>"
        print str(int(sel_hrr_value)) + ' kW is attained at a time of ' + str(int(max_time)) + ' seconds'
        print "</h3>"

    elif sel_stopping_value == "opt2":
        time = np.arange(sel_time_value + 1)
        hrr = alpha * time**2
        max_time = np.max(time)
        max_hrr = alpha * max_time**2

        print "<h2>Results:</h2>"
        print "<h3>"
        print str(int(max_hrr)) + ' kW is attained at a time of ' + str(int(max_time)) + ' seconds'
        print "</h3>"

    jobid = np.random.randint(10000000)

    # ====================================
    # = Save .csv file for user download =
    # ====================================

    try:
        form["sel_save1_value"].value
        header_rows = np.array([['alpha', alpha], ['Time (s)', 'HRR (kW)']])
        output_data = np.column_stack([time, hrr])
        csv_output = np.row_stack([header_rows, output_data])
        csv_output = csv_output.tolist()

        csv_filename = '../../cgi-media/t_squared/case%i.csv' % jobid

        for n in range(len(csv_output)):
            outstring = csv_output[n] + ['\n']
            stats(csv_filename, ','.join(outstring))

        print "<a href='%s'>Download CSV file</a><br/><br/>" % csv_filename
    except KeyError:
        pass

    # ===================================
    # = Save .fds text for FDS HRR ramp =
    # ===================================

    try:
        form["sel_save2_value"].value

        time_list = np.arange(0, np.max(time) + 1, 10)
        time_list = time_list.tolist()

        fds_filename = '../../cgi-media/t_squared/fds%i.txt' % jobid
        surf_string = "&SURF ID='fire', RAMP_Q='tsquared', HRRPUA=%0.1f, COLOR='RED' /" % (np.max(hrr) / fds_fire_ramp_area)
        stats(fds_filename, surf_string + '\n')

        for n in time_list:
            fds_f_value = hrr[n] / np.max(hrr)
            ramp_text = "&RAMP ID='tsquared', T= %0.1f, F=%0.2f /" % (n, fds_f_value)
            outstring = ramp_text + '\n'
            stats(fds_filename, outstring)

        print "<a href='%s'>Download FDS ramp file</a><br/><br/>" % fds_filename
    except KeyError:
        pass

    # ============
    # = Plotting =
    # ============

    figure()

    plot(time, hrr, 'b-', lw=3)
    title_string = 't-squared fire growth ' + title_alpha
    title(title_string, fontsize=18)
    xlabel('Time (s)', fontsize=18)
    ylabel('Heat release rate (kW)', fontsize=18)
    grid(True)
    ax = gca()
    for xlabel_i in ax.get_xticklabels():
        xlabel_i.set_fontsize(14)
    for ylabel_i in ax.get_yticklabels():
        ylabel_i.set_fontsize(14)
    savestring = "../../cgi-media/t_squared/t_squared%i.png" % jobid
    savefig(savestring, dpi=80)

    print "<img src='%s'><br/>" % savestring

    # ============================
    # = Delete old results files =
    # ============================

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
        print """<script type="text/javascript">"""
        print "document.forms[0].%s.checked = true;" % (sel_alpha_value)
        print "document.forms[0].%s.checked = true;" % (sel_stopping_value)

        try:
            form["sel_save1_value"].value
            print "document.forms[0].sel_save1_value.checked = true;"
        except KeyError:
            pass

        try:
            form["sel_save2_value"].value
            print "document.forms[0].sel_save2_value.checked = true;"
        except KeyError:
            pass

        print "</script>"
        form_count += 1

def stats(path, string):
    # Write to stats text file
    filename = path
    f = open(filename, 'a')
    f.write(string)
    f.close()

def delete_old_files():
    ### Delete old plot files older than 1 hour ###
    path = '../../cgi-media/t_squared'
    now = time.time()
    for f in os.listdir(path):
        fullpath = path + "/" + f
        if ('t_squared' and '.png' in f) or ('case' and '.csv' in f) or ('fds' and '.txt' in f):
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
