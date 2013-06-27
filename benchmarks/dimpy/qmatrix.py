"""
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

This module provides a class for handling matrices with associated units and functions to manipulate them.

One should view a QuantMatrix as a regular matrix where each element has a dimension calculated from the outerproduct of two vectors.  E.g.

   kg  mol 
m 1.0  2.0 
s 3.0  4.0

represents the matrix

1.0 m kg  2.0 m mol
3.0 s kg  4.0 s mol

Defines the QuantMatrix class and the following functions:
qidentity, qones, qzeros            --- return a QuantMatrix with dimensionless dimensions similar to numpy.identity, ones and zeros.
qhomogeneous(size, dimension)       --- returns a list of dimensions of size size where all entries are dimension.  Size should be an integer, dimension
                                        a Quantity, Unit or Dimension.
qmat(array)                         --- returns a QuantMatrix, will cast a child of numpy.ndarray into a QuantMatrix.
qcolumn_vector(raw_numbers, quantities)     --- returns a QuantMatrix, a quick constructor for a column vector.  raw_numbers should be a list,
                                                quantities a list of Dimension, Unit or Quantities.
shuffle(qmatrix, shuffle_dimension) --- does not return a value, modifies argument, will alter the appearance of the QuantMatrix.  shuffle_dimension
                                        should be a Dimension, Unit or Quantity.
"""
import numpy
from units import *
from derived_units import dimensionless
from numpy import bool_, character, int_, int8, int16, int32, int64, float_, float32, float64, complex_, complex64, object_
from numpy import array, matrix

class QuantMatrixError(Exception):
    pass
   
