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
SCRIPT_NAME = '/cgi-bin/chemical_equation_balancer/index_alternate.cgi'
form = cgi.FieldStorage()

# Writes out html page templates and form fields
def print_html_header():
    HTML_TEMPLATE_HEAD = """<!DOCTYPE HTML>
    <html><head><title>Chemical Equation Balancer</title>
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
    <h4>Reactants</h4>
    <label>Chemical formula of fuel </label>
    <input class="input-small" name="sel_formula" type="text" size="4" value="C7H16"><br/><br/>
    
    <label>Nitrogen (mol) </label>
    <input class="input-small" name="sel_X_n2" type="text" size="4" value="0.77"><br/><br/>

    <label>Oxygen (mol) </label>
    <input class="input-small" name="sel_X_o2" type="text" size="4" value="0.20"><br/><br/>

    <label>Carbon dioxide (mol) </label>
    <input class="input-small" name="sel_X_co2" type="text" size="4" value="0.01"><br/><br/>

    <label>Water vapor (mol) </label>
    <input class="input-small" name="sel_X_h2o" type="text" size="4" value="0.02"><br/><br/>

    <h4>Products</h4>

    <label>Soot yield (kg/kg) </label>
    <input class="input-small" name="sel_Y_s" type="text" size="4" value="0.01"><br/><br/>

    <label>Carbon monoxide yield (kg/kg) </label>
    <input class="input-small" name="sel_Y_co" type="text" size="4" value="0.01"><br/><br/>

    <label><input type="checkbox" name="sel_prec_value" value="prec" id="prec">
    &nbsp;Print extra decimal precision </label>
    """

    CHEM_INPUT = """<table border=0>
    <tr><td colspan=3 align='right'><br/><input class="btn btn-large btn-primary" name="submit" type="submit" value="Balance chemical equation"></td></td></table><br/>
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
        sel_X_o2 = form["sel_X_o2"].value
        sel_X_n2 = form["sel_X_n2"].value
        sel_X_co2 = form["sel_X_co2"].value
        sel_X_h2o = form["sel_X_h2o"].value
        sel_Y_s = form["sel_Y_s"].value
        sel_Y_co = form["sel_Y_co"].value
    except:
        print_html_footer()
        sys.exit()
    
    # Writes fields and values to lists for input looping
    global input_fields
    global input_values
    input_fields = ("sel_formula", "sel_X_o2", "sel_X_n2", "sel_X_co2", "sel_X_h2o", "sel_Y_s", "sel_Y_co")
    input_values = (sel_formula, sel_X_o2, sel_X_n2, sel_X_co2, sel_X_h2o, sel_Y_s, sel_Y_co)

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
        float(sel_X_o2)
        float(sel_X_n2)
        float(sel_X_co2)
        float(sel_X_h2o)
        float(sel_Y_s)
        float(sel_Y_co)
    except:
        print """<h2><font color="red">Check inputs for an invalid entry</font></h2><br/>"""
        fill_previous_values()
        sys.exit()

    sel_X_o2 = float(sel_X_o2)
    sel_X_n2 = float(sel_X_n2)
    sel_X_co2 = float(sel_X_co2)
    sel_X_h2o = float(sel_X_h2o)
    sel_Y_s = float(sel_Y_s)
    sel_Y_co = float(sel_Y_co)
    
    formula = sel_formula
    O2_lhs = sel_X_o2
    N2_lhs = sel_X_n2
    CO2_lhs = sel_X_co2
    H2O_lhs = sel_X_h2o
    water_vapor = sel_X_h2o
    co2 = sel_X_co2
    water_vapor = sel_X_h2o
    soot_yield = sel_Y_s
    co_yield = sel_Y_co

    #  ==========================
    #  = Parse chemical formula =
    #  ==========================

    C, H, O, N = 0, 0, 0, 0

    # Search for C, H, O, N atoms in formula
    match = re.search('[cC](\d+\.?\d*)', formula)
    if match:
        C = match.group(1)
    match = re.search('[hH](\d+\.?\d*)', formula)
    if match:
        H = match.group(1)
    match = re.search('[oO](\d+\.?\d*)', formula)
    if match:
        O = match.group(1)
    match = re.search('[nN](\d+\.?\d*)', formula)
    if match:
        N = match.group(1)

    # If an atom is included with no number following,
    # then assign it a value of 1
    if (C == 0) and ('C' in formula):
        C = 1
    if (H == 0) and ('H' in formula):
        H = 1
    if (O == 0) and ('O' in formula):
        O = 1
    if (N == 0) and ('N' in formula):
        N = 1

    # Convert all atom numbers to floats
    C = float(C)
    H = float(H)
    O = float(O)
    N = float(N)

    # Throw error if formula does not include C or H
    if ((C == 0) or (H == 0)):
        print """<h2><font color="red">C and H must be included in the fuel</font></h2><br/>"""
        fill_previous_values()
        sys.exit()

    #  ==========================================
    #  = Chemical equation balance calculations =
    #  ==========================================

    # Molecular weights of C, H, O, N
    MW_C = 12.0107
    MW_H = 1.00794
    MW_O = 15.9994
    MW_N = 14.0067

    C_rhs = ((C * MW_C) + (H * MW_H) + (O * MW_O) + (N * MW_N)) * (soot_yield / MW_C)
    CO_rhs = ((C * MW_C) + (H * MW_H) + (O * MW_O) + (N * MW_N)) * (co_yield / (MW_C + MW_O))

    fuel_lhs = 1
    C_lhs = C + CO2_lhs
    H_lhs = H + H2O_lhs * 2
    O_lhs = O
    N_lhs = N2_lhs * 2

    CO2_rhs = C_lhs - C_rhs - CO_rhs
    H2O_rhs = H_lhs / 2
    N2_rhs = N_lhs / 2

    try:
        form["sel_prec_value"].value              
        precision = "%0.6f"
    except KeyError:
        precision = "%0.4f"

    #  =================
    #  = Print results =
    #  =================

    # Check for existence of CO2 in reactants
    if CO2_lhs > 0:
        CO2_reac = ' + <font color="blue">' + precision % CO2_lhs + ' </font> CO<sub>2</sub> '
    else:
        CO2_reac = ''

    # Check for existence of H2O in reactants
    if H2O_lhs > 0:
        H2O_reac = ' + <font color="blue">' + precision % H2O_lhs + ' </font> H<sub>2</sub>O '
    else:
        H2O_reac = ''

    # Check for existence of C in products
    if C_rhs > 0:
        C_prod = '+ <font color="blue">' + precision % C_rhs + '</font> C '
    else:
        C_prod = ''

    # Check for existence of CO in products
    if CO_rhs > 0:
        CO_prod = '+ <font color="blue">' + precision % CO_rhs + '</font> CO '
    else:
        CO_prod = ''

    FORMULA_OUTPUT = ('<h3>Balanced chemical equation</h3>' +
                      '<h4>Reactants: <br><br> <font color="blue">' +
                      precision % fuel_lhs +
                      '</font> ' +
                      formula.upper() +
                      ' + <font color="blue"> ' +
                      precision % N2_lhs +
                      ' </font> N<sub>2</sub> + <font color="blue">' +
                      precision % O2_lhs +
                      ' </font> O<sub>2</sub>' +
                      CO2_reac +
                      H2O_reac +
                      '<br><br> &darr; <br><br>' +
                      ' <br><br> Products: <br><br>' +
                      '<font color="blue">' +
                      precision % N2_rhs +
                      '</font> N<sub>2</sub> + <font color="blue">' +
                      precision % CO2_rhs +
                      '</font> CO<sub>2</sub> + <font color="blue">' +
                      precision % H2O_rhs +
                      '</font> H<sub>2</sub>O ' +
                      CO_prod +
                      C_prod +
                      '</h4>')

    print FORMULA_OUTPUT
    
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
        # Set previous value of checkboxes
        try:
            form["sel_prec_value"].value
            print "document.forms[0].sel_prec_value.checked = true;"
        except KeyError:
            pass
        print "</script>"
        form_count += 1
    
    
###############################################################
#  Actual start of execution of script using above functions  #
###############################################################

print_html_header()

print_html_body()

check_input_fields()

fill_previous_values()

print_html_footer()
