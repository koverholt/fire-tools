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

from decimal import *
from math import sqrt
import cgi, sys

import cgitb
cgitb.enable()

# Variables to script path and that gather form fields
SCRIPT_NAME = '/cgi-bin/fds_mesh/index_mesh.cgi'
form = cgi.FieldStorage()

global resolution
resolution = ''

# Groups integers into comma separated thousands
def group(number):
    s = '%d' % number
    groups = []
    while s and s[-1].isdigit():
        groups.append(s[-3:])
        s = s[:-3]
    return s + ','.join(reversed(groups))

# Writes out html page templates and form fields
def print_html_header():
    HTML_TEMPLATE_HEAD = """<!DOCTYPE html>
    <html><head><title>FDS v5 Mesh Size Calculator</title>
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

    <font color="red"><b>NOTE: You should always perform a grid sensitivity analysis and verify the grid resolution yourself. This calculator should only be used as a guide / rule of thumb!</b></font><br/><br/>
    <h3><FONT FACE="Arial, Helvetica, Geneva"><font color="darkred">Enter the x, y, z dimensions (meters) and
    your expected HRR</font></h3>
    <form class="well" action="%(SCRIPT_NAME)s" method="POST" enctype="multipart/form-data">"""
    print "Content-type: text/html\n"
    print HTML_TEMPLATE_HEAD % {'SCRIPT_NAME':SCRIPT_NAME}


def print_html_body():
    HTML_XDIM = """X<sub>min</sub> <input class="input-mini" name="x0_dim" type="text" size="4"> &nbsp;&nbsp;X<sub>max</sub> <input class="input-mini" name="x1_dim" type="text" size="4"><br/>"""
    HTML_YDIM = """Y<sub>min</sub> <input class="input-mini" name="y0_dim" type="text" size="4"> &nbsp;&nbsp;Y<sub>max</sub> <input class="input-mini" name="y1_dim" type="text" size="4"><br/>"""
    HTML_ZDIM = """Z<sub>min</sub> <input class="input-mini" name="z0_dim" type="text" size="4"> &nbsp;&nbsp;Z<sub>max</sub> <input class="input-mini" name="z1_dim" type="text" size="4"><br/><br/>"""
    HTML_DX = """Requested cell size (dx, dy, dz): <input name="dx" type="text" size="4"><br/><br/>"""
    HTML_SUBMIT = """<input name="submit" type="submit" value="Calculate MESH Line"><br/><br/>"""

    DSTAR_INPUT = """

    <label>Heat Release Rate (Q) </label>
    <input class="input-mini" name="hrr" type="text" size="5"> kW
    <br/><br/>
    <label>Density (p<sub>&#8734;</sub>) </label>
    <input class="input-mini" name="p_inf" type="text" size="5" value="1.204"> kg / m<sup>3</sup>
    <br/><br/>
    <label>Specific Heat (c<sub>p</sub>) </label>
    <input class="input-mini" name="cp" type="text" size="5" value="1.005"> kJ / kg-K
    <br/><br/>
    <label>Ambient Temperature (T<sub>&#8734;</sub>) </label>
    <input class="input-mini" name="t_inf" type="text" size="5" value="293"> K
    <br/><br/>
    <label>Gravity (g) </label>
    <input class="input-mini" name="grav" type="text" size="5" value="9.81"> m / s<sup>2</sup>


    <br/><br/>

    <input class="btn btn-large btn-primary" name="submit" type="submit" value="Calculate suggested cell sizes &raquo;"><br/><br/>
    """

    USE_OLD_CALC = """To use the old MESH Size Calculator, <a
href="/cgi-bin/fds_mesh/mesh.cgi">click here</a>"""

    print HTML_XDIM
    print HTML_YDIM
    print HTML_ZDIM
    print DSTAR_INPUT
    print USE_OLD_CALC

def print_html_footer():
    HTML_TEMPLATE_FOOT = """</font>
    </form>

    <!-- Le javascript
    ================================================== -->
    <!-- Placed at the end of the document so the pages load faster -->
    <script src="../assets/js/jquery.js"></script>
    <script src="../assets/js/bootstrap-transition.js"></script>
    <script src="../assets/js/bootstrap-alert.js"></script>
    <script src="../assets/js/bootstrap-modal.js"></script>
    <script src="../assets/js/bootstrap-dropdown.js"></script>
    <script src="../assets/js/bootstrap-scrollspy.js"></script>
    <script src="../assets/js/bootstrap-tab.js"></script>
    <script src="../assets/js/bootstrap-tooltip.js"></script>
    <script src="../assets/js/bootstrap-popover.js"></script>
    <script src="../assets/js/bootstrap-button.js"></script>
    <script src="../assets/js/bootstrap-collapse.js"></script>
    <script src="../assets/js/bootstrap-carousel.js"></script>
    <script src="../assets/js/bootstrap-typeahead.js"></script>

    </div>
    </body>
    </html>"""
    print HTML_TEMPLATE_FOOT

