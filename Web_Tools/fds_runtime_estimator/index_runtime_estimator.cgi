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
os.environ['HOME'] = '/home/koverholt/webapps/koverholt/cgi-media/fds_runtime_estimator'

import re, cgi, time
import numpy as np

import matplotlib
matplotlib.use("Agg")
from pylab import *

import cgitb
cgitb.enable()

# Variables to script path and that gather form fields
SCRIPT_NAME = '/cgi-bin/fds_runtime_estimator/index_runtime_estimator.cgi'
form = cgi.FieldStorage()

# Writes out html page templates and form fields
def print_html_header():
    HTML_TEMPLATE_HEAD = """<!DOCTYPE html>
    <html><head><title>FDS Runtime Estimator</title>
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

    <div class="container">

    <form enctype="multipart/form-data" class="well" action="%(SCRIPT_NAME)s" method="POST" enctype="multipart/form-data">"""
    print "Content-type: text/html\n"
    print HTML_TEMPLATE_HEAD % {'SCRIPT_NAME':SCRIPT_NAME}


def print_html_body():

    # Windows option for file upload
    try: # Windows needs stdio set for binary mode.
        import msvcrt
        msvcrt.setmode (0, os.O_BINARY) # stdin  = 0
        msvcrt.setmode (1, os.O_BINARY) # stdout = 1
    except ImportError:
        pass

    OUT_FILE_INPUT = """

    <h3><FONT FACE="Arial, Helvetica, Geneva"><font color="darkred">Paste the contents of your FDS &lt;case&gt;.out file</font></h3><br/>
    <textarea class="input-xxlarge" id="outfile" name="outfile" rows="20"></textarea>
    <br/>

    <h5>(Optional) To demo this tool, <a href='#' onclick="loadSample(); return false;">load a sample .out file</a>.</h5><br/>

    <h3><FONT FACE="Arial, Helvetica, Geneva"><font color="darkred">Or, upload your FDS &lt;case&gt;.out file:</font></h3><br/>
    <input type="file" name="file"><br/><br/><br/>

    <input class="btn btn-large btn-primary" name="submit" type="submit" value="Calculate estimated FDS run time &raquo;"><br/><br/>
    """

    print OUT_FILE_INPUT

def print_html_footer():
    # Load sample .out file into textarea (on user request)
    sample_file_string = './sample.out'
    sample_raw = open(sample_file_string)
    sample_text = sample_raw.readlines(999999999)
    sample_fill = ''.join(sample_text).replace("\n", "\\r\\n")

    HTML_TEMPLATE_FOOT = """</font>
    </form>

    <script type="text/javascript">
    function loadSample()
    {
        document.forms[0].outfile.value = "%(sample)s";
    }
    </script>

    </div>
    </body>
    </html>"""

    print HTML_TEMPLATE_FOOT % {"sample":sample_fill}

