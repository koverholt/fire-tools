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

########## USER INPUT HERE #############

# Size of x1 dimension in meters
x1 = Decimal("21.0")
# Size of x2 dimension in meters
x2 = Decimal("55.0")
# Requested dx for both meshes
dx1 = Decimal(".2")


########################################

print "Given x1:", x1, "m"
print "Given x2:", x2, "m"
print "Given dx:", dx1, "m\n"

ijk_bars_mesh1 = {}
ijk_bars_mesh2 = {}

actual_dx_mesh1 = {}
actual_dx_mesh2 = {}

smallest = [0, 0, 0]
compatible_ijk_values1 = []
compatible_ijk_values2 = []

pre_winning_values = {}

def Poisson(desired_num, mesh_number):                                            
    """Uses mod 2, 3, 5 to see if numbers are Poisson optimized.                
    If they are not, it goes from x to x*1.2 in increments of 1 and rechecks un$
    Then it returns the factorable and Poisson-friendly I,J,K values"""         
    for i in range(desired_num*Decimal("1.4")):                                 
        global ijk_bars                                                         
        check_digit = desired_num
        # print "Trying:", check_digit
        while check_digit % 2 == 0:                                             
            check_digit = check_digit / 2
            # print check_digit                                   
        while check_digit % 3 == 0:                                             
            check_digit = check_digit / 3                                       
            # print check_digit
        while check_digit % 5 == 0:                                             
            check_digit = check_digit / 5                                       
            # print check_digit
                                                                                
        if check_digit in (1, 2, 3, 5):                                         
            # print dimension                                                   
            # print int(desired_num)                                            
            # print "<br/>"                                                     
            if mesh_number == 1:
                ijk_bars_mesh1[int(desired_num)] = mesh_number
            elif mesh_number == 2:
                ijk_bars_mesh2[int(desired_num)] = mesh_number
            break                                                               
        else:                                                                   
            desired_num = desired_num + 1                                       
            continue

def sortedDictValues1(adict):
    items = adict.items()
    items.sort()
    return [value for key, value in items]

def sortedDictValues2(adict):
    items = adict.items()
    items.sort()
    return [key for key, value in items]

# x1 = Decimal(raw_input("Enter x for mesh 1"))
# x2 = Decimal(raw_input("Enter x for mesh 2"))
# dx1 = Decimal(raw_input("Enter dx for primary mesh 1"))
# dx2 = Decimal(raw_input("Enter multiple for mesh 2"))

# mesh_factor = int(x2 / x1)
# print "Mesh factor:", mesh_factor

requested_i1 = x1 / dx1
# print "Requested i1:", requested_i1

print "#### Finding ranges for 30% 'around' requested IJK values...\n"

i1_range = range(requested_i1-(requested_i1*Decimal("0.3")),(requested_i1+(requested_i1*Decimal("0.3")))+1)
print i1_range

for i in i1_range:
    Poisson(int(i), 1)

# print "To have mesh of a different magnitude, we will multiply the dx1 by the mesh factor"
# dx2 = dx1 / mesh_factor
# print "dx2:", dx2

requested_i2 = x2 / dx1
print requested_i2

i2_range = range(requested_i2-(requested_i2*Decimal("0.2")),(requested_i2+(requested_i2*Decimal("0.2")))+1)
print i2_range

for i in i2_range:
    Poisson(int(i), 2)

print "\n"
print "#### Storing valid Poisson IJK values within ranges...\n"
print ijk_bars_mesh1
print ijk_bars_mesh2

for ijk in ijk_bars_mesh1:
    actual_dx_mesh1[x1/ijk] = ijk
    
for ijk in ijk_bars_mesh2:
    actual_dx_mesh2[x2/ijk] = ijk

print "\n"
print "#### Calculating actual DXes for both MESHes...\n"
print actual_dx_mesh1
print "\n"
print actual_dx_mesh2

print "\n"
# for k in actual_dx_mesh1:
    
compatible_ijk_values1 = sortedDictValues1(actual_dx_mesh1)
compatible_ijk_values2 = sortedDictValues1(actual_dx_mesh2)

print "#### Printing IJK values found within 30% of given dx...\n"
print compatible_ijk_values1
print compatible_ijk_values2
print "\n"

print "#### Finding IJK values that are multiples of each other...\n"

for item in compatible_ijk_values1:
    temp_list = []
    # print item
    for match in compatible_ijk_values2:
        if item/Decimal("2") == match:
            temp_list.append(item/2)
        elif item/Decimal("3")  == match:
            temp_list.append(item/3)
        elif item/Decimal("4")  == match:
            temp_list.append(item/4)
        elif item*Decimal("2")  == match:
            temp_list.append(item*2)
        elif item*Decimal("3")  == match:
            temp_list.append(item*3)
        elif item*Decimal("4")  == match:
            temp_list.append(item*4)
                                
    # print "temp-list:", temp_list

    for ijk in temp_list:
        # print "Phase 1", item
        item_multiple = ijk
        # print "item_mult:", item_multiple
        actual_dx1 = x1/item
        actual_dx2 = x2/item_multiple
        diff = abs((x1/item)-(x2/item_multiple))
        # print "\n"
        if diff < Decimal("0.05"):
            print "#### Found one!"
            print item, "and", item_multiple, "are within tolerance (0.05 m) with a diff of", round(diff,3)
            print item, "gives a dx of", round(actual_dx1,3)
            print item_multiple, "gives a dx of", round(actual_dx2,3)
            dev_from_requested_dx1 = abs(actual_dx1-dx1)
            dev_from_requested_dx2 = abs(actual_dx2-dx1)
            print "MESH1 is off of requested dx:", dx1, "by", round(dev_from_requested_dx1,3)
            print "MESH2 is off of requested dx:", dx1, "by", round(dev_from_requested_dx2,3)
            potential_ijk = str(item) + "," + str(item_multiple)
            # print potential_ijk
            pre_winning_values[dev_from_requested_dx1] = potential_ijk
            # print "pre_winners:", pre_winning_values
            print "\n"
            counter = 1
            temp_list2 = []
            for i in sortedDictValues2(pre_winning_values):
                if counter > 3:
                    break
                # print "A final number is:", round(i,3)
                temp_list2.append(i)
                # print round(i,3)
                counter += 1

print "#### Finding mimimum MESH differences and sorting...\n"
print "#### Now showing up to top 3 results...\n"

for deviation in temp_list2:
    print "With a MESH difference of", round(deviation,3), "m, you can use", pre_winning_values[deviation], "as IJK values on the abutting MESH faces for MESH 1 and 2 respectively"
