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
from math import sqrt
import cgi, sys

import cgitb
cgitb.enable()

# Variables to script path and that gather form fields
SCRIPT_NAME = '/cgi-bin/fds_mesh/dstar.cgi'
form = cgi.FieldStorage()

ijk_bars = []

# Writes out html page templates and form fields
def print_html_header():
    HTML_TEMPLATE_HEAD = """<!DOCTYPE HTML PUBLIC "-//W3C//DTD HTML 4.01 Transitional//EN">
    <html><head><title>FDS v5 Mesh Size Calculator</title>
    <meta http-equiv="Content-Type" content="text/html; charset=iso-8859-1">
    </head><body>
    <h3><FONT FACE="Arial, Helvetica, Geneva">Enter your HRR size in kW</h3>
    The D* (d-star) method is given by the following relationship:<br/>
    <img src="dstarform.png"><br/><br/>
    <form action="%(SCRIPT_NAME)s" method="POST" enctype="multipart/form-data">"""
    print "Content-type: text/html\n"
    print HTML_TEMPLATE_HEAD % {'SCRIPT_NAME':SCRIPT_NAME}

def print_html_body():

    HTML_VALUES = """<table border=0>
    <tr>
        <td align='right'><b>Heat Release Rate </b> (HRR): </td>
        <td> <input name="hrr" type="text" size="4"> </td>
        <td> kW </td>
    </tr>
    <tr>
        <td align='right'><b>Density </b> (p_inf): </td>
        <td> <input name="p_inf" type="text" size="4" value="1.204"> </td>
        <td> kg / m^3 </td>
    </tr>
    <tr>
        <td align='right'><b>Specific Heat </b> (c_p): </td>
        <td> <input name="cp" type="text" size="4" value="1.005"> </td>
        <td> kJ / kg-K </td>
    </tr>
    <tr>
        <td align='right'><b>Ambient Temperature </b> (T_inf): </td>
        <td> <input name="t_inf" type="text" size="4" value="293"> </td>
        <td> K </td>
    </tr>
    <tr>
        <td align='right'><b>Gravity </b> (g): </td>
        <td> <input name="grav" type="text" size="4" value="9.81"> </td>
        <td> m / s^2 </td>
    </tr>

    """
    
    HTML_SUBMIT = """<tr><td colspan=3 align='right'><br/><input name="submit" type="submit" value="Calculate suggested cell sizes"></td></td></table><br/><br/>"""

    print HTML_VALUES
    print HTML_SUBMIT

def print_html_footer():
    HTML_TEMPLATE_FOOT = """</font>
    </form>
    </body>
    </html>"""
    print HTML_TEMPLATE_FOOT

def check_input_fields(hrr="", p_inf="", cp="", t_inf="", grav=""):
    # Writes fields and values to lists for input looping
    global input_fields
    global input_values
    input_fields = ("hrr", "p_inf", "cp", "t_inf", "grav")
    input_values = (hrr, p_inf, cp, t_inf, grav)

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
    
    compute(hrr, p_inf, cp, t_inf, grav)
        
# Calculates the desired I,J,K values and sends them to the Poisson optimizer for checking/calculation
def compute(hrr, p_inf, cp, t_inf, grav):
    # global x_dim, y_dim, z_dim
    
    hrr = float(hrr)
    p_inf = float(p_inf)
    cp = float(cp)
    t_inf = float(t_inf)
    grav = sqrt(float(grav))
    
    dstar_power = float("0.4")
    
    d_star = pow((hrr / (p_inf * cp * t_inf * grav) ), dstar_power)
    print "D* = ", round(d_star, 3)
    
    uguide_min_suggested_dx = d_star / 16
    uguide_max_suggested_dx = d_star / 4
    
    print "<br/><br/>"
    print "User Guide recommendation of D*/dx = 16:<br/>", round(uguide_min_suggested_dx, 3), "m <br/><br/>"
    print "User Guide recommendation of D*/dx = 4:<br/>", round(uguide_max_suggested_dx, 3), "m <br/><br/>"

    nrc_min_suggested_dx = d_star / 10
    nrc_max_suggested_dx = d_star / 5
    print "NRC NUREG recommendation of D*/dx = 10:<br/>", round(nrc_min_suggested_dx, 3), "m <br/><br/>"
    print "NRC NUREG recommendation of D*/dx = 5:<br/>", round(nrc_max_suggested_dx, 3), "m <br/><br/>"

# def Poisson(desired_num, dimension):
#     """Uses mod 2, 3, 5 to see if numbers are Poisson optimized.
#     If they are not, it goes from x to x*1.2 in increments of 1 and rechecks until factorable
#     Then it returns the factorable and Poisson-friendly I,J,K values"""
#     for i in range(desired_num*Decimal("1.4")):
#         global ijk_bars
#         check_digit = desired_num
#         while check_digit % 2 == 0:
#             check_digit = check_digit / 2
#         while check_digit % 3 == 0:
#             check_digit = check_digit / 3
#         while check_digit % 5 == 0:
#             check_digit = check_digit / 5
#     
#         if check_digit in (1, 2, 3, 5):
#             # print dimension
#             # print int(desired_num)
#             # print "<br/>"
#             ijk_bars.append(int(desired_num))
#             break
#         else:
#             desired_num = desired_num + 1
#             continue

def fill_previous_values():
    js_form_fill = """<script type="text/javascript">
          document.forms[0].%(FORM_ELEMENT_NAME)s.value = '%(FORM_VALUE)s';
          </script>"""
    form_field_names = ("hrr", "p_inf", "cp", "t_inf", "grav")
    # Loops through form fields and writes out a custom javascript line for each element
    # to keep the previously typed number in the form
    form_count = 0
    for field in input_values:
        print js_form_fill % {'FORM_ELEMENT_NAME':form_field_names[form_count], 'FORM_VALUE':field}
        form_count += 1

def print_output_results():
    print "<br/>"
    
    # print "Your MESH line for FDS is:<br/><h2>&MESH IJK=" + str(ijk_bars[0]) + "," + str(ijk_bars[1]) + "," + str(ijk_bars[2]) + ", XB=" + str(x0_dim) + "," + str(x1_dim) + "," + str(y0_dim) + "," + str(y1_dim) + "," + str(z0_dim) + "," + str(z1_dim) + " /</h2>"
    # 
    # print "You entered: " , "<br/><b>x0:</b> ",x0_dim, "<b>x1:</b> ",x1_dim, "<br/><b>y0:</b> ",y0_dim, "<b>y1:</b> ",y1_dim, "<br/><b>z0:</b> ",z0_dim, "<b>z1:</b> ",z1_dim, "<br/><b>dx:</b> ",dx
    # 
    # print "<br/><br/>"
    # 
    # print "Your actual dx(es) are: ", round(x_dim/ijk_bars[0],3), round(y_dim/ijk_bars[1],3), round(z_dim/ijk_bars[2],3), 
    # print "<br/>"
    # print "Your distances are:", x_dim, y_dim, z_dim
    
###############################################################
#  Actual start of execution of script using above functions  #
###############################################################
    
print_html_header()

print_html_body()

try:
    hrr = form["hrr"].value
    p_inf = form["p_inf"].value
    cp = form["cp"].value
    t_inf = form["t_inf"].value
    grav = form["grav"].value
except:
    sys.exit()

check_input_fields(hrr, p_inf, cp, t_inf, grav)

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
