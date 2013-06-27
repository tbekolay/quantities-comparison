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

This file is a modified version of the units module in the piquant package.
            http://sourceforge.net/projects/piquant/
Thanks to Dan Goodman
It contains the class definitions of Dimension, Unit, Quantity and DimensionMismatchError and these functions
    is_dimensionless(obj), get_dimensions(obj), have_same_dimensions(obj) and is_scalar_type(obj)

          
To use this class, define new quantities in terms of existing units
>>> V = 3 * volt
>>> I = 2 * amp
1.5 ohm

Use the in_unit method to display quantities in other units (this is only useful when we also use derived_units)
>>> R = 2*ohm
>>> (I*R).in_unit(volt)
'6.0 V'

    The following fundamental units are defined:
    metre, kilogram, second, amp, kelvin, mole, candela.
    And these additional basic units:
    radian, steradian, hertz, newton, pascal, joule, watt,
    coulomb, volt, farad, ohm, siemens, weber, tesla, henry,
    celsius, lumen, lux, becquerel, gray, sievert, katal,
    gram, gramme.
    Derived units, such as mile, foot etc. can be found in derived_units
    
To view a Quantity in other units use
quantity.in_unit(other_units)  other_units should be a Unit, using Quantities may give undesired results.
or
quantity % (other_units)