def check_input_fields(outfile=""):

    random_num = np.random.randint(10000000)

    # Initialization
    all_fds_times = np.array([])
    all_predicted_times = np.array([])
    all_predicted_times_backup = np.array([])
    all_time_steps = np.array([])
    all_cpu_steps = np.array([])
    remaining_times = np.array([])
    mesh_time_sums = np.array([])
    mesh_count = 0
    calc_time = 0
    check_1 = 0
    check_2 = 0

    # Writes fields and values to lists for input looping
    global input_fields, input_values, textarea_print, textarea_option
    input_fields = ["outfile"]
    input_values = [outfile]

    # Check if the file was uploaded
    if fileitem.filename:
        file_string = '../../cgi-media/fds_runtime_estimator/outfile' + str(random_num) + '.txt'
        open(file_string, 'wb').write(fileitem.file.read())
        outfile_raw = open(file_string)
        outfile = outfile_raw.readlines(999999999)
        textarea_print = outfile
        textarea_option = 2
    # Otherwise, use the information from the textarea
    else:
        outfile_raw = outfile
        outfile = outfile.splitlines()
        textarea_print = outfile_raw
        textarea_option = 1

    # Check to see if any input was provided
    if outfile == []:
        print '<font color="red">Error: No file provided.<br/><br/>Please paste the contents (or upload) of your FDS &lt;case&gt;.out file</font>'
        sys.exit()

    # Check to see if the file is a valid FDS .out file
    for line in outfile:
        if 'Fire Dynamics Simulator' in line:
            check_1 = 1
        if 'Run Time Diagnostics' in line:
            check_2 = 1
    if (check_1 == 0) and (check_2 == 0):
        print '<font color="red">Error: This does not appear to be a valid FDS .out file. Please resubmit.</font>'
        sys.exit()

    # Check to see if the case contains multiple meshes
    for line in outfile:
        if 'Grid Dimensions, Mesh' in line:
            mesh_count += 1

    # Search for appropriate times in .out file
    for line in outfile:
        if 'Simulation End Time' in line:
            t_end_line = re.findall('\d+.\d+', line)
            t_end = float(t_end_line[0]) / 3600

        if 'Total CPU' in line:
            cpu_line = re.findall('\d+.\d+', line)
            current_cpu_step = float(cpu_line[0])
            if 'hr' in line:
                cpu_time = float(cpu_line[1])
            elif 'min' in line:
                cpu_time = float(cpu_line[1]) / 60
            else:
                cpu_time = float(cpu_line[1]) / 3600

        if 'Total time' in line:
            wall_clock_line = re.findall('\d+.\d+', line)
            current_time_step = float(wall_clock_line[0])
            if 'hr' in line:
                fds_time = float(wall_clock_line[1])
            elif 'min' in line:
                fds_time = float(wall_clock_line[1]) / 60
            else:
                fds_time = float(wall_clock_line[1]) / 3600

            # If FDS time is zero, skip this line in the .out file
            if fds_time == 0:
                continue

            calc_time = 1

        if calc_time == 1:
            # The predicted end time calculation routine
            predicted_end_time = cpu_time / (fds_time) * (t_end)
            remaining_time = predicted_end_time - cpu_time
            if remaining_time <= 0:
                remaining_time = 0

            all_fds_times = np.append(all_fds_times, fds_time)
            remaining_times = np.append(remaining_times, remaining_time)
            all_predicted_times = np.append(all_predicted_times, predicted_end_time)
            all_time_steps = np.append(all_time_steps, current_time_step)
            all_cpu_steps = np.append(all_cpu_steps, current_cpu_step)

            calc_time = 0

    #  =================
    #  = Print results =
    #  =================

    print '<br/><h2>When will your FDS simulation complete?</h2><br/>'

    # Determine the mesh that is taking the most CPU
    if mesh_count > 1:
        for i in range(mesh_count):
            mesh_time_sums = np.append(mesh_time_sums, np.sum(all_predicted_times[0+i::mesh_count]))
        slowest_mesh = np.argmax(mesh_time_sums)

        all_predicted_times_backup = all_predicted_times
        all_predicted_times = all_predicted_times[0+slowest_mesh::mesh_count]

        all_time_steps_backup = all_time_steps
        all_time_steps = all_time_steps[0+slowest_mesh::mesh_count]

        all_cpu_steps_backup = all_cpu_steps
        all_cpu_steps = all_cpu_steps[0+slowest_mesh::mesh_count]

        remaining_times_backup = remaining_times
        remaining_times = remaining_times[0+slowest_mesh::mesh_count]

        print '<font color="blue"><b>Note: Multiple meshes detected.</b><br/>'
        print 'The most computationally expensive mesh is MESH #%s.<br/>' % (str(slowest_mesh + 1))
        print 'The following calculations are based on this mesh.</font><br/><br/>'

    # Print general timing results
    print 'Based on the provided data, the estimated total runtime for your FDS simulation is <b>%0.1f hours (%0.0f minutes).</b><br/><br/>' % (all_predicted_times[-1], all_predicted_times[-1] * 60)

    if remaining_times[-1] == 0:
        print 'Your simulation is complete.<br/><br/>'
    else:
        print 'Your simulation has about <b>%0.1f hours (%0.0f minutes) of runtime remaining.</b><br/><br/>' % (remaining_times[-1], remaining_times[-1] * 60)

    #  ==============================================================
    #  = Plot estimated FDS runtime vs. elapsed FDS simulation time =
    #  ==============================================================

    figure()
    if mesh_count > 1:
        multi_label = 'Mesh #%s' % (str(slowest_mesh + 1))
        plot(all_fds_times * 3600, all_predicted_times_backup, color='0.80', label='All other meshes')
        plot(all_fds_times[::mesh_count] * 3600, all_predicted_times, lw=3, label=multi_label, color='b')
        legend(loc=0)
    else:
        plot(all_fds_times * 3600, all_predicted_times, lw=3)
    title('Estimated FDS runtime vs. elapsed FDS simulation time', fontsize=14)
    xlabel('Elapsed FDS simulation time (seconds)', fontsize=16)
    ylabel('Estimated total FDS runtime (hours)', fontsize=16)
    ax = gca()
    for xlabel_i in ax.get_xticklabels():
        xlabel_i.set_fontsize(14)
    for ylabel_i in ax.get_yticklabels():
        ylabel_i.set_fontsize(14)
    grid(True)
    savestring = "../../cgi-media/fds_runtime_estimator/fds_runtime%i.png" % random_num
    savefig(savestring, dpi=80)

    print "<img src='%s'><br/><br/>" % savestring

    #  ==================================================
    #  = Plot time step vs. elapsed FDS simulation time =
    #  ==================================================

    figure(figsize=(9,6))
    if mesh_count > 1:
        multi_label = 'Mesh #%s' % (str(slowest_mesh + 1))
        plot(all_fds_times * 3600, all_time_steps_backup, color='0.80', label='All other meshes')
        plot(all_fds_times[::mesh_count] * 3600, all_time_steps, lw=3, label=multi_label, color='b')
        legend(loc=0)
    else:
        plot(all_fds_times * 3600, all_time_steps, lw=3)
    title('FDS time step vs. elapsed FDS simulation time', fontsize=14)
    xlabel('Elapsed FDS simulation time (seconds)', fontsize=16)
    ylabel('FDS time step (seconds)', fontsize=16)
    ax = gca()
    for xlabel_i in ax.get_xticklabels():
        xlabel_i.set_fontsize(14)
    for ylabel_i in ax.get_yticklabels():
        ylabel_i.set_fontsize(14)
    grid(True)
    savestring = "../../cgi-media/fds_runtime_estimator/fds_timestep%i.png" % random_num
    savefig(savestring, dpi=71)

    print "<img src='%s'><br/><br/>" % savestring

    #  ==================================================
    #  = Plot CPU/step vs. elapsed FDS simulation time =
    #  ==================================================

    figure()
    if mesh_count > 1:
        multi_label = 'Mesh #%s' % (str(slowest_mesh + 1))
        plot(all_fds_times * 3600, all_cpu_steps_backup, color='0.80', label='All other meshes')
        plot(all_fds_times[::mesh_count] * 3600, all_cpu_steps, lw=3, label=multi_label, color='b')
        legend(loc=0)
    else:
        plot(all_fds_times * 3600, all_cpu_steps, lw=3)
    title('FDS CPU/step vs. elapsed FDS simulation time', fontsize=14)
    xlabel('Elapsed FDS simulation time (seconds)', fontsize=16)
    ylabel('FDS CPU/step (seconds)', fontsize=16)
    ax = gca()
    for xlabel_i in ax.get_xticklabels():
        xlabel_i.set_fontsize(14)
    for ylabel_i in ax.get_yticklabels():
        ylabel_i.set_fontsize(14)
    grid(True)
    savestring = "../../cgi-media/fds_runtime_estimator/fds_cpustep%i.png" % random_num
    savefig(savestring, dpi=80)

    print "<img src='%s'><br/><br/>" % savestring

    # Delete older files from previous runs
    delete_old_files()