# Checks the form field for empty submission, otherwise sends the query to the execute_search() fucntion
def check_input_fields(x0_dim="", x1_dim="", y0_dim="", y1_dim="", z0_dim="", z1_dim="", hrr="", p_inf="", cp="", t_inf="", grav=""):
    # Writes fields and values to lists for input looping
    global input_fields
    global input_values
    input_fields = ("X0", "X1", "Y0", "Y1", "Z0", "Z1", "hrr", "p_inf", "cp", "t_inf", "grav")
    input_values = (x0_dim, x1_dim, y0_dim, y1_dim, z0_dim, z1_dim, hrr, p_inf, cp, t_inf, grav)

    # Loops through input values to check for empty fields and returns an error if so
    count = 0
    for field in input_values:
        if field == "":
            print """<h2><font color="red">""" + input_fields[count] + """ was not specified</font></h2><br/>"""
            fill_previous_values()
            print_html_footer()
            sys.exit()
        count += 1

    # Check to see if all inputs are valid numbers (by attempting to convert each one to a float)
    # If not, it will exit and fill the previous values
    count = 0
    for field in input_values:
        try:
            float(field)
        except:
            print """<h2><font color="red">""" + input_fields[count] + """ is not a valid number</font></h2><br/>"""
            fill_previous_values()
            print_html_footer()
            sys.exit()
        count += 1

    check_x0 = float(x0_dim)
    check_x1 = float(x1_dim)
    check_y0 = float(y0_dim)
    check_y1 = float(y1_dim)
    check_z0 = float(z0_dim)
    check_z1 = float(z1_dim)

    #### Add error checking for non-numbers

    if check_x1 < check_x0:
        print """<h2><font color="red">X1 should be greater than X0</font></b>"""
        fill_previous_values()
        print_html_footer()
        sys.exit()
    if check_y1 < check_y0:
        print """<h2><font color="red">Y1 should be greater than Y0</font></b>"""
        fill_previous_values()
        print_html_footer()
        sys.exit()
    if check_z1 < check_z0:
        print """<h2><font color="red">Z1 should be greater than Z0</font></b>"""
        fill_previous_values()
        print_html_footer()
        sys.exit()

    dstar_compute(hrr, p_inf, cp, t_inf, grav)

# Calculates the desired I,J,K values and sends them to the Poisson optimizer for checking/calculation
def dstar_compute(hrr, p_inf, cp, t_inf, grav):
    hrr = float(hrr)
    p_inf = float(p_inf)
    cp = float(cp)
    t_inf = float(t_inf)
    grav = sqrt(float(grav))

    dstar_power = float("0.4")

    d_star = pow((hrr / (p_inf * cp * t_inf * grav) ), dstar_power)
    print "<br/><br/><h2>"
    print '<hr>'
    print "The characteristic fire diameter D<sup>*</sup> is ", round(d_star, 3)
    print "</h2>"

    uguide_min_suggested_dx = d_star / 16
    uguide_mod_suggested_dx = d_star / 10
    uguide_max_suggested_dx = d_star / 4

    coarse = "<img src='../../cgi-media/fds_mesh/coarse.png'><br/>" + "When D<sup>*</sup>/dx = 4: " + "the suggested coarse cell size is " + str(round(float(uguide_max_suggested_dx * 100), 2)) + " cm <br/><br/>"
    moderate = "<img src='../../cgi-media/fds_mesh/moderate.png'><br/>" + "When D<sup>*</sup>/dx = 10: " + "the suggested moderate cell size is " + str(round(float(uguide_mod_suggested_dx * 100), 2)) + " cm <br/><br/>"
    fine = "<img src='../..//cgi-media/fds_mesh/fine.png'><br/>" + "When D<sup>*</sup>/dx = 16, " + "the suggested fine cell size is " + str(round(float(uguide_min_suggested_dx * 100), 2)) + " cm <br/><br/>"

    uguide_min_suggested_dx = str(uguide_min_suggested_dx)
    uguide_mod_suggested_dx = str(uguide_mod_suggested_dx)
    uguide_max_suggested_dx = str(uguide_max_suggested_dx)

    mesh_compute(x0_dim, x1_dim, y0_dim, y1_dim, z0_dim, z1_dim, uguide_max_suggested_dx, coarse)
    mesh_compute(x0_dim, x1_dim, y0_dim, y1_dim, z0_dim, z1_dim, uguide_mod_suggested_dx, moderate)
    mesh_compute(x0_dim, x1_dim, y0_dim, y1_dim, z0_dim, z1_dim, uguide_min_suggested_dx, fine)

