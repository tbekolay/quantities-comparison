'''
* Copyright (c) 2008, David Bate
* All rights reserved.
*
* Redistribution and use in source and binary forms, with or without
* modification, are permitted provided that the following conditions are met:
*     * Redistributions of source code must retain the above copyright
*       notice, this list of conditions and the following disclaimer.
*     * Redistributions in binary form must reproduce the above copyright
*       notice, this list of conditions and the following disclaimer in the
*       documentation and/or other materials provided with the distribution.
*     * Neither the name of the University of Cambridge nor the
*       names of its contributors may be used to endorse or promote products
*       derived from this software without specific prior written permission.
*
* THIS SOFTWARE IS PROVIDED BY DAVID BATE ''AS IS'' AND ANY
* EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE IMPLIED
* WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE ARE
* DISCLAIMED. IN NO EVENT SHALL DAVID BATE BE LIABLE FOR ANY
* DIRECT, INDIRECT, INCIDENTAL, SPECIAL, EXEMPLARY, OR CONSEQUENTIAL DAMAGES
* (INCLUDING, BUT NOT LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS OR SERVICES;
* LOSS OF USE, DATA, OR PROFITS; OR BUSINESS INTERRUPTION) HOWEVER CAUSED AND
* ON ANY THEORY OF LIABILITY, WHETHER IN CONTRACT, STRICT LIABILITY, OR TORT
* (INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY OUT OF THE USE OF THIS
* SOFTWARE, EVEN IF ADVISED OF THE POSSIBILITY OF SUCH DAMAGE.


These are new units for conversion purposes and are not added to the UnitRegistry
'''
from units import *
from math import pi

def dimensionless(value=1):
    '''Returns a dimensionless unit with scalar value.'''
    return Unit.create(Dimension(),"","",value)
    
conv_units=[\
                #[name,value,defining unit, display name], note inche is here so that when s is removed from inches, we have a coresponding unit
                  #time
                  ['minute','60.0','second','min'],\
                  ['hour','60.0','minute','hr'],\
                  ['day','24.0','hour','day'],\
                  ['week','7','day','wk'],\
                  ['fortnight','14','day','forghtnight'],\
                  ['month','30','day','month'],\
                  ['year','365.25','day','yr'],\
                  #length
                  ['mile','1609.344','meter','mi'],\
                  ['kilometer','1000','meter','km'],\
                  ['nmile','1852','meter','nmi'],\
                  ['inch','25.4*10**-3','meter','inch'],\
                  ['inche','25.4*10**-3','meter','inch'],\
                  ['foot','12','inch','ft'],\
                  ['feet','12','inch','ft'],\
                  ['yard','3','feet','yd'],\
                  ['fathom','2','yard','fathom'],\
                  ['AU','149.60*10**9','meter','AU'],\
                  ['angstrom','10**-10','meter','angstrom'],\
                  ['furlong','660','feet','furlong'],\
                  #volume                  
                  ['litre','0.001','meter**3','l'],\
                  ['gallon','4.54609','litre','gallon'],\
                  ['impGal','4.54609','litre','ImpGal'],\
                  ['usGal','3.785411784','litre','USGal'],\
                  ['impFlOz','1.0/160.0','impGal','ImpFlOz'],\
                  ['usFlOz','1.0/128.0','usGal','usFlOz'],\
                  ['barrel','117.347765','litre','barrel'],\
                  ['pint','0.56826125','litre','pint'],\
                  #mass        m_0 = solar mass, m_p = Plank mass 
                  ['kilogramme','1','kilogram','kg'],\
                  ['gram','0.001','kilogram','g'],\
                  ['gramme','0.001','kilogram','g'],\
                  ['ton','1000','kilogram','T'],\
                  ['tonne','1000','kilogram','T'],\
                  ['amu','1.66054**-27','kilogram','amu'],\
                  ['pound','0.45359237','kilogram','lb'],\
                  ['ounce','28.3495231','gram','oz'],\
                  ['m0','1.98892*10**30','kilogram','M_0'],\
                  ['mp','2.17645*10**-8','kilogram','m_p'],\
                  #extra
                  ['eV','1.60218**-19','joule','eV'],\
                  ['knot','1','nmile/hour','knot'],\
                  ['acre','4046.8564224','meter**2','acre'],\
                  ['bar','10**5','pascal','bar'],\
                  ['kWh','1000','watt*hour','kWh'],\
                  ['Wh','1','watt*hour','Wh'],\
                  ['erg','10**-7','joule','erg'],\
                  #incase the user wants other prefixes
                  ['hectare','10000','meter**2','ha'],\
                  ]

#import the units
for entry in conv_units:
    exec entry[0]+'=dimensionless('+entry[1]+')*'+entry[2]
    exec entry[0]+'.dispname.clear()'
    exec entry[0]+'.dispname[\''+entry[3]+'\']=1'
    exec entry[0]+'.name = '+'\"'+entry[0]+'\"'
    exec entry[0]+'.iscompound = False'         #after mult or div, iscompound = True, set to False so that we don't get (ft)/(min) in display
    #although we dont want these units in the registry, we would like a record of their names
    Quantity.all_unit_names.append(entry[0])

#Constants
G = 6.67300 * 10**-11 *meter**3 *kilogram**-1 *second**-2
c = 299792458 * meter/second
epsilon_0 = 8.8541878176*10**-12 *coulomb**2 *newton**-1 *meter**-2 #permitivity of free space
mu_0 = 4*pi*10**-7 *newton* amp**-2  #permeability of free space