class QuantMatrix(object):
    '''
    A matrix with quantities.
    
    ATTRIBUTES:
    QuantMatrix.inner_product_placement     --- set to "top" or "left", chooses which unit vector the inner product units are placed into
    self.raw_numbers    --- takes a numpy.matrix as value, a property that gets or sets the base matrix.  Will perform type and size checking.
                            The value should be a child of numpy.ndarray.
    self.quantities     --- A property that gets and sets the quantity vectors.  Will perform type and size checking.  The value should be a list of
                            two lists, each with lengths
                            corresponding to self.shape().
    self.whitesize      --- value should be an integer. the number of spaces to be put before and after an entry in string representation
    
    
    METHODS:
    Arithmetic and representation.
    self.legal_add(B)       --- returns a bool, checks if it is legal to perform self+B as described in QuantMatrix.__add__.  B should be a QuantMatrix.
    self.legal_mul(B)       --- returns a bool, checks if it is legal to perform self*B as described in QuantMatrix._mul__.  B can be a QuantMatrix,
                                numpy.ndarray or a scalar type.
    self.inverse()          --- returns a QuantMatrix B s.t. self*B = B*self = Identity
    self.shape()            --- returns a tuple, the shape of the QuantMatrix, as numpy.ndarray.shape
    self.trace()            --- returns a Quantity, the trace of the QuantMatrix (if defined, raises QuantMatrixError if not).
    self.transpose()        --- returns a QuantMatrix, the transpose of the QuantMatrix
    self.dtype()            --- returns the type of the entries of the matrix, as numpy.ndarray.dtype
    '''
    inner_product_placement = "top" #change to "left" if user wants them to be placed in the left
    
    def __init__(self,raw_numbers,quantities, unsafe = False):
        '''
        Construct a QuantMatrix in the following way.
        
        >>> numerical_matrix = numpy.array([[1,2],[3,4]])
        >>> vertical_dimensions = [meter,second]
        >>> horizontal_dimensions = [kilogram, mole]
        >>> QuantMatrix(numerical_matrix, [vertical_dimensions, horizontal_dimensions])
           kg  mol 
        m 1.0  2.0 
        s 3.0  4.0
        
        The dimensions may be given as Dimension, Quantity or Unit types and the numerical_matrix will be configured so that we display
        in SI units (and a Dimension instance is stored).
        
        >>> non_basic_vertical = [mile, hour]
        >>> non_basic_horizontal = [yard, foot]
        >>> QuantMatrix(numerical_matrix, [non_basic_vertical, non_basic_horizontal])
                m            m      
        m 1471.5841536  981.0561024 
        s    9875.52      4389.12  
        
        The numerical_matrix and quantities may be changed using QuantMatrix_instance.raw_numbers = new_matrix, QuantMatrix_quantities = new_quantities
        and the type and size of each will be checked against the existing values.
        '''
        if not unsafe:
            self.raw_numbers = numpy.mat(raw_numbers)
            self.quantities = quantities
        else:   #This should only be used when we know the two values are legal.  It is used to speed up arithmetic as we do not need to
                #chop the matrix up.
            self.__raw_numbers = numpy.mat(raw_numbers)
            self.__quantities = quantities        
        
        self.white_size = 1 #the number of spaces to be put before and after an entry in string representation
              
    ### PROPERTIES ###
    #RAW_NUMBERS
    def _set_raw_numbers(self, numb):
        if (not isinstance(numb, numpy.ndarray)) or (len(numb.shape)>2):
                raise QuantMatrixError, "QuantMatrix.raw_numbers must be of type numpy.ndarray and have <= 2 axes."
        if not isinstance(numb, numpy.ndarray):
                raise QuantMatrixError, "QuantMatrix.raw_numbers must be of type numpy.ndarray."
        if hasattr(self,'raw_numbers'):
            #we need to check the new value is valid
            #if does not have attribute 'numb', then we are initializing for the first time    
            if not numb.shape == self.raw_numbers.shape:
                raise QuantMatrixError, "Shape of given array, "+str(numb.shape)+", does not match existing shape, "+str(self.raw_numbers.shape)+"."
        self.__raw_numbers = numb 
    def _get_raw_numbers(self):
        return self.__raw_numbers      
    raw_numbers = property(_get_raw_numbers, _set_raw_numbers)
    
    #QUANTITIES
    def _set_quantities(self, quant):
        if not isinstance(quant, list):
            raise QuantMatrixError, "QuantMatrix.quantities must be a list."
        for i in range(len(quant)):
            if not isinstance(quant[i], list):
                raise QuantMatrixError, "QuantMatrix.quantities must be a list of lists"
        for i in range(len(quant)):
            if not len(quant[i]) == self.raw_numbers.shape[i]:
                raise QuantMatrixError, "The data and unit arrays are not of the same shape."                
        
        #Modify raw_numbers so that the stored quantities are products of SI units and we store just the dimension.
        for axis in range(len(quant)):
            quant_vector = quant[axis]
            pieces_of_self = [] #this will store the arrays obtained from each self.take([i],axis=axis)
            for index in range(len(quant_vector)):
                quantity = quant_vector[index]
                if isinstance(quantity, Dimension):
                    pieces_of_self.append(self.raw_numbers.take([index], axis=axis))
                    quant_vector[index] = quantity
                else:
                    pieces_of_self.append(self.raw_numbers.take([index], axis=axis)*(1*quantity).value)
                    quant_vector[index] = (1*quantity).dim
            self.raw_numbers = numpy.concatenate(tuple(pieces_of_self), axis=axis)
            quant[axis] = quant_vector
            
        self.__quantities = quant
        
    def _get_quantities(self):
        return self.__quantities
    quantities = property(_get_quantities, _set_quantities)
    
    ### ARITHMETIC ###
    def __add__(self, other):
        '''
        Returns (if legal) the sum A+B with the dimensions of A.  Raises QuantMatrixError if ilegal.
        
        We first check if the sum is legal, this has three requirements.
        Suppose we are computing A+B, let AL and AT be the left and top dimensions of A, sim for B.
        #1: The pointwise division AL/BL must give a list of dimensions which are all the same (i.e. AL/BL is homogeneous).
        #2: #1 for AT, BT.
        #3: If alpha and beta are these two dimensions, alpha*beta must be dimensionless.
        '''
        if not self.legal_add(B):
            raise QuantMatrixError, "Cannot add these matrices."        
        return QuantMatrix(self.raw_numbers + other.raw_numbers, self.quantities, True)
    
    def legal_add(self,B):
        '''
        Returns a boolean, whether it is legal to add B to A, as described in the __add__ method.
        '''
        if not isinstance(B, QuantMatrix):
            return False
        if not A.shape() == B.shape():
            return False
        
        # Number 1
        for i in range(len(self.quantities[0])):
            if i == 0:
                first_division = self.quantities[0][i]/other.quantities[0][i]
            else:
                if not self.quantities[0][i]/other.quantities[0][i] == first_division:
                    return False
        
        # Number 2
        for i in range(len(self.quantities[1])):
            if i == 0:
                second_division = self.quantities[1][i]/other.quantities[1][i]
            else:
                if not self.quantities[1][i]/other.quantities[1][i] == second_division:
                    return False
                
        # Number 3
        if first_division * second_division == Dimension():
            return True
        else:
            return False
        
    def __sub__(self, other):
        return self + other.__neg__()
        
    def __mul__(self, other):
        '''
        Returns (if legal) A*B.  Raises QuantMatrixError if ilegal.
        If other passes is_scalar_type then we return the product, else we
        check if the product is legal, this has two requirements.
        #1 We need self.shape()[1] == other.shape()[0]
        #2 we require the inner product of AT and BL to be well defined
        (i.e. the sum is allowed, which occours if each term has the same dimension).
        
        The inner product of AT and BL is put into the top vector of the resultant.
        '''
        if isinstance(other, numpy.ndarray):
            other = qmat(other) 
        if not self.legal_mul(other):
            return NotImplemented        
          
        if isinstance(other, Quantity):
            new = []
            for entry in self.quantities[1]:
                new.append(entry*other.dim)
            return QuantMatrix(self.raw_numbers*other.value, [self.quantities[0], new])
        
        if is_scalar_type(other):
            return QuantMatrix(self.raw_numbers*other, self.quantities)  
        
        quantities = [self.quantities[0]+[], other.quantities[1]+[]]
        
        inner_product = self.quantities[1][0]*other.quantities[0][0]
        if QuantMatrix.inner_product_placement == "top":
            temp = []
            for unit in quantities[1]:
                temp.append(unit * inner_product)
            quantities[1] = temp
        elif QuantMatrix.inner_product_placement == "left":
            temp = []
            for unit in quantities[0]:
                temp.append(unit * inner_product)
            quantities[0] = temp
        else:
            raise QuantMatrixError, QuantMatrix.inner_product_placement+" is not 'top' or 'left'."
        return QuantMatrix(self.raw_numbers*other.raw_numbers, quantities, True)
    
    def __rmul__(self,other):
        '''
        Although multiplication isn't commutative, we only get to this method if other is not of type QuantMatrix, so this is OK.
        '''
        return self.__mul__(other)                    
        
    def legal_mul(self, other):
        '''
        Returns a boolean, whether it is legal to multiply B to A, as described in the __mul__ method.
        '''
        if is_scalar_type(other) or isinstance(other,Quantity):
            return True
        if isinstance(other, numpy.ndarray):
            other = qmat(other) 
        #1
        if not self.shape()[1] == other.shape()[0]:
            return False
        #2
        product = [self.quantities[1][i]*other.quantities[0][i] for i in range(len(self.quantities[1]))]
        first_dimension = product[0]
        for i in product:
            if not i == first_dimension:
                return False
        return True  
    
    def __pow__(self, other):
        if not self.legal_mul(self):
            raise QuantMatrixError, "Cannot take powers of this matrix."
        if not isinstance(other, int):
            raise QuantMatrixError, "The exponent must be an integer."
        if other == 0:
            return qidentity(self.shape()[0])
        if other < 0:
            return self.inverse().__pow__(-other)
            
        inner_product = self.quantities[1][0]*self.quantities[0][0]
        quantities = [self.quantities[0]+[], self.quantities[1]+[]]
        if QuantMatrix.inner_product_placement == "top":
            temp = []
            for unit in quantities[1]:
                temp.append(unit * inner_product**(other-1))
            quantities[1] = temp
        elif QuantMatrix.inner_product_placement == "left":
            temp = []
            for unit in quantities[0]:
                temp.append(unit * inner_product**(other-1))
            quantities[0] = temp
        else:
            raise QuantMatrixError, QuantMatrix.inner_product_placement+" is not 'top' or 'left'."
        return QuantMatrix(self.raw_numbers**other, quantities, True)
    
    def inverse(self):
        quantities = [[],[]]
        for entry in self.quantities[0]:
            quantities[1].append(Dimension()/entry)
        for entry in self.quantities[1]:
            quantities[0].append(Dimension()/entry)
        return QuantMatrix(self.raw_numbers**-1, quantities)
           
    def __pos__(self):
        return self
    def __neg__(self):
        return QuantMatrix(-self.raw_numbers, self.quantities, True)
            
    ### REPRESENTATION ###
        
    def __str__(self):
        widths = []         #this will store the width of each collumn in the matrix
        left_unit_lengths = [len(str(unit)) for unit in self.quantities[0]]
        left_width = max(left_unit_lengths)
        for column_number in range(self.shape()[1]):
            column_widths = [len(str(self.raw_numbers[row, column_number])) for row in range(self.shape()[0])]
            column_widths.append(len(str(self.quantities[1][column_number])))
            widths.append(max(column_widths) + 2*self.white_size)
            
        output = ""
        #add the top dimensions
        #skip the space for the left dimensions
        output += white_space(left_width)
        for column_number in range(self.shape()[1]):
            number_of_spaces = widths[column_number] - len(str(self.quantities[1][column_number]))
            if number_of_spaces % 2 == 0:
                output += white_space(number_of_spaces / 2)
            else:
                output += white_space(number_of_spaces / 2 +1)
            output += str(self.quantities[1][column_number])
            output += white_space(number_of_spaces / 2)
        output += "\n"
        
        #add the rest of the matrix
        for row_number in range(self.shape()[0]):
            #print the left dimension
            number_of_spaces = left_width - len(str(self.quantities[0][row_number]))
            if number_of_spaces % 2 == 0:
                output += white_space(number_of_spaces / 2)
            else:
                output += white_space(number_of_spaces / 2 +1)
            output += str(self.quantities[0][row_number])
            output += white_space(number_of_spaces / 2)
            
            for column_number in range(self.shape()[1]):
                number_of_spaces = widths[column_number] - len(str(self.raw_numbers[row_number, column_number]))
                if number_of_spaces % 2 == 0:
                    output += white_space(number_of_spaces / 2)
                else:
                    output += white_space(number_of_spaces / 2 +1)
                output += str(self.raw_numbers[row_number, column_number])
                output += white_space(number_of_spaces / 2)
            output += "\n"
        output = output[:-2] #to remove the last new line
        return output
       
    def __repr__(self):
        return self.__str__()
          
    ### MATRIX METHODS ###    
    def shape(self):
        return self.raw_numbers.shape
    
    def trace(self):
        #check the trace is valid
        total = 0
        minimum = min(self.shape())
        coordinate = []
        for i in range(minimum):
            temp = []
            for j in range(len(self.shape())):
                temp.append(i)
            temp = tuple(temp)
            try:
                total += self.__getitem__(temp)
            except DimensionMismatchError:
                raise QuantMatrixError, "Trace: The inner product of the quantity vectors is not of a single unit"
        return total
    
    def transpose(self):
        return QuantMatrix(self.raw_numbers.transpose(), [self.quantities[1], self.quantities[0]], True) 
    
    ### READING ###
    def __getitem__(self, key):
        if isinstance(key, slice):
            return self
        if isinstance(key, int):
            return QuantMatrix(self.raw_numbers[key], [[self.quantities[0][key]], self.quantities[1]])
        if isinstance(key, tuple):
            first_dim = self.quantities[0][key[0]]
            second_dim = self.quantities[1][key[1]]
            if not isinstance(first_dim, list):
                first_dim = [first_dim]
            if not isinstance(second_dim, list):
                second_dim = [second_dim]
            temp_matrix = QuantMatrix(self.raw_numbers[key], [first_dim, second_dim])
            if temp_matrix.shape() == (1,1):
                return temp_matrix.raw_numbers[0,0]*Unit.create(temp_matrix.quantities[0][0])*Unit.create(temp_matrix.quantities[1][0])
            return temp_matrix
        raise IndexError, "Enter an integer or a tuple."
        
    ### OTHERS ###
    def dtype(self):
        return self.raw_numbers.dtype
        
