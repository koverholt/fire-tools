#!/home/koverholt/anaconda/bin/python

# LICENSE
#
# Copyright (c) 2011 Kristopher Overholt
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
os.environ['HOME'] = '/home/koverholt/webapps/koverholt/cgi-media/cfast_online'

import numpy as np
from decimal import *
from math import sqrt
import cgi, sys, time, subprocess, shutil, zipfile

import matplotlib
matplotlib.use("Agg")
from pylab import *

import cgitb
cgitb.enable()

# Variables to script path and that gather form fields
SCRIPT_NAME = './index_cfast.cgi'
form = cgi.FieldStorage()

cfast_input_file = """VERSN,6,CFAST Online Simulation
!!
!!Scenario Configuration Keywords
!!
TIMES,%(sim_time)s,-50,10,10
EAMB,293.15,101300,0
TAMB,293.15,101300,0,50
CJET,WALLS
WIND,0,10,0.16
!!
!!Material Properties
!!
MATL,GYPSUM,0.16,900,790,0.016,0.9,Gypsum Board (5/8 in)
MATL,METHANE,0.07,1090,930,0.0127,0.04,Methane
!!
!!Compartment keywords
!!
COMPA,Compartment 1,%(room_length)s,%(room_width)s,%(room_height)s,0,0,0,GYPSUM,OFF,GYPSUM
!!
!!Vent keywords
!!
HVENT,1,2,1,%(door_width)s,%(door_height)s,0,1,0,0,1,1
!!
!!Fire keywords
!!
GLOBA,10,393.15
!!bunsen
FIRE,1,1.8,1.2,0,1,1,0,0,0,1,bunsen
CHEMI,1,4,0,0,0,0.33,5E+07,METHANE
TIME,%(time_ramp)s
HRR,%(hrr_ramp)s
SOOT,0,0,0,0,0,0,0,0,0,0,0
CO,0.001047221,0.001047221,0.001047221,0.001047221,0.001047221,0.001047221,0.001047221,0.001047221,0.001047221,0.001047221,0.001047221
TRACE,0,0,0,0,0,0,0,0,0,0,0
AREA,0.1,0.1,0.1,0.1,0.1,0.1,0.1,0.1,0.1,0.1,0.1
HEIGH,0,0,0,0,0,0,0,0,0,0,0
"""

