#!/home/koverholt/bin/python

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

import numpy as np
import cgi, sys, time, re

import cgitb
cgitb.enable()

# Variables to script path and that gather form fields
SCRIPT_NAME = '/cgi-bin/chemical_reaction_balancer/index.cgi'
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
    HTML_INPUTS = """    
    <label>Chemical formula of fuel </label>
    <input class="input-small" name="sel_formula" type="text" size="4" value="C3H8"><br/><br/>
    
    <label>Soot yield </label>
    <input class="input-small" name="sel_Y_s" type="text" size="4" value="0.01"><br/><br/>

    <input type="checkbox" name="sel_prec_value" value="prec" id="prec">
    &nbsp;Print extra decimal precision <br/>
    """

    CHEM_INPUT = """<table border=0>
    <tr><td colspan=3 align='right'><br/><input class="btn btn-large btn-primary" name="submit" type="submit" value="Balance chemical reaction"></td></td></table><br/>
    """

    print HTML_INPUTS
    print CHEM_INPUT

def print_html_footer():
    HTML_TEMPLATE_FOOT = """</font>
    </form>
    </body>
    </html>"""
    print HTML_TEMPLATE_FOOT

def check_input_fields():
    
    try:
        sel_formula = form["sel_formula"].value
        sel_Y_s = form["sel_Y_s"].value
    except:
        print_html_footer()
        sys.exit()
    
    # Writes fields and values to lists for input looping
    global input_fields
    global input_values
    input_fields = ("sel_formula", "sel_Y_s")
    input_values = (sel_formula, sel_Y_s)

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
        float(sel_Y_s)
    except:
        print """<h2><font color="red">Soot yield is not a valid number</font></h2><br/>"""
        fill_previous_values()
        sys.exit()
        
    sel_Y_s = float(sel_Y_s)

    formula = sel_formula
    soot_yield = sel_Y_s

    #  ==========================
    #  = Parse chemical formula =
    #  ==========================

    C, H, O, N = 0, 0, 0, 0

    match = re.search('C(\d+\.?\d*)', formula)
    if match:
        C = match.group(1)
    match = re.search('H(\d+\.?\d*)', formula)
    if match:
        H = match.group(1)
    match = re.search('O(\d+\.?\d*)', formula)
    if match:
        O = match.group(1)
    match = re.search('N(\d+\.?\d*)', formula)
    if match:
        N = match.group(1)

    if (C == 0) and ('C' in formula):
        C = 1
    if (H == 0) and ('H' in formula):
        H = 1
    if (O == 0) and ('O' in formula):
        O = 1
    if (N == 0) and ('N' in formula):
        N = 1

    C = float(C)
    H = float(H)
    O = float(O)
    N = float(N)

    if ((C == 0) or (H == 0)):
        print """<h2><font color="red">C and H must be included in the reaction</font></h2><br/>"""
        fill_previous_values()
        sys.exit()

    #  ==========================================
    #  = Chemical reaction balance calculations =
    #  ==========================================

    MW_C = 12.0107
    MW_H = 1.00794
    MW_O = 15.9994
    MW_N = 14.0067

    C_rhs = ((C * MW_C) + (H * MW_H)) / MW_C * soot_yield

    fuel_lhs = 1
    C_lhs = C
    H_lhs = H
    O_lhs = O
    N_lhs = N
    O2_lhs = 1
    N2_lhs = 3.7619

    CO2_rhs = C_lhs - C_rhs
    H2O_rhs = H_lhs / 2
    air_lhs = CO2_rhs + (H2O_rhs / 2) - (O_lhs / 2)
    N2_rhs = (air_lhs * N2_lhs) + (N_lhs / 2)

    #  =================
    #  = Print results =
    #  =================

    FORMULA_OUTPUT = """
    <h3>Balanced chemical reaction</h3>
    <h4>Reactants: <br><br> <font color="blue">%0.4f</font> %s + <font color="blue">%0.4f</font> (O<sub>2</sub> + 3.7619 N<sub>2</sub>) <br><br> &darr; <br><br> Products: <br><br> <font color="blue">%0.4f</font> CO<sub>2</sub> + <font color="blue">%0.4f</font> H<sub>2</sub>O + <font color="blue">%0.4f</font> N<sub>2</sub> + <font color="blue">%0.4f</font> C</h4>
    """

    FORMULA_OUTPUT_NO_SOOT = """
    <h3>Balanced chemical reaction</h3>
    <h4>Reactants: <br><br> <font color="blue">%0.4f</font> %s + <font color="blue">%0.4f</font> (O<sub>2</sub> + 3.7619 N<sub>2</sub>) <br><br> &darr; <br><br> Products: <br><br> <font color="blue">%0.4f</font> CO<sub>2</sub> + <font color="blue">%0.4f</font> H<sub>2</sub>O + <font color="blue">%0.4f</font> N<sub>2</sub>
    """

    FORMULA_OUTPUT_HI_PREC = """
    <h3>Balanced chemical reaction</h3>
    <h4>Reactants: <br><br> <font color="blue">%0.6f</font> %s + <font color="blue">%0.6f</font> (O<sub>2</sub> + 3.7619 N<sub>2</sub>) <br><br> &darr; <br><br> Products: <br><br> <font color="blue">%0.6f</font> CO<sub>2</sub> + <font color="blue">%0.6f</font> H<sub>2</sub>O + <font color="blue">%0.6f</font> N<sub>2</sub> + <font color="blue">%0.6f</font> C</h4>
    """

    FORMULA_OUTPUT_NO_SOOT_HI_PREC = """
    <h3>Balanced chemical reaction</h3>
    <h4>Reactants: <br><br> <font color="blue">%0.6f</font> %s + <font color="blue">%0.6f</font> (O<sub>2</sub> + 3.7619 N<sub>2</sub>) <br><br> &darr; <br><br> Products: <br><br> <font color="blue">%0.6f</font> CO<sub>2</sub> + <font color="blue">%0.6f</font> H<sub>2</sub>O + <font color="blue">%0.4f</font> N<sub>2</sub>
    """

    try:
        form["sel_prec_value"].value
        if soot_yield > 0:
            print FORMULA_OUTPUT_HI_PREC % (fuel_lhs, formula, air_lhs, CO2_rhs, H2O_rhs, N2_rhs, C_rhs)
        else:
            print FORMULA_OUTPUT_NO_SOOT_HI_PREC % (fuel_lhs, formula, air_lhs, CO2_rhs, H2O_rhs, N2_rhs)
    except KeyError:
        if soot_yield > 0:
            print FORMULA_OUTPUT % (fuel_lhs, formula, air_lhs, CO2_rhs, H2O_rhs, N2_rhs, C_rhs)
        else:
            print FORMULA_OUTPUT_NO_SOOT % (fuel_lhs, formula, air_lhs, CO2_rhs, H2O_rhs, N2_rhs)
    
def fill_previous_values():
    js_form_fill = """<script type="text/javascript">
          document.forms[0].%(FORM_ELEMENT_NAME)s.value = '%(FORM_VALUE)s';
          </script>"""
    # Loops through form fields and writes out a custom javascript line for each element
    # to keep the previously typed number in the form
    form_count = 0
    for field in input_values:
        print js_form_fill % {'FORM_ELEMENT_NAME':input_fields[form_count], 'FORM_VALUE':field}
        try:
            form["sel_prec_value"].value
            print """<script type="text/javascript">"""
            print "document.forms[0].sel_prec_value.checked = true;"
            print "</script>"
        except KeyError:
            pass
        form_count += 1
    
    
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

print_html_footer()