def qidentity(size, **kwargs):
    '''
    Creates the identitiy matrix of size size.
    
    >>> qidentity(3)
       1    1    1  
    1 1.0  0.0  0.0 
    1 0.0  1.0  0.0 
    1 0.0  0.0  1.0
    '''
    if kwargs.has_key('dtype'):
        return QuantMatrix(numpy.identity(size, dtype=kwargs['dtype']), [qhomogeneous(size, dimensionless().dim), qhomogeneous(size, dimensionless().dim)], True) 
    return QuantMatrix(numpy.identity(size), [qhomogeneous(size, dimensionless().dim), qhomogeneous(size, dimensionless().dim)], True)

def qones(size, **kwargs):
    '''
    Produces a qmatrix of zeroes, similar to numpy.zeros.  Accepts dtype argument.
    
    >>> qones((2,3))
       1    1    1  
    1 1.0  1.0  1.0 
    1 1.0  1.0  1.0

    >>> qones(2)
       1    1  
    1 1.0  1.0

    >>> qones((2,3), dtype=int16)
      1  1  1 
    1 1  1  1 
    1 1  1  1
    '''
    if (not isinstance(size,tuple)):
        size = (1,size)
    if len(size)>2:
        raise QuantMatrixError, "Enter a tuple of size <= 2."
    if kwargs.has_key('dtype'):
        return QuantMatrix(numpy.ones(size, dtype=kwargs['dtype']), [qhomogeneous(size[0], dimensionless().dim), qhomogeneous(size[1],dimensionless().dim)], True)
    return QuantMatrix(numpy.ones(size), [qhomogeneous(size[0], dimensionless().dim), qhomogeneous(size[1],dimensionless().dim)], True)

