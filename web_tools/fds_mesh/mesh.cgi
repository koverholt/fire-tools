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

from decimal import *
import cgi, sys

import cgitb
cgitb.enable()

# Variables to script path and that gather form fields
SCRIPT_NAME = '/cgi-bin/fds_mesh/mesh.cgi'
form = cgi.FieldStorage()

ijk_bars = []

# Writes out html page templates and form fields
def print_html_header():
    HTML_TEMPLATE_HEAD = """<!DOCTYPE HTML PUBLIC "-//W3C//DTD HTML 4.01 Transitional//EN">
    <html><head><title>FDS v5 Mesh Size Calculator</title>
    <meta http-equiv="Content-Type" content="text/html; charset=iso-8859-1">
    </head><body>
    <h3><FONT FACE="Arial, Helvetica, Geneva"><font color="darkred">Enter x, y, z offsets and 
your requested cell size in meters</font></h3>
    <form action="%(SCRIPT_NAME)s" method="POST" enctype="multipart/form-data">"""
    print "Content-type: text/html\n"
    print HTML_TEMPLATE_HEAD % {'SCRIPT_NAME':SCRIPT_NAME}

def print_html_body():

    HTML_XDIM = """X0: <input name="x0_dim" type="text" size="4"> &nbsp;&nbsp;X1: <input name="x1_dim" type="text" size="4"><br/>"""
    HTML_YDIM = """Y0: <input name="y0_dim" type="text" size="4"> &nbsp;&nbsp;Y1: <input name="y1_dim" type="text" size="4"><br/>"""
    HTML_ZDIM = """Z0: <input name="z0_dim" type="text" size="4"> &nbsp;&nbsp;Z1: <input name="z1_dim" type="text" size="4"><br/><br/>"""
    HTML_DX = """Requested cell size (for dx, dy, and dz): <input name="dx" type="text" size="4"><br/><br/>"""
    HTML_SUBMIT = """<input name="submit" type="submit" value="Calculate MESH Line"><br/><br/>"""

    print HTML_XDIM
    print HTML_YDIM
    print HTML_ZDIM
    print HTML_DX
    print HTML_SUBMIT

def print_html_footer():
    HTML_TEMPLATE_FOOT = """</font>
    </form>
    </body>
    </html>"""
    print HTML_TEMPLATE_FOOT

def check_input_fields(x0_dim="", x1_dim="", y0_dim="", y1_dim="", z0_dim="", z1_dim="", dx=""):
    # Writes fields and values to lists for input looping
    global input_fields
    global input_values
    input_fields = ("X0", "X1", "Y0", "Y1", "Z0", "Z1", "DX")
    input_values = (x0_dim, x1_dim, y0_dim, y1_dim, z0_dim, z1_dim, dx)

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
    for field in input_values:
        try:
            float(field)
        except:
            print """<h2><font color="red">""" + input_fields[count] + """ is not a valid number</font></h2><br/>"""
            fill_previous_values()
            sys.exit()
        count += 1    
    
    check_x0 = float(x0_dim)
    check_x1 = float(x1_dim)
    check_y0 = float(y0_dim)
    check_y1 = float(y1_dim)
    check_z0 = float(z0_dim)
    check_z1 = float(z1_dim)
    check_dx = float(dx)

    #### Add error checking for non-numbers
    
    if check_x1 < check_x0:
        print """<h2><font color="red">X1 should be greater than X0</font></b>"""
        fill_previous_values()
        sys.exit()
    if check_y1 < check_y0:
        print """<h2><font color="red">Y1 should be greater than Y0</font></b>"""
        fill_previous_values()
        sys.exit()
    if check_z1 < check_z0:
        print """<h2><font color="red">Z1 should be greater than Z0</font></b>"""
        fill_previous_values()
        sys.exit()
    
    # Checks if the specified distance dx is greater than zero    
    if check_dx <= 0:
        print """<h2><font color="red">The cell size <b>dx</b> must be greater than zero</font></b>"""
        fill_previous_values()
        sys.exit()
        
    compute(x0_dim, x1_dim, y0_dim, y1_dim, z0_dim, z1_dim, dx)
        