'''

_ilabel = ["m","kg","s","A","K","mol","cd"]

__origall__ = ['Dimension', 'DimensionMismatchError', 'Quantity', 'Unit', 'register_new_unit',
           'is_scalar_type', 'get_dimensions', 'have_same_dimensions', 'is_dimensionless']

__all__ = __origall__ + []

from operator import isNumberType, isSequenceType
from itertools import izip
from math import log as log


automatically_register_units = False

class Dimension(object):
    '''Stores the indices of the 7 basic SI unit dimension (length, mass, etc).
    
    A general user of DimPy will not need to use this class or its methods.
    ATTRIBUTES:
        Dimension._di       --- a dictionary used for input, it transforms words to a common index, i.e. length, meter, meters ---> 0.
        self._dims          --- a list that stores the exponent of each unit.
    METHODS:
        Arithmetic and representation
        self.set_dimension, self.get_dimension      --- value should be a Dimension
        self.is_dimensionless   --- returns a bool    
    
    '''
    __slots__=["_dims","_di"]
    #A dictionary to convert a unit into the corresponding index
    _di = { "Length":0, "length": 0, "metre":0, "metres":0, "metre":0, "metres":0, "metre":0, "metres":0, "metre":0, "metres":0, "m":0,\
        "Mass":1, "mass": 1, "kilogram":1, "kilograms":1, "kilogram": 1, "kilograms":1, "kg": 1,\
        "Time":2, "time": 2, "second":2, "seconds":2, "second": 2, "seconds":2, "s": 2,\
        "Electric Current":3, "Electric Current":3, "electric current": 3, "Current":3, "current":3, "ampere":3, "amperes":3, "ampere": 3,\
        "amperes":3,"A": 3,\
        "Temperature":4, "temperature": 4, "kelvin":4, "kelvins":4, "kelvin": 4, "kelvins":4, "K": 4,\
        "Quantity of Substance":5, "Quantity of substance": 5, "quantity of substance": 5, "Substance":5, "substance":5, "mole":5, "moles":5,\
        "mole": 5, "moles":5, "mol": 5,\
       "Luminosity":6, "luminosity": 6, "candela":6,"cd": 6 }
    #### INITIALISATION ####
    def __init__(self,*args,**keywords):
        """Initialise Dimension object with a vector or keywords
        
        Call as Dimension(list), Dimension(keywords) or Dimension(dim)
        
        list -- a list with the indices of the 7 elements of an SI dimension
        keywords -- a sequence of keyword=value pairs where the keywords are
          the names of the SI dimensions, or the standard unit
        dim -- a dimension object to copy
        
        Examples:
        
        The following are all definitions of the dimensions of force
        
        Dimension(length=1, mass=1, time=-2)
        Dimension(m=1, kg=1, s=-2)
        Dimension([1,1,-2,0,0,0,0])
        
        The 7 units are (in order):
        
        Length, Mass, Time, Electric Current, Temperature,
        Quantity of Substance, Luminosity
        
        and can be referred to either by these names or their SI unit names,
        e.g. length, metre, and m all refer to the same thing here.
        """
        
        if len(args):
            if isSequenceType(args[0]) and len(args[0])==7:
                # initialisation by list
                self._dims = args[0]
            elif isinstance(args[0],Dimension):
                # initialisation by another dimension object
                self._dims = args[0]._dims
        else:
            # initialisation by keywords
            self._dims = [0,0,0,0,0,0,0]
            for k in keywords.keys():
                # self._di stores the index of the dimension with name 'k'
                self._dims[Dimension._di[k]]=keywords[k]
    #### METHODS ####
    def get_dimension(self,d):
        return self._dims[Dimension._di[d]]
    def set_dimension(self,d,value):
        self._dims[Dimension._di[d]]=value
    def is_dimensionless(self):
        return sum([x==0 for x in self._dims])==7
    #### REPRESENTATION ####
    def __repr__(self):
        return self.__str__()
    def __str__(self):
        """String representation in basic SI units, or 1 for dimensionless."""
        s = ""
        for i in range(len(self._dims)):
            if self._dims[i]:
                s += _ilabel[i]
                if self._dims[i]!=1: s += "^" + str(self._dims[i])
                s += " "
        if not len(s): return "1"
        return s.strip()
    #### ARITHMETIC ####
    # Note that none of the dimension arithmetic objects do sanity checking
    # on their inputs, although most will throw an exception if you pass the
    # wrong sort of input
    def __mul__(self,value):
        return Dimension([x+y for x,y in izip(self._dims,value._dims)])
    def __div__(self,value):
        return Dimension([x-y for x,y in izip(self._dims,value._dims)])
    def __truediv__(self,value):
        return self.__div__(value)
    def __pow__(self,value):
        return Dimension([x*value for x in self._dims])
    def __imul__(self,value):
        self._dims = [x+y for x,y in izip(self._dims,value._dims)]
        return self
    def __idiv__(self,value):
        self._dims = [x-y for x,y in izip(self._dims,value._dims)]
        return self
    def __itruediv__(self,value):
        return self.__idiv__(value)
    def __ipow__(self,value):
        self._dims = [x*value for x in self._dims]
        return self
    #### COMPARISON ####
    def __eq__(self,value):
        return sum([x==y for x,y in izip(self._dims,value._dims)])==7
    def __ne__(self,value):
        return not self.__eq__(value)
    #### MAKE DIMENSION PICKABLE ####
    def __getstate__(self):
        return self._dims
    def __setstate__(self,state):
        self._dims = state

class DimensionMismatchError(Exception):
    """Exception class for attempted operations with inconsistent dimensions.
    
    For example, ``3*mvolt + 2*amp`` raises this exception. The purpose of this
    class is to help catch errors based on incorrect units. The exception will
    print a representation of the dimensions of the two inconsistent objects
    that were operated on. If you want to check for inconsistent units in your
    code, do something like::
    
        try:
            ...
            your code here
            ...
        except DimensionMismatchError, inst:
            ...
            cleanup code here, e.g.
            print "Found dimension mismatch, details:", inst
            ...
    """
    def __init__(self,description,*dims):
        """Raise as DimensionMismatchError(desc,dim1,dim2,...)
        
        desc -- a description of the type of operation being performed, e.g.
                Addition, Multiplication, etc.
        dim -- the dimensions of the objects involved in the operation, any
               number of them is possible
        """
        self._dims = dims
        self.desc = description
    def __repr__(self):
        return self.__str__()
    def __str__(self):
        s = self.desc + ", dimensions were "
        for d in self._dims:
            s += "(" + str(d) + ") "
        return s 

def is_scalar_type(obj):
    """Tells you if the object is a 1d number type.
    
    This function is mostly used internally by the module for
    argument type checking. A scalar type can be considered
    a dimensionless quantity (see the documentation for
    Quantity for more information).
    """
    return isNumberType(obj) and not isSequenceType(obj) and not isinstance(obj, Quantity)

def get_dimensions(obj):
    """Returns the dimensions of any object that has them.
    
    Slightly more general than obj.get_dimensions() because it will return
    a new dimensionless Dimension() object if the object is of number type
    but not a Quantity (e.g. a float or int).
    """
    if isNumberType(obj) and not isinstance(obj,Quantity): return Dimension()
    return obj.get_dimensions()

def have_same_dimensions(obj1,obj2):
    """Tests if two scalar values have the same dimensions, returns a ``bool``.
    
    """
    return get_dimensions(obj1)==get_dimensions(obj2)

def is_dimensionless(obj):
    if is_scalar_type(obj):
        return True
    if isinstance(obj, Quantity):            
        return obj.is_dimensionless()
    return False


class Quantity(object):
    """A number with an associated physical dimension.
    
    It is not necessary to deal with this class directly.  Instead define new
    quantities using arithmetic and existing quantities.  A DimensionMismatchError
    exception is raised if dimensions are inconsistent.
    
    Typical usage:
    >>> I = 3*amp
    >>> R = 2*ohm
    
    Use the in_unit method to display quantities in other units
    >>> (I*R).in_unit(volt)
    '6.0 V'
    
    ATTRIBUTES:
        self.dim        --- a Dimension object, the dimensions of the quantity
        self.value      --- a number, the scalar multiple
        Quantity.use_prefix --- a bool, should Quantities be displayed using SI prefixes i.e. 1.4 mega mile
        Quantity.all_unit_names     --- a list containing all of the unit names predefined in DimPy
    METHODS:
        Arithmetic, representation and comparisons
        self.get_dimensions()       --- returns the dimensions of self
        self.set_dimensions(dimension)      --- dimension should be a Dimension
        self.is_dimensionless       --- returns a bool
        self.has_same_dimensions(other)     --- returns a bool
        self.in_unit(other)     --- string representation of the object in unit other.
        self.in_best_unit(*regs)        --- uses the unit registries to find and then display self in its best unit
        Quantity.with_dimensions(value, *args, **kwargs)    --- returns a Quantity, allows defining by keywords
    """
    __slots__=["dim","value","use_prefix","all_unit_names"]    
    all_unit_names = []
    #The log (base 10) of the SI pirefixes.  if Quantity.use_prefix, the output will be of the form "###.###..... [SI prefix]"
    si_prefix_log = {-24:'yocto',-21:'zepto',-18:'atto',-15:'femto',-12:'pico',-9:'nano',-6:'micro',-3:'milli',0:'',\
    3:'kilo',6:'mega',9:'giga',12:'tera',15:'peta',18:'exa',21:'zetta',24:'yotta'}
    use_prefix = False
    #### CONSTRUCTION ####
    def __init__(self,value):
        """Initialises as dimensionless
        """
        self.value = value
        self.dim = Dimension()
    @staticmethod
    def with_dimensions(value,*args,**keywords):
        """Static method to create a Quantity object with dimensions
        
        Use as Quantity.with_dimensions(value,dim),
               Quantity.with_dimensions(value,dimlist) or
               Quantity.with_dimensions(value,keywords...)
               
        -- value is a float or other scalar type
        -- dim is a dimension object
        -- dimlist, keywords (see the Dimension constructor)
        
        e.g.        
        x = Quantity.with_dimensions(2,Dimension(length=1))
        x = Quantity.with_dimensions(2,length=1)
        x = 2 * metre        
        all define the same object.
        """
        x = Quantity(value)
        if len(args) and isinstance(args[0],Dimension):
            x.set_dimensions(args[0])
        else:
            x.set_dimensions(Dimension(*args,**keywords))
        return x
    #### METHODS ####
    def get_dimensions(self):
        """Returns the dimensions of this object
        """
        return self.dim
    def set_dimensions(self,dim):
        """Set the dimensions of this object
        """
        self.dim = dim
    def is_dimensionless(self):
        """Tells you whether this is a dimensionless object
        """
        return self.dim.is_dimensionless()
    def has_same_dimensions(self,other):
        """Tells you if this object has the same dimensions as another.
        """
        return self.dim == get_dimensions(other)
    def in_unit(self,u):
        """String representation of the object in unit u.
        """
        if not self.has_same_dimensions(u):
            raise DimensionMismatchError("Non-matching unit for method in_unit",self.dim,u.dim)
        if Quantity.use_prefix:
            val = int(log(float(self/u),10))
            val = val - (val%3)
            if val > 24:
                val = 24
            if val < -24:
                val = -24
            s = str(float(self/u)/10**val) + " " + Quantity.si_prefix_log[val]
        else:
            s = str(float(self/u))
        if not u.is_dimensionless():
            if isinstance(u,Unit):
                s += " "+str(u)
            else:
                s += " "+str(u.dim)
        return s.strip()
    
    def in_best_unit(self,*regs):
        """String representation of the object in the 'best unit'.
        
        For more information, see the documentation for the UnitRegistry
        class. Essentially, this looks at the value of the quantity for
        all 'known' matching units (e.g. mvolt, namp, etc.) and returns
        the one with the most compact representation. Standard units are
        built in, but you can register new units for consideration. 
        """
        u = _get_best_unit(self,*regs)
        return self.in_unit(u)
    #### METHODS (NUMERICAL) ####
    def sqrt(self):
        return self**0.5
    #### REPRESENTATION ####
    def __repr__(self):
        return self.__str__()
    def __str__(self):
        return self.in_best_unit()
    def __float__(self):
        return float(self.value)
    def __mod__(self, other):
        '''
        We overload the mod operator to perform unit conversions.
        '''
        return self.in_unit(other)
    
    #### ARITHMETIC ####
    # Arithmetic operations implement the following set of rules for
    # determining casting:
    # 1. Quantity op Quantity returns Quantity (and performs dimension checking if appropriate)
    # 2. Scalar op Quantity returns Quantity (and performs dimension checking assuming Scalar is dimensionless)
    # 3. other op Quantity returns NotImplemented
    # Scalar types are those for which is_scalar_type() returns True, including float, int, long, complex but not array
    def __mul__(self,other):
        # This code, like all the other arithmetic code below, implements the casting rules
        # defined above.
        if isinstance(other,Quantity):
            return Quantity.with_dimensions(float(self)*float(other),self.dim*other.dim)
        elif is_scalar_type(other):
            return Quantity.with_dimensions(float(self)*other,self.dim)
        else:
            return NotImplemented
    def __rmul__(self,other):
        return self.__mul__(other)
    def __div__(self,other):
        if isinstance(other,Quantity):
            return Quantity.with_dimensions(float(self)/float(other),self.dim/other.dim)
        elif is_scalar_type(other):
            return Quantity.with_dimensions(float(self)/other,self.dim)
        else:
            return NotImplemented
    def __truediv__(self,other):
        if isinstance(other,Quantity):
            return Quantity.with_dimensions(float(self)/float(other),self.dim/other.dim)
        elif is_scalar_type(other):
            return Quantity.with_dimensions(float(self)/other,self.dim)
        else:
            return self.value.__truediv__(other)
    def __rdiv__(self,other):
        if isinstance(other,Quantity):
            return Quantity.with_dimensions(float(other)/float(self),other.dim/self.dim)
        elif is_scalar_type(other):
            return Quantity.with_dimensions(other/float(self),[-x for x in self.dim._dims])
        else:
            return self.value.__rdiv__(other)
    def __rtruediv__(self,other):
        if isinstance(other,Quantity):
            return Quantity.with_dimensions(float(other)/float(self),other.dim/self.dim)
        elif is_scalar_type(other):
            return Quantity.with_dimensions(other/float(self),[-x for x in self.dim._dims])
        else:
            return self.value.__rtruediv__(other)
    def __add__(self,other):
        if isinstance(other,Quantity) or is_scalar_type(other):
            dim = get_dimensions(other)
            if dim==self.dim or other == 0:
                return Quantity.with_dimensions(float(self)+float(other),self.dim)
            else: raise DimensionMismatchError("Addition",self.dim,dim)
        else:
            return NotImplemented
    def __radd__(self,other):
        return self.__add__(other)
    def __sub__(self,other):
        if isinstance(other,Quantity) or is_scalar_type(other):
            dim = get_dimensions(other)
            if dim==self.dim or other == 0:
                return Quantity.with_dimensions(float(self)-float(other),self.dim)
            else: raise DimensionMismatchError("Subtraction",self.dim,dim)
        else:
            return NotImplemented
    def __rsub__(self,other):
        if isinstance(other,Quantity) or is_scalar_type(other):
            dim = get_dimensions(other)
            if dim==self.dim:
                return Quantity.with_dimensions(float(other)-float(self),self.dim)
            else: raise DimensionMismatchError("Subtraction(R)",self.dim,dim)
        else:
            return self.value.__rsub__(other)
    def __pow__(self,other):
        if isinstance(other,Quantity):
            if other.is_dimensionless():
                # WARNING: because dimension consistency is checked by exact comparison of dimensions,
                # this may lead to unexpected behaviour (e.g. (x**2)**0.5 may not have the same dimensions as x)
                return Quantity.with_dimensions(float(self)**float(other),self.dim**float(other))
            else: raise DimensionMismatchError("Power",self.dim,other.dim)
        elif is_scalar_type(other):
            return Quantity.with_dimensions(float(self)**other,self.dim**other)
        else:
            return self.value.__pow__(other)
    def __rpow__(self,other):
        if self.is_dimensionless():
            if isinstance(other,Quantity):
                return Quantity.with_dimensions(float(other)**float(self),other.dim**float(self))
            elif is_scalar_type(other):
                return Quantity(other**float(self))
            else:
                return self.value.__pow__(other)
        else:
            raise DimensionMismatchError("Power(R)",self.dim)
    def __neg__(self):
        return Quantity.with_dimensions(-float(self),self.dim)
    def __pos__(self):
        return self
    def __abs__(self):
        return Quantity.with_dimensions(abs(float(self)),self.dim)
    #### COMPARISONS ####
    def __lt__(self,other):
        if isinstance(other,Quantity):
            if self.dim==other.dim:
                return float(self)<float(other)
            else: raise DimensionMismatchError("LessThan",self.dim,other.dim)
        elif is_scalar_type(other):
            if other==0 or other==0.: return float(self)<other
            if self.is_dimensionless():
                return float(self)<other
            else: raise DimensionMismatchError("LessThan",self.dim,Dimension())
        else:
            return self.value.__lt__(other)
    def __le__(self,other):
        if isinstance(other,Quantity):
            if self.dim==other.dim:
                return float(self)<=float(other)
            else: raise DimensionMismatchError("LessThanOrEquals",self.dim,other.dim)
        elif is_scalar_type(other):
            if other==0 or other==0.: return float(self)<=other
            if self.is_dimensionless():
                return float(self)<=other
            else: raise DimensionMismatchError("LessThanOrEquals",self.dim,Dimension())
        else:
            return self.value.__le__(other)
    def __gt__(self,other):
        if isinstance(other,Quantity):
            if self.dim==other.dim:
                return float(self)>float(other)
            else: raise DimensionMismatchError("GreaterThan",self.dim,other.dim)
        elif is_scalar_type(other):
            if other==0 or other==0.: return float(self)>other
            if self.is_dimensionless():
                return float(self)>other
            else: raise DimensionMismatchError("GreaterThan",self.dim,Dimension())
        else:
            return self.value.__gt__(other)
    def __ge__(self,other):
        if isinstance(other,Quantity):
            if self.dim==other.dim:
                return float(self)>=float(other)
            else: raise DimensionMismatchError("GreaterThanOrEquals",self.dim,other.dim)
        elif is_scalar_type(other):
            if other==0 or other==0.: return float(self)>=other
            if self.is_dimensionless():
                return float(self)>=other
            else: raise DimensionMismatchError("GreaterThanOrEquals",self.dim,Dimension())
        else:
            return self.value.__ge__(other)
    def __eq__(self,other):
        if isinstance(other,Quantity):
            if self.dim==other.dim:
                return float(self)==float(other)
            else: return False
        elif is_scalar_type(other):
            if other==0 or other==0.: return float(self)==other
            if self.dim.is_dimensionless():
                return float(self)==other
            else: raise DimensionMismatchError("Equals",self.dim,Dimension())
        else:
            return self.value.__eq__(other)
    def __ne__(self,other):
        if isinstance(other,Quantity):
            if self.dim==other.dim:
                return float(self)!=float(other)
            else: raise DimensionMismatchError("Equals",self.dim,other.dim)
        elif is_scalar_type(other):
            if other==0 or other==0.: return float(self)!=other
            if self.dim.is_dimensionless():
                return float(self)!=other
            else: raise DimensionMismatchError("NotEquals",self.dim,Dimension())
        else:
            return self.value.__ne__(other)
    #### MAKE QUANTITY PICKABLE ####
    def __reduce__(self):
        return (Quantity.with_dimensions, (float(self),self.dim))

class Unit(Quantity):
    '''
    A physical unit.
    
    Normally, you do not need to worry about the implementation of
    units. They are derived from the :class:`Quantity` object with
    some additional information (name and string representation).
    You can define new units which will be used when generating
    string representations of quantities simply by doing an
    arithmetical operation with only units, for example::
    
        Nm = newton * metre
    
    Note that operations with units are slower than operations with
    :class:`Quantity` objects, so for efficiency if you do not need the
    extra information that a :class:`Unit` object carries around, write
    ``1*second`` in preference to ``second``.
    
    ATTRIBUTES:
        self.dim       --- a Dimension that stores the Units dimensions
        self.dispname       --- a dictionary that stores the unit symbols, has symbol:exponent pairs
        self.iscompound     --- a boolean, determines how the representation string looks.  Is set to True after a new unit is created from arithmetic.
    METHODS:
        Arithmetic and representation.
        Unit.create(dimension, name, display_name, scalar_multiple)     --- creates a new unit.  dimension - a dimension, name - a string, display_name
                                                                            - a string, scalar_multiple - a float
    '''
    __slots__=["dim","dispname","name","iscompound"]
    #### CONSTRUCTION ####
    def __init__(self,value):
        """Initialises a dimensionless unit
        """
        super(Unit,self).__init__(value)
        self.dim = Dimension()
        self.dispname = {}
        self.iscompound = False
    def __new__(typ, *args, **kw):
        obj = super(Unit, typ).__new__(typ,*args,**kw)
        if automatically_register_units:
            register_new_unit(obj)
        return obj
    @staticmethod
    def create(dim,name="",dname="", scalar_multiple=1.0,):
        """Creates a new named unit
        
        dim -- the dimensions of the unit
        name -- the full name of the unit, e.g. volt
        dispname -- the display name, e.g. V
        """
        #scalar_multiple used when defining miles, hours etc.
        u = Unit(scalar_multiple)
        u.dim = dim
        u.name = name + ""
        u.dispname[dname] = 1
        u.iscompound = False
        return u
    #### METHODS ####
    def set_name(self,name):
        """Sets the name for the unit
        """
        self.name = name
    def set_display_name(self,name):
        """Sets the display name for the unit
        """
        self.dispname.clear()
        self.dispname[name]=1
    #### REPRESENTATION ####
    def __repr__(self):
        return self.__str__()
    def __str__(self):
        s = ""
        if self.dispname=={}:
            for i in range(7):
                if self.dim._dims[i]:
                    s += _ilabel[i]
                    if self.dim._dims[i]!=1: s += "^" + str(self.dim._dims[i])
                    s += " "
            if not len(s): return "1"
            return s.strip()
        else:
            #converts the dictionary into a string
            for key in self.dispname.keys():
                value = self.dispname[key]
                if value != 1:
                    s += key+"^"+str(value)+" "
                else:
                    s += key+" "
            return s.strip()
    def __float__(self):
        return float(self.value)
    #### ARITHMETIC ####
    def __mul__(self,other):
        if isinstance(other,Unit):
            u = Unit(float(self)*float(other))
            u.name = self.name + other.name
            for key in self.dispname.keys():
                u.dispname[key] = self.dispname[key]
            for key in other.dispname.keys():
                if key in self.dispname.keys():
                    u.dispname[key] += other.dispname[key]
                else:
                    u.dispname[key] = other.dispname[key]
            u.dim = self.dim * other.dim
            u.iscompound = True
            return u
        else:
            return super(Unit,self).__mul__(other)
    def __rmul__(self,other):
        return self*other
    def __div__(self,other):
        if isinstance(other,Unit):
            u = Unit(float(self)/float(other))
            u.name = self.name + 'inv_' + other.name + '_endinv'
            for key in self.dispname.keys():
                u.dispname[key] = self.dispname[key]
            for key in other.dispname.keys():
                if key in self.dispname.keys():
                    u.dispname[key] -= other.dispname[key]
                else:
                    u.dispname[key] = -other.dispname[key]
            u.dim = self.dim / other.dim
            u.iscompound = True
            return u
        else:
            return super(Unit,self).__div__(other)
    def __pow__(self,other):
        if is_scalar_type(other):
            u = Unit(float(self)**other)
            u.name = self.name + 'pow_' + str(other) + '_endpow'
            for key in self.dispname.keys():
                u.dispname[key] = self.dispname[key]*other
            u.dim = self.dim ** other
            return u
        else:
            return super(Unit,self).__mul__(other)        

#### FUNDAMENTAL UNITS
metre = Unit.create(Dimension(m=1),"metre","m")
meter = Unit.create(Dimension(m=1),"meter","m")
kilogram = Unit.create(Dimension(kg=1),"kilogram","kg")
second = Unit.create(Dimension(s=1),"second","s")
amp = Unit.create(Dimension(A=1),"amp","A")
ampare = amp
kelvin = Unit.create(Dimension(K=1),"kelvin","K")
mole = Unit.create(Dimension(mol=1),"mole","mol")
candela = Unit.create(Dimension(candela=1),"candela","cd")
fundamental_units = [ metre, meter, kilogram, second, amp, kelvin, mole, candela ]

#### DERIVED UNITS, from http://physics.nist.gov/cuu/Units/units.html
derived_unit_table = \
        [\
        [ 'radian',     'rad',   Dimension() ],\
        [ 'steradian',  'sr',    Dimension() ],\
        [ 'hertz',      'Hz',    Dimension(s=-1) ],\
        [ 'newton',     'N',     Dimension(m=1,kg=1,s=-2) ],\
        [ 'pascal',     'Pa',    Dimension(m=-1, kg=1, s=-2) ],\
        [ 'joule',      'J',     Dimension(m=2,kg=1,s=-2) ],\
        [ 'watt',       'W',     Dimension(m=2,kg=1,s=-3) ],\
        [ 'coulomb',    'C',     Dimension(s=1,A=1) ],\
        [ 'volt',       'V',     Dimension(m=2, kg=1, s=-3, A=-1) ],\
        [ 'farad',      'F',     Dimension(m=-2,kg=-1,s=4,A=2) ],\
        [ 'ohm',        'ohm',   Dimension(m=2,kg=1,s=-3,A=-2) ],\
        [ 'siemens',    'S',     Dimension(m=-2,kg=-1,s=3,A=2) ],\
        [ 'weber',      'Wb',    Dimension(m=2,kg=1,s=-2,A=-1) ],\
        [ 'tesla',      'T',     Dimension(kg=1,s=-2,A=-1) ],\
        [ 'henry',      'H',     Dimension(m=2,kg=1,s=-2,A=-2) ],\
        [ 'celsius',    'degC',  Dimension(K=1) ],\
        [ 'lumen',      'lm',    Dimension(cd=1) ],\
        [ 'lux',        'lx',    Dimension(m=-2,cd=1) ],\
        [ 'becquerel',  'Bq',    Dimension(s=-1) ],\
        [ 'gray',       'Gy',    Dimension(m=2,s=-2) ],\
        [ 'sievert',    'Sv',    Dimension(m=2,s=-2) ],\
        [ 'katal',      'kat',   Dimension(s=-1,mol=1) ]\
        ]

# Generate derived unit objects and make a table of base units from these and the fundamental ones
base_units = fundamental_units
for _du in derived_unit_table:
    _u = Unit.create(_du[2],_du[0],_du[1])
    exec _du[0]+"=_u"
    base_units.append(_u)

all_units = base_units + []

class UnitRegistry(object):
    """Stores known units for printing in best units
    
    All a user needs to do is to use the register_new_unit(u)
    function.
    
    Default registries:
    
    The units module defines three registries, the standard units,
    user units, and additional units. Finding best units is done
    by first checking standard, then user, then additional. New
    user units are added by using the register_new_unit(u) function.
    
    Standard units includes all the basic non-compound unit names
    built in to the module, including volt, amp, etc. Additional
    units defines some compound units like newton metre (Nm) etc.
    
    Methods:
    
    add(u) - add a new unit
    __getitem__(x) - get the best unit for quantity x
      e.g. UnitRegistry ur; ur[3*mvolt] returns mvolt
    """
    def __init__(self):
        self.objs = []
    def add(self,u):
        """Add a unit to the registry
        """
        self.objs.append(u)
    def __getitem__(self,x):
        """Returns the best unit for quantity x
        
        The algorithm is to consider the value:
        
        m=abs(x/u)
        
        for all matching units u. If there is a unit u with a value of
        m in [1,1000) then we select that unit. Otherwise, we select
        the first matching unit.
        """
        matching = filter(lambda o: have_same_dimensions(o,x),self.objs)
        if len(matching)==0:
            raise KeyError("Unit not found in registry.")
        floatrep = filter(lambda o: 0.1<=abs(float(x/o))<100,matching)
        if len(floatrep):
            return floatrep[0]
        else:
            return matching[0]

def register_new_unit(u):
    """Register a new unit for automatic displaying of quantities
    
    Example usage:
    
    2.0*farad/metre**2 = 2.0 m^-4 kg^-1 s^4 A^2
    register_new_unit(pfarad / mmetre**2)
    2.0*farad/metre**2 = 2000000.0 pF/mm^2
    """
    user_unit_register.add(u)

standard_unit_register = UnitRegistry()
additional_unit_register = UnitRegistry()
user_unit_register = UnitRegistry()
map(standard_unit_register.add,base_units)

def all_registered_units(*regs):
    """Returns all registered units in the correct order
    """
    if not len(regs):
        regs = [ standard_unit_register, user_unit_register, additional_unit_register]
    for r in regs:
        for u in r.objs:
            yield u

def _get_best_unit(x,*regs):
    """Returns the best unit for quantity x
    
    Checks the registries regs, unless none are provided in which
    case it will check the standard, user and additional unit
    registers in turn.
    """
    if get_dimensions(x)==Dimension():
        return Quantity(1)
    if len(regs):
        for r in regs:
            try:
                return r[x]
            except KeyError:
                pass
        return Quantity.with_dimensions(1,x.dim)
    else:
        return _get_best_unit(x,standard_unit_register,user_unit_register,additional_unit_register)
    
# Add unit names to __all__
Quantity.all_unit_names = [u.name for u in all_units]
__all__.extend(Quantity.all_unit_names)

if __name__=="__main__":
    import doctest
    doctest.testmod()