def qzeros(size, **kwargs):
    '''
    Produces a qmatrix of zeroes, similar to numpy.zeros.  Accepts dtype argument.
    
    >>> qzeros((2,3))
       1    1    1  
    1 0.0  0.0  0.0 
    1 0.0  0.0  0.0

    >>> qzeros(2)
       1    1  
    1 0.0  0.0

    >>> qzeros((2,3), dtype=int16)
      1  1  1 
    1 0  0  0 
    1 0  0  0
    '''
    if (not isinstance(size,tuple)):
        size = (1,size)
    if len(size)>2:
        raise QuantMatrixError, "Enter a tuple of size <= 2."
    if kwargs.has_key('dtype'):
        return QuantMatrix(numpy.zeros(size, dtype=kwargs['dtype']), [qhomogeneous(size[0], dimensionless().dim), qhomogeneous(size[1],dimensionless().dim)], True)
    return QuantMatrix(numpy.zeros(size), [qhomogeneous(size[0], dimensionless().dim), qhomogeneous(size[1],dimensionless().dim)], True)

def qhomogeneous(size, dimension):
    '''
    Produces a list of dimensions of size size where all entries are dimension.
    
    Will accept a dimension, quantitiy or unit as input.
    
    >>> qhomogeneous(4,meter)
    [m, m, m, m]
    >>> qhomogeneous(4,Dimension(m=1,s=2))
    [m s^2, m s^2, m s^2, m s^2]

    '''
    if not isinstance(dimension, Dimension):
        try:
            dimension = dimension.dim
        except AttributeError:
            print "Require a dimensional quantity to create the vector, got '"+type(shuffle_dimension).__name__ + "'."
    if isinstance(dimension, Dimension):
        output = []
        for i in range(size):
            output.append(dimension)
        return output