# Writes out html page templates and form fields
def print_html_header():
    HTML_TEMPLATE_HEAD = """<!DOCTYPE html>
<!--[if lt IE 7 ]><html class="ie ie6" lang="en"> <![endif]-->
<!--[if IE 7 ]><html class="ie ie7" lang="en"> <![endif]-->
<!--[if IE 8 ]><html class="ie ie8" lang="en"> <![endif]-->
<!--[if (gte IE 9)|!(IE)]><!--><html lang="en"> <!--<![endif]-->
<head>

	<!-- Basic Page Needs
  ================================================== -->
	<meta charset="utf-8">
	<title>CFAST Online</title>
	<meta name="description" content="Fire modeling in your browser">
	<meta name="author" content="">
    <meta name="keywords" content="cfast, online, fire modeling, fire, modeling, zone model, zone, modeling, fpe, fire protection engineering, fire protection, hot gas layer, flashover, computer, fire effects, enclosure fire, fire dynamics, fire research">
	<!--[if lt IE 9]>
		<script src="http://html5shim.googlecode.com/svn/trunk/html5.js"></script>
	<![endif]-->

	<!-- Mobile Specific Metas
  ================================================== -->
	<meta name="viewport" content="width=device-width, initial-scale=1, maximum-scale=1">

	<!-- CSS
  ================================================== -->
	<link rel="stylesheet" href="stylesheets/base.css">
	<link rel="stylesheet" href="stylesheets/skeleton.css">
	<link rel="stylesheet" href="stylesheets/layout.css">

	<!-- Favicons
	================================================== -->
	<link rel="shortcut icon" href="images/favicon.ico">

    <style type="text/css">

    .tabContent
    {
    height: 240px
    }

    </style>

    <style type="text/css" media="screen">
    html, body {
        background-color: #FFFFFF;
    }

    </style>

    <script type="text/javascript">

      // this is a bit of a hack here
      // just list the tab content divs here
      var tabs = ["tab1","tab2","tab3","tab4","tab5"];

      function initTab( tab ){

        // first make sure all the tabs are hidden
        for(i=0; i < tabs.length; i++){
          var obj = document.getElementById(tabs[i]);
          obj.style.display = "none";
        }

        // show the first tab
        tab1.style.display = "block";

      }

      function showTab( tab ){

        // first make sure all the tabs are hidden
        for(i=0; i < tabs.length; i++){
          var obj = document.getElementById(tabs[i]);
          obj.style.display = "none";
        }

        // show the tab we're interested in
        var obj = document.getElementById(tab);
        obj.style.display = "block";

      }

    </script>

<script type="text/javascript">

  var _gaq = _gaq || [];
  _gaq.push(['_setAccount', 'UA-25487613-1']);
  _gaq.push(['_trackPageview']);

  (function() {
    var ga = document.createElement('script'); ga.type = 'text/javascript'; ga.async = true;
    ga.src = ('https:' == document.location.protocol ? 'https://ssl' : 'http://www') + '.google-analytics.com/ga.js';
    var s = document.getElementsByTagName('script')[0]; s.parentNode.insertBefore(ga, s);
  })();

</script>

    </head>
    <body onload="initTab()">

	<!-- Primary Page Layout
	================================================== -->

	<div class="container">
    <h4>Fire modeling in your browser</h4>
    <br/><br/>

    <!-- Standard <ul> with class of "tabs" -->
    <ul class="tabs">
      <!-- Give href an ID value of corresponding "tabs-content" <li>'s -->
      <li><a class="active" onclick="showTab('tab1')" href="#geom">Geometry</a></li>
      <li><a onclick="showTab('tab2')" href="#vent">Ventilation</a></li>
      <li><a onclick="showTab('tab3')" href="#desi">Fires</a></li>
      <li><a onclick="showTab('tab4')" href="#simu">Simulation parameters</a></li>
      <li><a onclick="showTab('tab5')" href="#abou">About</a></li>
    </ul>

    <!-- Standard <ul> with class of "tabs-content" -->
    <ul class="tabs-content">
      <!-- Give ID that matches HREF of above anchors -->
      <li class="active" id="geom"><h3>Geometry setup</h3></li>
      <li id="vent"><h3>Ventilation openings</h3></li>
      <li id="desi"><h3>Design fire</h3></li>
      <li id="simu"><h3>Simulation parameters</h3></li>
      <li id="abou"><h3>About</h3></li>
      </li>
    </ul>

    <!-- NOTE: jQuery that fires the change is in tabs.js -->

    <form action="%(SCRIPT_NAME)s" method="POST" enctype="multipart/form-data">"""
    print "Content-type: text/html\n"
    print HTML_TEMPLATE_HEAD % {'SCRIPT_NAME':SCRIPT_NAME}

def print_html_body():
    HTML_XDIM = """

      <div id="tab1" class="tabContent">

          <label for="regularInput">Room length (m)</label>
          <input type="text" name="txt_length_value" value="3.6" />

          <label for="regularInput">Room width (m)</label>
          <input type="text" name="txt_width_value" value="2.4" />

          <label for="regularInput">Room height (m)</label>
          <input type="text" name="txt_height_value" value="2.4" />

      </div>

      <div id="tab2" class="tabContent">

          <label for="regularInput">Door width (m)</label>
          <input type="text" name="txt_door_width_value" value="0.9" />

          <label for="regularInput">Door height (m)</label>
          <input type="text" name="txt_door_height_value" value="2.0" />

      </div>

      <div id="tab3" class="tabContent">

          <label for="selectList">Design fire type</label>
          <select name="lst_fire_value">
          <option value="1">Constant fire</option>
          <option value="2">Linearly growing</option>
          <option value="3">t-squared slow ramp</option>
          <option value="4">t-squared medium ramp</option>
          <option value="5">t-squared fast ramp</option>
          <option value="6">t-squared ultrafast ramp</option>
          </select>

          <label for="regularInput">Fire size (kW)</label>
          <input type="text" name="txt_q_value" value="400" />

      </div>

      <div id="tab4" class="tabContent">

          <label for="regularInput">Simulation time (s)</label>
          <input type="text" name="txt_time_value" value="600" />

          <label for="regularCheckbox">
            <input type="checkbox" name="chk_zip_value" value="1" />
            <span>Download CFAST output as ZIP archive</span>
          </label>

          <br/>

      </div>

      <div id="tab5" class="tabContent">

          CFAST Online was created to quickly and easily run zone model fire simulations in your browser, without installing any software. It can also be used to quickly generate case files, then download a ZIP archive of the results to your local computer.

          <br/><br/>

          Many of the CFAST input parameters that are not available in the web interface utilize the default values. For more detailed control over the simulation, select the "Download CFAST output" option from the Simulation Parameters tab to download the case to your local computer.

          <br/><br/>

          This website is a frontend for the <a href="http://www.nist.gov/el/fire_research/cfast.cfm">CFAST zone model</a> (version 6.2.0), which is maintained by the National Institute of Standards and Technology. The results and CFAST case files are for educational purposes only, and any output should be reviewed by a qualified person. The accuracy of the results is not guaranteed in any way.

       </div>

  <button type="submit">Run CFAST Online</button>
  <button type="reset">Reset inputs</button>
  </form>

  """

    print HTML_XDIM