# Calculates the desired I,J,K values and sends them to the Poisson optimizer for checking/calculation
def compute(x0_dim, x1_dim, y0_dim, y1_dim, z0_dim, z1_dim, dx):
    global x_dim, y_dim, z_dim
    
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
        sys.exit()
    if y_dim == 0:
        print """<h2><font color="red">Y dimension cannot be zero</font></h2>"""
        fill_previous_values()
        sys.exit()
    if z_dim == 0:
        print """<h2><font color="red">Z dimension cannot be zero</font></h2>"""
        fill_previous_values()
        sys.exit()
    
    # Checks to see if dx is bigger than any single dimension
    if (dx > x_dim) | (dx > y_dim) | (dx > z_dim):
        print """<h2><font color="red">dx cannot be greater than any x, y, or z dimension</font></h2><br/>"""
        fill_previous_values()
        sys.exit()
    
    desired_i = x_dim / dx
    desired_j = y_dim / dx
    desired_k = z_dim / dx
    
    Poisson(int(desired_i), "IBAR")
    Poisson(int(desired_j), "JBAR")
    Poisson(int(desired_k), "KBAR")

def fname():
    """docstring for fname"""
    pass


def Poisson(desired_num, dimension):
    """Uses mod 2, 3, 5 to see if numbers are Poisson optimized.
    If they are not, it goes from x to x*1.2 in increments of 1 and rechecks until factorable
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
            # print dimension
            # print int(desired_num)
            # print "<br/>"
            ijk_bars.append(int(desired_num))
            break
        else:
            desired_num = desired_num + 1
            continue

def fill_previous_values():
    js_form_fill = """<script type="text/javascript">
          document.forms[0].%(FORM_ELEMENT_NAME)s.value = '%(FORM_VALUE)s';
          </script>"""
    form_field_names = ("x0_dim", "x1_dim", "y0_dim", "y1_dim", "z0_dim", "z1_dim", "dx")
    # Loops through form fields and writes out a custom javascript line for each element
    # to keep the previously typed number in the form
    form_count = 0
    for field in input_values:
        print js_form_fill % {'FORM_ELEMENT_NAME':form_field_names[form_count], 'FORM_VALUE':field}
        form_count += 1

def print_output_results():
    print "<br/>"
    
    print "Your MESH line for FDS is:<br/><h2>&MESH IJK=" + str(ijk_bars[0]) + "," + str(ijk_bars[1]) + "," + str(ijk_bars[2]) + ", XB=" + str(x0_dim) + "," + str(x1_dim) + "," + str(y0_dim) + "," + str(y1_dim) + "," + str(z0_dim) + "," + str(z1_dim) + " /</h2>"

    print "You entered: " , "<br/><b>x0:</b> ",x0_dim, "<b>x1:</b> ",x1_dim, "<br/><b>y0:</b> ",y0_dim, "<b>y1:</b> ",y1_dim, "<br/><b>z0:</b> ",z0_dim, "<b>z1:</b> ",z1_dim, "<br/><b>dx:</b> ",dx
    
    print "<br/><br/>"
    
    print "Your actual dx(es) are: ", round(x_dim/ijk_bars[0],3), round(y_dim/ijk_bars[1],3), round(z_dim/ijk_bars[2],3), 
    print "<br/>"
    
    print "Your distances are:", x_dim, y_dim, z_dim
    print "<br/>"
    
    totnumcells = ijk_bars[0] * ijk_bars[1] * ijk_bars[2]
    print "Your total number of cells is: ", totnumcells
    
###############################################################
#  Actual start of execution of script using above functions  #
###############################################################
    
print_html_header()
# (x_existing, y_existing, z_existing, dx_existing) = write_existing_html_values()

print_html_body()

try:
    x0_dim = form["x0_dim"].value
    x1_dim = form["x1_dim"].value
    y0_dim = form["y0_dim"].value
    y1_dim = form["y1_dim"].value
    z0_dim = form["z0_dim"].value
    z1_dim = form["z1_dim"].value
    dx = form["dx"].value
except:
    sys.exit()

check_input_fields(x0_dim, x1_dim, y0_dim, y1_dim, z0_dim, z1_dim, dx)

fill_previous_values()

print_output_results()

js_form_textbox_red = """<script type="text/javascript">
document.getElementById("x0_dim").style.color="red";
</script>"""

js_form_textbox_red_2 = """<script type="text/javascript">
x0_dim.style.backgroundColor = "#FF0000";
</script>"""

print js_form_textbox_red_2

print_html_footer()

##### Put in line to show ACTUAL cell dimensions

###### put in multiple input forms for multimesh cases