def qmat(array):
    '''
    Casts array into a QuantMatrix.
    
    >>> a = array([[1,2],[3,4]])
    >>> qmat(a)
      1  1 
    1 1  2 
    1 3  4
    '''
    if (not isinstance(array, numpy.ndarray)) or (not len(array.shape)==2):
        raise QuantMatrixError, "qmat takes a two dimensional ndarray as its argument."
    return QuantMatrix(array, [qhomogeneous(array.shape[0], dimensionless().dim), qhomogeneous(array.shape[1], dimensionless().dim)], True)

def qcolumn_vector(raw_numbers, quantities):
    '''
    A quick constructor for a column vector.
    
    >>> qcolumn_vector((1,2,3),(meter,second,mole))
         1  
     m  1.0 
     s  2.0 
    mol 3.0
    '''
    matrix = []
    for element in raw_numbers:
        matrix.append([element])
    return QuantMatrix(numpy.array(matrix), [list(quantities),[dimensionless()]])

def shuffle(qmatrix, shuffle_dimension):
    '''
    Multiplies the top dimensions by the shuffle_dimension and divides the left dimensions by shuffle_dimension, this process does not
    alter the quant matrix but may be used to create a better representation of the QuantMatrix.
    
    Will take any dimensional quantity as the second argument.
    
    >>> a = qidentity(3)
    >>> shuffle(a, meter)
    >>> a
          m    m    m  
    m^-1 1.0  0.0  0.0 
    m^-1 0.0  1.0  0.0 
    m^-1 0.0  0.0  1.0
    '''
    if not isinstance(shuffle_dimension, Dimension):
        try:
            shuffle_dimension = shuffle_dimension.dim
        except AttributeError:
            print "Require a dimensional quantity to shuffle, got '"+type(shuffle_dimension).__name__ + "'."
    if isinstance(shuffle_dimension, Dimension):
        qmatrix.quantities = [[a/shuffle_dimension for a in qmatrix.quantities[0]],[a*shuffle_dimension for a in qmatrix.quantities[1]]]
    
def white_space(number):
    '''
    Prints "number" space characters.
    '''
    i = 0
    output = ""
    while i<int(number):
        output += " "
        i += 1
    return output

if __name__ == "__main__":
    import doctest
    from derived_units import *
    doctest.testmod()