def print_html_footer():
    HTML_TEMPLATE_FOOT = """<h5>CFAST Online is provided by <a href="http://www.koverholt.com">Kristopher Overholt</a>
    </h5><br/>

    <h6>Note: This site is not affiliated with NIST or <a href="http://www.nist.gov/el/fire_research/cfast.cfm">official CFAST development</a>.</h6>

    </div><!-- container -->

	<!-- JS
	================================================== -->
	<script src="//ajax.googleapis.com/ajax/libs/jquery/1.6.2/jquery.min.js"></script>
	<script src="javascripts/tabs.js"></script>

    </body>
    </html>"""
    print HTML_TEMPLATE_FOOT

# Checks the form field for empty submission, otherwise sends the query to the execute_search() fucntion
def check_user_inputs():
    """Check user form inputs and load into dict"""

    # Writes fields and values to lists for input looping
    inputs = {}

    input_fields = ('txt_time_value',
    'txt_length_value',
    'txt_width_value',
    'txt_height_value',
    'txt_q_value',
    'lst_fire_value',
    'chk_zip_value',
    'txt_door_width_value',
    'txt_door_height_value')

    # ========================
    # = Load user selections =
    # ========================
    for field in input_fields:
        try:
            inputs[field] = form[field].value
        except KeyError:
            if field == 'chk_zip_value':
                inputs['chk_zip_value'] = '0'
            else:
                print_html_footer()
                sys.exit()

    # Loops through input values to check for empty fields
    for field in input_fields:
        if inputs[field] == "":
            print """<h2><font color="red">""" + field + """ was not specified</font></h2><br/>"""
            fill_previous_values(inputs, input_fields)
            sys.exit()

    # Check to see if all inputs are valid numbers (by attempting to convert each one to a float)
    # If not, it will exit and fill the previous values
    try:
        for field in input_fields:
            float(inputs[field])
    except:
        print """<h2><font color="red">""" + field + """ is not a valid number</font></h2><br/>"""
        fill_previous_values(inputs, input_fields)
        sys.exit()

    # Convert all fields to floats
    for field in input_fields:
        inputs[field] = float(inputs[field])

    return inputs, input_fields

def cfast(sim_time, room_length, room_width, room_height, door_width, door_height, fire_type, fire_size, token1):

    # ========================
    # = Generate design fire =
    # ========================
    times = np.linspace(0, sim_time, 100)
    hrrs = np.zeros(len(times))

    if fire_type == 1:
        hrrs += fire_size
    elif fire_type == 2:
        hrrs += fire_size * (times / np.max(times))
    elif fire_type == 3:
        alpha = 0.00293 # kW/s2
        hrrs += alpha * times**2
        hrrs = hrrs.clip(0, fire_size)
    elif fire_type == 4:
        alpha = 0.01172 # kW/s2
        hrrs += alpha * times**2
        hrrs = hrrs.clip(0, fire_size)
    elif fire_type == 5:
        alpha = 0.0469 # kW/s2
        hrrs += alpha * times**2
        hrrs = hrrs.clip(0, fire_size)
    elif fire_type == 6:
        alpha = 0.1876 # kW/s2
        hrrs += alpha * times**2
        hrrs = hrrs.clip(0, fire_size)

    # Additional specifications
    specimen_length = 1
    specimen_width = 1
    HoC = 50000000 # Methane

    # Convert HRR from kW to W
    hrr_w = hrrs * 1000

    # Format arrays as comma separated lists for CFAST input file
    times_to_print = ','.join([str(i) for i in times])
    hrrs_to_print = ','.join([str(i) for i in hrr_w])

    # Insert values into CFAST input file
    outcase = cfast_input_file % {'sim_time': sim_time,
    'room_length': room_length,
    'room_width':room_width,
    'room_height':room_height,
    'door_width':door_width,
    'door_height':door_height,
    'time_ramp':times_to_print,
    'hrr_ramp':hrrs_to_print}

    # Create directory for case
    os.mkdir('../../cgi-media/cfast_online/' + str(token1))

    # Name and write CFAST input file
    filename = '../../cgi-media/cfast_online/' + str(token1) + '/case.in'
    f = open(filename, 'w')
    f.write(outcase)
    f.close()

