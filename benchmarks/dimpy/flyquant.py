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

Defines types Flydim and Flyquant.  Flydim stores the information regarding dimensions constructed on-the-fly.
Flyquant stores an object with both Flydims and regular quantities.  The scalar value is stored in quant.value

Defines the functions:
get_dimensions(obj)     --- returns a tuple containing the proper and fly parts of obj (works for Flyquants, Quantities and Units)
is_dimensionless(obj)   --- returns a bool
def fly(obj)            --- casts a Quantity or Unit into a Flyquant
'''
from units import *

def flt(obj):
    if isinstance(obj,Flyquant):
        return obj.quant.value
    elif isinstance(obj,Quantity) and not isinstance(obj,Unit):
        return obj.value
    else:
        return float(obj)

class Flydim(object):
    '''
    Will a unit with virtual dimensions that are created on-the-fly.
    
    ATTRIBUTES:
    self.dim    --- a dictionary in unit_name:power pairs
    METHODS:
    standard arithmetic and printing
    self.invert()   --- returns a new Flydim with all powers inverted
    self.copy()     --- returns a copy
    self.is_dimensionless()     --- returns a bool
    self.get_dimensions()       --- if self.is_dimensionless, returns self.dim, else returns 1
        
    
    ----------------Flydims-----------------------
    Define the initial Flydim by a string, for example a has dimension "house = 1"
    >>> a = Flydim('house')
    >>> b = Flydim('flat')
    
    Multiplication combines the dimensions
    >>> a*b
    house flat
    
    Can define an empty Flydim for later use
    >>> c = Flydim()
    
    Can then modify the contents directly
    >>> c.dim['garage']=2
    >>> print c
    garage^2
    
    Can copy Flydims
    >>> c = a.copy()
    >>> print c
    house
    
    ARITHMETIC:
    >>> a.invert()
    house^-1
    
    >>> a/b
    house flat^-1
    >>> a/meter
    1.0 m^-1 house
    >>> a/2
    0.5 house
    >>> 2/a
    2.0 house^-1
    '''
    __slots__=["dim"]  #dim, a dictionary of the form {flyUnitName:exponent}
    
    def __init__(self,name=""):
        #create a new Flydim, with one unit of power 1
        self.dim = {}
        if name:
            self.dim[name]=1
    ### ARITHMETIC ###  
    def __mul__(self,other):
        if type(other)==type(self):
            #do dictionary stuff
            s = self.copy()
            for k,v in other.dim.items():
                if not s.dim.has_key(k):
                    s.dim[k]=0
                s.dim[k]+= v
                if not s.dim[k]:
                    del s.dim[k]
            return s
        elif isinstance(other,Quantity):
            return Flyquant(self,other)
        elif isinstance(other,Flyquant):
            return NotImplemented
        elif is_scalar_type(other) or isinstance(other, Quantity):
            return Flyquant(self, Quantity(other))
        else:
            return NotImplemented
    def __rmul__(self,other):
        return self.__mul__(other)
    def __div__(self,other):
        if isinstance(other,Flydim):
            return self*other.invert()
        elif isinstance(other,Flyquant):
            return NotImplemented
        elif is_scalar_type(other) or isinstance(other, Quantity):
            return self*(1.0/other)
        else:
            return NotImplemented
    def __rdiv__(self,other):
        return other*self.invert()
    def __pow__(self,other):
        if isinstance(other,Flyquant) or isinstance(other,Quantity):
            if other.is_dimensionless():
                s = self.copy()
                for k in s.dim.keys():
                    s[k]=s[k]**float(other)
                return s
            else:
                raise DimensionMismatchError("Power",self.dim,other.dim)
        elif is_scalar_type(other):
            s = self.copy()
            for k in s.dim.keys():
                s.dim[k] = s.dim[k]*other
            return s        
        else:
            return NotImplemented
    def invert(self):
        s = self.copy()
        for k,v in s.dim.items():
            s.dim[k]*=-1
        return s
    ### REPRESENTATION ###
    def __str__(self):
        strg = ""
        for key in self.dim.keys():
            strg += key
            if self.dim[key]!=1:
                strg += "^"+str(self.dim[key])
            strg+=" "
        strg = strg.strip()
        return strg
    def __repr__(self):
        return self.__str__()
    ### OTHERS ###
    def copy(self):
        cpy = Flydim()
        cpy.dim = self.dim.copy()
        return cpy
    def is_dimensionless(self):
        return not len(self.dim)
    def get_dimensions(self):
        if self.is_dimensionless():
            return 1
        else:
            return self.dim
   
class Flyquant(object):
    """    
    A Flyquant is usualy defined from multiplication of quants and Flydims or numbers and Flydims,  refer to the "proper part" and "fly part".
    
    ATTRIBUTES:
    self.quant  --- a Quantity, store the quant part
    self.fly    --- a Flydim, store the fly part 
    METHODS:
    Standard arithmetic and representation.
    self.copy()     --- returns a copy
    self.is_dimensionless()     --- returns a bool
    self.is_proper_unit()       --- returns a bool, True if self.fly is dimensionless
    self.get_dimensions()       --- returns a tuple (self.quant, self.fly)
    self.to_quant()             --- if self.is_proper_unit(), returns a copy of self of type Quantity
    self.in_unit(target_units)  --- returns a string containing the value of self in target_units, target_units should be a product of Units and Flydims
                                    i.e. meter*Flydim('house'), using Quantities may produce undesired results.
        
    ---------------Flyquants------------------            
    >>> a = Flydim('house')
    >>> A = 3*a; A
    3.0 house
    >>> B = a*3; B
    3.0 house
    >>> type(B)
    <class '__main__.Flyquant'>
    
    can also multiply Flyquants and Flydims to get Flyquants
    >>> A*a
    3.0 house^2
    >>> a*A
    3.0 house^2
    
    >>> A/B
    1.0
    >>> A/a
    3.0
    >>> a/A
    0.333333333333
    >>> A/2
    1.5 house
    >>> 2/A
    0.666666666667 house^-1
    
    >>(A*(1*meter))^2
    o
    
    arithmetic will return the simplest type of object
    >>> A = 2*meter*a
    >>> B = Flyquant(Flydim(""),1*meter)
    >>> C = Flyquant(Flydim(""),Quantity(4))
    >>> A*(2*meter)
    4.0 m^2 house
    >>> (2*meter)*A
    4.0 m^2 house
    >>> A+A
    4.0 m house
    >>> B+2*meter
    3.0 m
    >>> 2*meter+B    
    3.0 m
    >>> type(_)
    <class 'units.Quantity'>
    >>> C + 8
    12.0
    >>> 8 + C
    12.0
    >>> type(_)
    <type 'float'>
    
    conversion    
    >>> from derived_units import *
    >>> a = meter*Flydim('house')
    >>> b = mile*Flydim('house')
    >>> b.in_unit(a)
    '1609.344 m house'
    >>> a.in_unit(b)
    '0.000621371192237 mi house'
    """
    __slots__=["quant","fly","dim"]
    
    def __init__(self, fly, quant=Quantity(1)):
        self.quant = quant
        self.fly = fly
    ### ARITHMETIC ###
    def __mul__(self,other):
        if type(other)==type(self):
            return Flyquant(self.fly*other.fly,self.quant*other.quant)
        elif isinstance(other,Flydim):
            return Flyquant(self.fly*other,self.quant)
        elif isinstance(other,Quantity):
            return Flyquant(self.fly,self.quant*other)
        elif is_scalar_type(other):
            return Flyquant(self.fly, self.quant*float(other))
        else:
            return NotImplemented
    def __rmul__(self,other):
        return self.__mul__(other)
    def __div__(self,other):
        if isinstance(other,Flydim) or isinstance(other,Flyquant):
            return self*other.invert()
        elif is_scalar_type(other) or isinstance(other, Quantity):
            return self*(1.0/other)
        else:
            return NotImplemented
    def __rdiv__(self,other):
        return other*self.invert()
    def __pow__(self,other):
        if is_scalar_type(other) or isinstance(other,Flyquant) or isinstance(other, Quantity):
            if get_dimensions(other)==get_dimensions(Dimension(),Flydim().get_dimensions()):
                return Flyquant(self.fly**flt(other),self.quant**flt(other))
            else:
                raise DimensionMismatchError("Power",get_dimensions(self),get_dimensions(other))       
        else:
            return NotImplemented
    def __add__(self,other):
        if isinstance(other,Flyquant) or isinstance(other,Quantity) or is_scalar_type(other):
            if get_dimensions(other) == get_dimensions(self):
                a = self*(flt(self)+flt(other))/flt(self)
                #return the an object of the simplest form i.e. return a Quantity if we have no on-the-fly dimensions
                if get_dimensions(a)[1] == Flydim().get_dimensions():
                    #then we have a proper dimension
                    if get_dimensions(a)[0] == Dimension():
                        #then we have a float
                        return a.quant.value
                    else:        
                        return a.quant
                else:
                    #then we have a Flyquant
                    return a
            else: raise DimensionMismatchError("Addition",get_dimensions(self),get_dimensions(other))
        else:
            return NotImplemented
    def __radd__(self,other):
        return self.__add__(other)
    def __sub__(self,other):
        return self + other.__neg__()
    def __rsub__(self,other):
        return other + self.__neg__()
    def __pos__(self):
        return self
    def __neg__(self):
        a = self.copy()
        a.quant.value = -a.quant.value
        return a
    def __abs__(self):
        a = self.copy()
        a.quant.value = abs(a.quant.value)
        return a
    def invert(self):
        return Flyquant(self.fly.invert(),1/self.quant)
    ### REPRESENTATION ###
    def __str__(self):
        strg = str(self.quant)+" "
        strg += str(self.fly)
        return strg.strip()
    def __repr__(self):
        return self.__str__()    
    def value(self):
        return float(self.quant)
    ### OTHERS ###
    def copy(self):
        return Flyquant(self.fly,self.quant)
    def is_dimensionless(self):
        return self.quant.is_dimensionless() and self.fly.is_dimensionless()
    def is_proper_unit(self):
        #i.e. does not have any on-the-fly units
        return self.fly.is_dimensionless()
    def get_dimensions(self):
        #returns a tuple (proper dim,fly dim)
        return (self.quant.get_dimensions(),self.fly.get_dimensions())
    def to_quant(self):
        #returns a Quantity representing self if self is a proper unit
        if self.is_proper_unit():
            return self.quant
        else:
            raise ValueError("Argument of to_quant is not a proper unit")
    def in_unit(self,other):
        if isinstance(other.quant,Unit):
            return str((1.0*self)/other)+" "+str(other.quant)+" "+str(other.fly)    #the 1.0*self is to ensure self.quant is a quantity, not a unit
        else:
            return str(self/other)+" "+str(other.quant.dim)+" "+str(other.fly)
    
def get_dimensions(obj):
    '''As for quantities, this is slightly more general than obj.get_dimensions, as it will return a tuple, filled with dimensionless dimensions where
    the types are not quite right, such as for floats or Quantities
    '''
    if isinstance(obj,Flyquant):
        return obj.get_dimensions()
    elif isinstance(obj,Quantity):
        return (obj.get_dimensions(),Flydim().get_dimensions())
    elif is_scalar_type(obj):
        return (Dimension(),Flydim().get_dimensions())
    
def is_dimensionless(obj):
    return get_dimensions(obj) == (Dimension(),Flydim().get_dimensions())

def fly(obj):
    '''obj a Quantity or anything that passes is_scalar_type, returns a Flyquant representing the same quantity
    '''
    if isinstance(obj,Flyquant):
        return obj
    elif isinstance(obj,Quantity):
        return Flyquant(Flydim(),obj)
    elif is_scalar_type(obj):
        return Flyquant(Flydim(),Quantity(float(obj)))

if __name__ == "__main__":
    import doctest
    doctest.testmod()