def fill_previous_values():
    js_form_fill = """<script type="text/javascript">
          document.forms[0].%(FORM_ELEMENT_NAME)s.value = "%(FORM_VALUE)s";
          </script>"""
    form_field_names = ["outfile"]
    # Loops through form fields and writes out a custom javascript line for each element
    # to keep the previously typed number in the form
    form_count = 0

    # Replace newlines in .out file with appropriate newlines for javascript
    if textarea_option == 1:
        refill = textarea_print.replace("\r\n", "\\r\\n")
    if textarea_option == 2:
        refill = ''.join(textarea_print).replace("\n", "\\r\\n")

    # Refill textarea content
    print js_form_fill % {'FORM_ELEMENT_NAME':form_field_names[form_count], 'FORM_VALUE':refill}

def delete_old_files():
    ### Delete old plot files older than 1 hour ###
    path = '../../cgi-media/fds_runtime_estimator'
    now = time.time()
    for f in os.listdir(path):
        fullpath = path + "/" + f
        if ('fds_runtime' and '.png' in f) or ('outfile' and '.txt' in f):
            if os.stat(fullpath).st_mtime < now - 3600:
                if os.path.isfile(fullpath):
                    os.remove(fullpath)

###############################################################
#  Actual start of execution of script using above functions  #
###############################################################

print_html_header()

print_html_body()

try:
    outfile = form["outfile"].value
    fileitem = form['file']
except:
    print_html_footer()
    sys.exit()

check_input_fields(outfile)

fill_previous_values()

js_form_textbox_red = """<script type="text/javascript">
document.getElementById("x0_dim").style.color="red";
</script>"""

js_form_textbox_red_2 = """<script type="text/javascript">
x0_dim.style.backgroundColor = "#FF0000";
</script>"""

print js_form_textbox_red_2

print_html_footer()