def run_cfast(token1):
    """Run CFAST model on case"""
    cfast_job = subprocess.Popen(['./bin/cfast_intel', '../../cgi-media/cfast_online/' + str(token1) + '/case'])

    # Check to see if job lasts for longer than 10 seconds
    # If so, terminate it to avoid a spinning process

    jobcomplete = 0

    for i in range(10):
        time.sleep(1)
        if cfast_job.poll() == 0:
            jobcomplete = 1
            break

    if jobcomplete == 0:
        cfast_job.terminate()
        print '<h3><font color="red">Error: CFAST job ran too long; job terminated.</font></h3>'
        print '<br>'

def read_cfast_output(token1):
    """Reads in CFAST output files"""
    try:
        cfast_n = np.genfromtxt('../../cgi-media/cfast_online/' + str(token1) + '/case_n.csv', delimiter=',', skip_header=3)
    except (IOError, StopIteration):
        print '<h2><font color="red">CFAST error:</font></h2>'
        cfast_log = open('../../cgi-media/cfast_online/' + str(token1) + '/case.log', 'r')
        logtext = cfast_log.readlines()
        for line in logtext:
            print line + '<br/>'
        fill_previous_values(inputs, input_fields)
        sys.exit()

    return cfast_n

def save_figures(cfast_n, token1, fire_type, fire_size):
    """Plot figures with matplotlib and save plots to working CFAST dir"""

    # Create directory for case
    os.mkdir('../../cgi-media/cfast_online/' + str(token1) + '/Figures')

    # ==================
    # = Generate plots =
    # ==================
    plot_cfast(cfast_n, 1, 'Hot gas layer temperature vs. time',
    'Time (s)', u'Temperature ($^\circ$C)', 'hgl_temps', token1, fire_type, fire_size)

    plot_cfast(cfast_n, 3, 'Layer height vs. time',
    'Time (s)', u'Height (m)', 'layer_height', token1, fire_type, fire_size)

    plot_cfast(cfast_n, 7, 'Floor heat flux vs. time',
    'Time (s)', u'Heat flux (kW/m$^2$)', 'heat_flux', token1, fire_type, fire_size)

    plot_cfast(cfast_n, 12, 'Heat release rate vs. time',
    'Time (s)', u'HRR (kW)', 'heat_release_rate', token1, fire_type, fire_size)

    # plot_cfast(cfast_n, 11, 'Flame height vs. time',
    # 'Time (s)', u'Height (m)', 'flame_height', token1)

def plot_cfast(data, column, plot_title, xlab, ylab, filename, token1, fire_type, fire_size):
    """Plot figures with matplotlib and save plots to working CFAST dir"""
    figure()

    # Adjust heat flux from W to kW
    if column == 7:
        data[:,7] = data[:,7] / 1000

    # Adjust HRR from W to kW
    elif column == 12:
        data[:,12] = data[:,12] / 1000

    plot(data[:,0], data[:,column], lw=3)
    title(plot_title, fontsize=20)
    # axvline(L, ls='--', color='black')
    xlabel(xlab, fontsize=20)
    ylabel(ylab, fontsize=20)
    ylim(ymin=0)
    # Scale ymax to 20% of fire size
    if column == 10:
        ylim([0, fire_size + fire_size * 0.2])
    grid(True)
    ax = gca()
    for xlabel_i in ax.get_xticklabels():
        xlabel_i.set_fontsize(16)
    for ylabel_i in ax.get_yticklabels():
        ylabel_i.set_fontsize(16)
    savestring = '../../cgi-media/cfast_online/' + str(token1) + '/Figures/' + filename + '.png'
    savefig(savestring, dpi=80)

    # Show plots in page
    print '<center>'
    print '<img src="../../cgi-media/cfast_online/' + str(token1) + '/Figures/' + filename + '.png">'
    print '</center>'