# Calculates the desired I,J,K values and sends them to the Poisson optimizer for checking/calculation
def mesh_compute(x0_dim, x1_dim, y0_dim, y1_dim, z0_dim, z1_dim, dx, resolution):
    global ijk_bars
    ijk_bars = []
    print '<hr>'
    print resolution
    global x_dim, y_dim, z_dim, current_dx

    current_dx = dx

    x0_dim = Decimal(x0_dim)
    x1_dim = Decimal(x1_dim)
    y0_dim = Decimal(y0_dim)
    y1_dim = Decimal(y1_dim)
    z0_dim = Decimal(z0_dim)
    z1_dim = Decimal(z1_dim)
    dx = Decimal(dx)

    x_dim = x1_dim - x0_dim
    y_dim = y1_dim - y0_dim
    z_dim = z1_dim - z0_dim

    if x_dim == 0:
        print """<h2><font color="red">X dimension cannot be zero</font></h2>"""
        fill_previous_values()
        print_html_footer()
        sys.exit()
    if y_dim == 0:
        print """<h2><font color="red">Y dimension cannot be zero</font></h2>"""
        fill_previous_values()
        print_html_footer()
        sys.exit()
    if z_dim == 0:
        print """<h2><font color="red">Z dimension cannot be zero</font></h2>"""
        fill_previous_values()
        print_html_footer()
        sys.exit()

    # Checks to see if dx is bigger than any single dimension
    if (dx > x_dim) | (dx > y_dim) | (dx > z_dim):
        print """<h2><font color="red">dx cannot be greater than any x, y, or z dimension</font></h2><br/>"""
        fill_previous_values()
        print_html_footer()
        sys.exit()

    desired_i = x_dim / dx
    desired_j = y_dim / dx
    desired_k = z_dim / dx

    Poisson(int(desired_i))
    Poisson(int(desired_j))
    Poisson(int(desired_k))

def Poisson(desired_num):
    """Uses mod 2, 3, 5 to see if numbers are Poisson optimized.
    If they are not, it goes from x to x*1.4 in increments of 1 and rechecks until factorable
    Then it returns the factorable and Poisson-friendly I,J,K values"""
    for i in range(desired_num*Decimal("1.4")):
        global ijk_bars
        check_digit = desired_num
        while check_digit % 2 == 0:
            check_digit = check_digit / 2
        while check_digit % 3 == 0:
            check_digit = check_digit / 3
        while check_digit % 5 == 0:
            check_digit = check_digit / 5

        if check_digit in (1, 2, 3, 5):
            ijk_bars.append(int(desired_num))
            break
        else:
            desired_num = desired_num + 1
            continue

    if len(ijk_bars) == 3:
        print_output_results()
        resolution = ''

def fill_previous_values():
    js_form_fill = """<script type="text/javascript">
          document.forms[0].%(FORM_ELEMENT_NAME)s.value = '%(FORM_VALUE)s';
          </script>"""
    form_field_names = ("x0_dim", "x1_dim", "y0_dim", "y1_dim", "z0_dim", "z1_dim", "hrr", "p_inf", "cp", "t_inf", "grav")
    # Loops through form fields and writes out a custom javascript line for each element
    # to keep the previously typed number in the form
    form_count = 0
    for field in input_values:
        print js_form_fill % {'FORM_ELEMENT_NAME':form_field_names[form_count], 'FORM_VALUE':field}
        form_count += 1

def print_output_results():

    print "Your MESH line for FDS is:<br/><h2>&MESH IJK=" + str(ijk_bars[0]) + "," + str(ijk_bars[1]) + "," + str(ijk_bars[2]) + ", XB=" + str(x0_dim) + "," + str(x1_dim) + "," + str(y0_dim) + "," + str(y1_dim) + "," + str(z0_dim) + "," + str(z1_dim) + " /</h2>"

    print "You entered: " , "<br/>X<sub>min</sub>: ",x0_dim, "X<sub>max</sub>: ",x1_dim, "<br/>Y<sub>min</sub>: ",y0_dim, "Y<sub>max</sub>: ",y1_dim, "<br/>Z<sub>min</sub>: ",z0_dim, "Z<sub>max</sub>: ",z1_dim, "<br/>dx: ",round(float(current_dx),3)

    print "<br/><br/>"

    print "Your actual dx(es) are ", round(x_dim/ijk_bars[0],3), round(y_dim/ijk_bars[1],3), round(z_dim/ijk_bars[2],3), " (meters)"
    print "<br/>"

    print "Your distances are", x_dim, y_dim, z_dim, " (meters)"
    print "<br/>"

    totnumcells = ijk_bars[0] * ijk_bars[1] * ijk_bars[2]
    print "Your total number of cells is ", str(group(int(totnumcells)))
    print "<br/><br/>"


###############################################################
#  Actual start of execution of script using above functions  #
###############################################################

print_html_header()

print_html_body()

try:
    x0_dim = form["x0_dim"].value
    x1_dim = form["x1_dim"].value
    y0_dim = form["y0_dim"].value
    y1_dim = form["y1_dim"].value
    z0_dim = form["z0_dim"].value
    z1_dim = form["z1_dim"].value
    hrr = form["hrr"].value
    p_inf = form["p_inf"].value
    cp = form["cp"].value
    t_inf = form["t_inf"].value
    grav = form["grav"].value
except:
    print_html_footer()
    sys.exit()

check_input_fields(x0_dim, x1_dim, y0_dim, y1_dim, z0_dim, z1_dim, hrr, p_inf, cp, t_inf, grav)

fill_previous_values()

js_form_textbox_red = """<script type="text/javascript">
document.getElementById("x0_dim").style.color="red";
</script>"""

js_form_textbox_red_2 = """<script type="text/javascript">
x0_dim.style.backgroundColor = "#FF0000";
</script>"""

print js_form_textbox_red_2

print_html_footer()
