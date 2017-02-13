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

import numpy as np
import cgi, sys, time, re

import cgitb
cgitb.enable()

# Variables to script path and that gather form fields
SCRIPT_NAME = '/cgi-bin/chemical_equation_balancer/index_chemical_balancer.cgi'
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
    <label>Chemical formula of fuel </label>
    <input class="input-small" name="input_formula" type="text" size="4" value="C3H8"><br/><br/>

    <label>Carbon monoxide yield (kg/kg)</label>
    <input class="input-small" name="input_Y_CO" type="text" size="4" value="0.00"><br/><br/>

    <label>Soot yield (kg/kg)</label>
    <input class="input-small" name="input_Y_s" type="text" size="4" value="0.00"><br/><br/>

    <label>Hydrogen atomic fraction in soot </label>
    <input class="input-small" name="input_X_H" type="text" size="4" value="0.00"><br/><br/>

    <b>Volume fractions of background species: </b>
    <label>Fuel: </label>
    <input class="input-small" name="input_bg_1" type="text" size="4" value="0.00"><br/>
    <label>O<sub>2</sub> </label>
    <input class="input-small" name="input_bg_2" type="text" size="4" value="0.208"><br/>
    <label>N<sub>2</sub>: </label>
    <input class="input-small" name="input_bg_3" type="text" size="4" value="0.783"><br/>
    <label>H<sub>2</sub>O: </label>
    <input class="input-small" name="input_bg_4" type="text" size="4" value="0.00834"><br/>
    <label>CO<sub>2</sub>: </label>
    <input class="input-small" name="input_bg_5" type="text" size="4" value="0.000387"><br/>
    <label>CO: </label>
    <input class="input-small" name="input_bg_6" type="text" size="4" value="0.00"><br/>
    <label>Soot: </label>
    <input class="input-small" name="input_bg_7" type="text" size="4" value="0.00"><br/><br/>

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
        input_formula = form["input_formula"].value
        input_Y_s = form["input_Y_s"].value
        input_Y_CO = form["input_Y_CO"].value
        input_X_H = form["input_X_H"].value
        input_bg_1 = form["input_bg_1"].value
        input_bg_2 = form["input_bg_2"].value
        input_bg_3 = form["input_bg_3"].value
        input_bg_4 = form["input_bg_4"].value
        input_bg_5 = form["input_bg_5"].value
        input_bg_6 = form["input_bg_6"].value
        input_bg_7 = form["input_bg_7"].value
    except:
        print_html_footer()
        sys.exit()

    # Writes fields and values to lists for input looping
    global input_fields
    global input_values
    input_fields = ("input_formula", "input_Y_s", "input_Y_CO", "input_X_H", "input_bg_1", "input_bg_2", "input_bg_3", "input_bg_4", "input_bg_5", "input_bg_6", "input_bg_7")
    input_values = (input_formula, input_Y_s, input_Y_CO, input_X_H, input_bg_1, input_bg_2, input_bg_3, input_bg_4, input_bg_5, input_bg_6, input_bg_7)

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
    try:
        float(input_Y_s)
        float(input_Y_CO)
        float(input_X_H)
        float(input_bg_1)
        float(input_bg_2)
        float(input_bg_3)
        float(input_bg_4)
        float(input_bg_5)
        float(input_bg_6)
        float(input_bg_7)
    except:
        print """<h2><font color="red">Soot yield is not a valid number</font></h2><br/>"""
        fill_previous_values()
        sys.exit()

    formula = input_formula
    y_s = float(input_Y_s)
    y_CO = float(input_Y_CO)
    X_H = float(input_X_H)
    bg_1 = float(input_bg_1)
    bg_2 = float(input_bg_2)
    bg_3 = float(input_bg_3)
    bg_4 = float(input_bg_4)
    bg_5 = float(input_bg_5)
    bg_6 = float(input_bg_6)
    bg_7 = float(input_bg_7)

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

    ### Based on work on a previous Matlab script by: ###
    # Randall McDermott
    # 3-31-11
    # fds_simple_chemistry.m
    #
    # This script is a distilled version of the SIMPLE_CHEMISTRY routine in FDS and may be
    # used as a check on reaction coefficients for primitive and lumped species.

    # Molecular weights of C, H, O, N
    MW_C = 12.0107
    MW_H = 1.00794
    MW_O = 15.9994
    MW_N = 14.0067

    # define the element matrix (number of atoms [rows] for each primitive species [columns])

    i_fuel            = 0
    i_oxygen          = 1
    i_nitrogen        = 2
    i_water_vapor     = 3
    i_carbon_dioxide  = 4
    i_carbon_monoxide = 5
    i_soot            = 6

    E = np.matrix([[C, 0, 0, 0, 1, 1, (1-X_H)],              # C
                   [H, 0, 0, 2, 0, 0, X_H    ],              # H
                   [O, 2, 0, 1, 2, 1, 0      ],              # O
                   [N, 0, 2, 0, 0, 0, 0]     ], dtype=float) # N

    MW = np.matrix([MW_C, MW_H, MW_O, MW_N]) # primitive species molecular weights

    W = E.T * MW.T

    # define the volume fractions of the background and fuel

    v_0 = np.matrix([bg_1, bg_2, bg_3, bg_4, bg_5, bg_6, bg_7], dtype=float)
    v_0 = v_0/np.sum(v_0) # normalize

    # print v_0

    v_1 = np.matrix([1, 0, 0, 0, 0, 0, 0], dtype=float)
    v_1 = v_1/np.sum(v_1) # normalize

    # the reaction coefficients for the product primitive species temporarily stored in v_2

    v_2 = np.matrix([0, 0, 0, 0, 0, 0, 0], dtype=float)

    # compute what we know so far

    v_2[0,i_carbon_monoxide] = W.item(i_fuel) / W.item(i_carbon_monoxide) * y_CO
    v_2[0,i_soot]            = W.item(i_fuel) / W.item(i_soot) * y_s

    # linear system right hand side

    b = E * (v_1.T - v_2.T)

    # matrix

    L = np.column_stack([E*v_0.T, E[:,i_carbon_dioxide], E[:,i_water_vapor], E[:,i_nitrogen]])

    # solve the system

    x = np.linalg.inv(L)*b

    nu_0                    = x.item(0) # background stoichiometric coefficient
    v_2.T[i_carbon_dioxide] = x.item(1)
    v_2.T[i_water_vapor]    = x.item(2)
    v_2.T[i_nitrogen]       = x.item(3)

    nu_1 = -1 # fuel stoich coeff
    nu_2 = np.sum(v_2) # prod stoich coeff

    v_2 = v_2/nu_2 # normalize volume fractions

    # display fuel properties

    Z2Y = np.row_stack([v_0, v_1, v_2])

    Z2Y = Z2Y.T

    coeff_fuel = Z2Y[0,1] # Fuel

    coeff_lhs_1 = Z2Y[0,0] # Fuel
    coeff_lhs_2 = Z2Y[1,0] # O2
    coeff_lhs_3 = Z2Y[2,0] # N2
    coeff_lhs_4 = Z2Y[3,0] # H2O
    coeff_lhs_5 = Z2Y[4,0] # CO2
    coeff_lhs_6 = Z2Y[5,0] # CO
    coeff_lhs_7 = Z2Y[6,0] # C

    coeff_rhs_1 = Z2Y[0,2] # Fuel
    coeff_rhs_2 = Z2Y[1,2] # O2
    coeff_rhs_3 = Z2Y[2,2] # N2
    coeff_rhs_4 = Z2Y[3,2] # H2O
    coeff_rhs_5 = Z2Y[4,2] # CO2
    coeff_rhs_6 = Z2Y[5,2] # CO
    coeff_rhs_7 = Z2Y[6,2] # C

    #  =================
    #  = Print results =
    #  =================

    # Print extra decimal precision if selected
    try:
        form["sel_prec_value"].value
        decimal_precision = 6
    except KeyError:
        decimal_precision = 3

    if np.min(np.array([coeff_lhs_1, coeff_lhs_2, coeff_lhs_3, coeff_lhs_4, coeff_lhs_5, coeff_lhs_6, coeff_lhs_7,
              coeff_rhs_1, coeff_rhs_2, coeff_rhs_3, coeff_rhs_4, coeff_rhs_5, coeff_rhs_6, coeff_rhs_7])) < 0:
        print """<h2><font color="red">Error: Results include negative stoichiometric coefficients. Check inputs.</font></h2><br/>"""
        fill_previous_values()
        sys.exit()

    FORMULA_OUTPUT = """
    <h3>Balanced chemical equation</h3>
    <h4>Reactants: <br><br>
    """

    FORMULA_OUTPUT += '<font color="red">{num:.{prec}f}</font> {text}'.format(num=coeff_fuel, prec=decimal_precision, text=formula.upper())
    FORMULA_OUTPUT += '&nbsp;+ <font color="red">{num:.{prec}f}</font>('.format(num=np.abs(nu_0), prec=decimal_precision)

    if coeff_lhs_2 != 0:
        FORMULA_OUTPUT += '<font color="blue">{num:.{prec}f}</font>&nbsp;O<sub>2</sub>'.format(num=coeff_lhs_2, prec=decimal_precision)
    if coeff_lhs_3 != 0:
        FORMULA_OUTPUT += ' + <font color="blue">{num:.{prec}f}</font>&nbsp;N<sub>2</sub>'.format(num=coeff_lhs_3, prec=decimal_precision)
    if coeff_lhs_4 != 0:
        FORMULA_OUTPUT += ' + <font color="blue">{num:.{prec}f}</font>&nbsp;H<sub>2</sub>O'.format(num=coeff_lhs_4, prec=decimal_precision)
    if coeff_lhs_5 != 0:
        FORMULA_OUTPUT += ' + <font color="blue">{num:.{prec}f}</font>&nbsp;CO<sub>2</sub>'.format(num=coeff_lhs_5, prec=decimal_precision)
    if coeff_lhs_6 != 0:
        FORMULA_OUTPUT += ' + <font color="blue">{num:.{prec}f}</font>&nbsp;CO'.format(num=coeff_lhs_6, prec=decimal_precision)
    if coeff_lhs_7 != 0:
        FORMULA_OUTPUT += ' + <font color="blue">{num:.{prec}f}</font>&nbsp;C'.format(num=coeff_lhs_7, prec=decimal_precision)

    FORMULA_OUTPUT += ') <br><br> &darr; <br><br> Products: <br><br> <font color="red">{num:.{prec}f}</font>('.format(num=np.abs(nu_2), prec=decimal_precision)

    if coeff_rhs_2 != 0:
        FORMULA_OUTPUT += ' + <font color="blue">{num:.{prec}f}</font>&nbsp;O<sub>2</sub>'.format(num=coeff_rhs_2, prec=decimal_precision)
    if coeff_rhs_3 != 0:
        FORMULA_OUTPUT += '<font color="blue">{num:.{prec}f}</font>&nbsp;N<sub>2</sub>'.format(num=coeff_rhs_3, prec=decimal_precision)
    if coeff_rhs_4 != 0:
        FORMULA_OUTPUT += ' + <font color="blue">{num:.{prec}f}</font>&nbsp;H<sub>2</sub>O'.format(num=coeff_rhs_4, prec=decimal_precision)
    if coeff_rhs_5 != 0:
        FORMULA_OUTPUT += ' + <font color="blue">{num:.{prec}f}</font>&nbsp;CO<sub>2</sub>'.format(num=coeff_rhs_5, prec=decimal_precision)
    if coeff_rhs_6 != 0:
        FORMULA_OUTPUT += ' + <font color="blue">{num:.{prec}f}</font>&nbsp;CO'.format(num=coeff_rhs_6, prec=decimal_precision)
    if coeff_rhs_7 != 0:
        FORMULA_OUTPUT += ' + <font color="blue">{num:.{prec}f}</font>&nbsp;C'.format(num=coeff_rhs_7, prec=decimal_precision)

    FORMULA_OUTPUT += ')</h4>'

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