def zip_files(token1):
    """create archive of all case files"""
    zip_path = '../../cgi-media/cfast_online/' + str(token1) + '/'
    os.chdir(zip_path)

    archive_list = os.listdir('./')
    for figs in os.listdir('./Figures'):
        archive_list += ['./Figures/' + figs]

    # save the files in the archive_list into a PKZIP format .zip file
    zip_name = 'case_files.zip'
    zout = zipfile.ZipFile(zip_name, 'w')
    for fname in archive_list:
        zout.write(fname)
    zout.close()

    os.chdir('../../../cgi-bin/cfast_online/')

def fill_previous_values(inputs, input_fields):
    """Fill in user-specified values"""
    js_form_fill = """<script type="text/javascript">
          document.forms[0].%(FORM_ELEMENT_NAME)s.value = '%(FORM_VALUE)s';
          </script>"""
    js_checkbox_fill = """<script type="text/javascript">
          document.forms[0].%(FORM_ELEMENT_NAME)s.checked = %(FORM_VALUE)s;
          </script>"""
    js_list_fill = """<script type="text/javascript">
          document.forms[0].%(FORM_ELEMENT_NAME)s.selectedIndex = %(FORM_VALUE)s;
          </script>"""

    # Loops through form fields and writes out a custom javascript line for each element
    # to keep the previously typed number in the form
    for field in input_fields:
        if 'chk' in field:
            if inputs[field] == 1:
                checked = 'true'
            else:
                checked = 'false'
            print js_checkbox_fill % {'FORM_ELEMENT_NAME':field, 'FORM_VALUE':checked}
        elif 'lst' in field:
            print js_list_fill % {'FORM_ELEMENT_NAME':field, 'FORM_VALUE':int(inputs[field]) - 1}
        else:
            print js_form_fill % {'FORM_ELEMENT_NAME':field, 'FORM_VALUE':inputs[field]}

def delete_old_files():
    ### Delete old case folders older than 1 hour ###
    path = '../../cgi-media/cfast_online'
    now = time.time()
    for f in os.listdir(path):
        fullpath = path + "/" + f
        if os.stat(fullpath).st_mtime < now - 3600:
            shutil.rmtree(fullpath)

# =============================================================
# = Actual start of execution of script using above functions =
# =============================================================

print_html_header()

print_html_body()

inputs, input_fields = check_user_inputs()

# Generate ID number for case
token1 = np.random.randint(10000000)

# ===================================
# = Execute primary CFAST functions =
# ===================================

# Generate CFAST input file
cfast(inputs['txt_time_value'],
      inputs['txt_length_value'],
      inputs['txt_width_value'],
      inputs['txt_height_value'],
      inputs['txt_door_width_value'],
      inputs['txt_door_height_value'],
      inputs['lst_fire_value'],
      inputs['txt_q_value'],
      token1)

# Run CFAST model
run_cfast(token1)

# Read in CFAST output files
cfast_n = read_cfast_output(token1)

print '<h3>Results</h3>'

# Print download links
if inputs['chk_zip_value'] == 1:
    print '<h4>'
    print '<a href="http://www.koverholt.com/cgi-media/cfast_online/' + str(token1) + '/case_files.zip' + '">Download CFAST files</a>'
    print '</h4>'

# Plot and save figures in case folder
save_figures(cfast_n, token1,
             inputs['lst_fire_value'],
             inputs['txt_q_value'])

# Zip files for download (if selected)
if inputs['chk_zip_value'] == 1:
    zip_files(token1)

# Remove old CFAST files
delete_old_files()

# ===============================
# = End primary CFAST functions =
# ===============================

fill_previous_values(inputs, input_fields)

js_form_textbox_red = """<script type="text/javascript">
document.getElementById("x0_dim").style.color="red";
</script>"""

js_form_textbox_red_2 = """<script type="text/javascript">
x0_dim.style.backgroundColor = "#FF0000";
</script>"""

print js_form_textbox_red_2
# print_output_results()

print_html_footer()
