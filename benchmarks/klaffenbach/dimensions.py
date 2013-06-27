'''A module for adding dimensions to numeric types for dimensional analysis
and automatic unit conversions.  '''

from __future__ import division
import math
import re
import os


t___add__     = r'(?P<__add__>\+)'
t___sub__     = r'(?P<__sub__>\-)'
t___pow__     = r'(?P<__pow__>\^|(\*\*))'
t___mul__     = r'(?P<__mul__>\*)'
t___truediv__ = r'(?P<__truediv__>/)'
t_LPAREN      = r'(?P<LPAREN>\()'
t_NUMBER      = r'(?P<NUMBER>(\+|-)?((\d+\.\d+)|(\.\d+)|(\d+\.)|(\d+))([eE](\+|-)?\d+)?)'
t_RPAREN      = r'(?P<RPAREN>\))'
t_IDENT       = r'(?P<IDENT>[a-zA-Z]\w*)' # ident names begin with letter
ulexres= r'\s*(' + "|".join([t___add__, t_IDENT, t___pow__, t___truediv__,
               t___sub__, t___mul__, t_NUMBER, t_LPAREN, t_RPAREN]) + r')\s*'
lexre = re.compile(ulexres)

def tokenize(s):
    '''return a list of token tuples: (token, value, start)'''
    l=[]                                  # list to hold tokens
    start=0                               # used to check for bad tokens
    sc=lexre.scanner(s)
    while 1:
        tg=sc.search()
        if tg:
            if tg.start()!=start:       # we should start at end of last token
                raise BadToken(start)
            l.append( [ (token, value, (tg.start(), tg.end()))
                     for (token, value) in tg.groupdict().items() if value][0])
            start=tg.end()                    # prepare start for next pass
        else:
            if start!=len(s):
                raise BadToken(start)
            break
    return l

class UnmatchedParenthesis(Exception):
    pass

class BadToken(Exception):
    def __init__(self,value):
        self.value=value
    def __str__(self):
        return repr(self.value)

PRIORITY={  '__add__':1,  '__sub__':1,
            '__mul__':2,  '__truediv__':2,
            '__pow__':3}

def convert(s):
    '''convert a list of token tuples from infix order to RPN'''
    input=s[:]
    stack=[]                            # 'Texas' LIFO
    output=[]                            # 'California' output accumulator
    while len(input)>0: # Careful!  We're iterating over changing input list.
        if input[0][0]=='IDENT' or input[0][0]=='NUMBER':
            # move operands directly to output
            output.append(input.pop(0))
        elif input[0][0]=='LPAREN':
            # Now handle a left parenthesis
            stack.append(input.pop(0))
        elif input[0][0]=='RPAREN':
            # Now handle a right parenthesis
            if not stack:
                # We shouldn't have an RPAREN without an LPAREN
                raise UnmatchedParenthesis
            elif stack[-1][0]=='LPAREN':
                # when RPAREN catches up with LPAREN, vaporize both
                stack.pop()
                input.pop(0)
            else:
                # pop operands until we hit LPAREN
                output.append(stack.pop())
        else:
            # logically, we should have an operand at the input, but
            # don't know about stack
            if stack:
                # there is at least one item in the stack
                if stack[-1][0]=='LPAREN':
                    # LPAREN on stack, push next operand to stack
                    stack.append(input.pop(0))
                elif PRIORITY[input[0][0]]>PRIORITY[stack[-1][0]]:
                    # higher priority input item goes to stack
                    stack.append(input.pop(0))
                else:
                    output.append(stack.pop())
            else:
                # no stack, push input to stack
                stack.append(input.pop(0))
    while len(stack)>0:
        # when input is empty we still may have stack items to move over
        if stack[-1][0]=='LPAREN':
            # Shouldn't be any LPARENs left!
            raise UnmatchedParenthesis
        else:
            output.append(stack.pop())
    return output

def proc_stack(input, vardict):
    '''process IDENTs, binary operators in input list using vardict namespace'''
    stack=[]
    for item in input:
        # anything left to process?
        if item[0]=='IDENT':
            # push object referred to by IDENT onto stack
            stack.append(vardict[item[1]])
        elif item[0]=='NUMBER':
            stack.append(float(item[1]))
        else:
            # we must have a binary operator
            # and assuming well formed input two operands on stack
            operand=item[0]
            y=stack.pop()
            x=stack.pop()
            # XXX the following hack should be fixed some time just
            # because it is really ugly!
            if operand=='__truediv__' and type(y)!=type(1.0) and \
                    type(x)==type(1.0) and x==1 :
                # special case of empty numerator and Q denom
                x=vardict['']
                # this is coordinated with hack in UNITS_LIST in dimensions.py
            stack.append(x.__getattribute__(operand)(y))
    return stack[0]

def ap_eval(instr,vardict):
    '''evaluate an expression string using vardict namespace'''
    t=tokenize(instr)
    s=convert(t)
    ans=proc_stack(s,vardict)
    return ans

class DimensionsError(Exception):
    def __init__(self, value):
        self.value=value
    def __str__(self):
        return repr(self.value)

class Q(object):
    EXPTOL=1e-14
    '''simple class for creating base dimensions'''
    def __init__(self, value, dimstr, utype=None):
        '''takes name of base unit and creates a Base object'''
        if utype=='BASE':   # manually create the dimension for a base unit
            self.value=value            # value of dimension
            self.dims={}    # dict of dimensions, keys are base units
            self.dims[dimstr]=1
        else:               # we're building a compound unit
            if dimstr.strip()=='':  # no Dim object yet, so build it
                self.value=value
                self.dims={}
            else:
                tmp=ap_eval(dimstr,units)
                # At this point we have a Dim object
                self.value=value*tmp.value
                self.dims=tmp.dims
    def copy(self):
        '''make a copy'''
        tmp=Q(1,'')
        tmp.value=self.value
        tmp.dims=self.dims.copy()
        return tmp
    def __neg__(self):
        '''return negative of self'''
        tmp=self.copy()
        tmp.value=-self.value
        return tmp
    def __pos__(self):
        '''unary positive operator'''
        return self.copy()
    def __abs__(self):
        '''abs operator'''
        tmp=self.copy()
        tmp.value=abs(self.value)
        return tmp
    def __add__(self, other):
        '''add like units together'''
        tmp=self.copy()
        if other.dims==tmp.dims:
            tmp.value=self.value+other.value
            return tmp
        else:
            raise DimensionsError, 'Units not consistent'
    # Rich comparison operators
    def __lt__(self, other):
        '''lt method for units'''
        if self.dims!=other.dims:
            raise DimensionsError, 'Units not consistent'
        else:
            return self.value<other.value
    def __ge__(self, other):
        '''ge method for units'''
        return not self.__lt__(other)
    def __eq__(self, other):
        '''eq method for units'''
        if self.dims!=other.dims:
            raise DimensionsError, 'Units not consistent'
        else:
            return self.value==other.value
    def __ne__(self, other):
        '''ne method for units'''
        return not self.__eq__(other)
    def __gt__(self, other):
        '''gt method for units'''
        if self.dims!=other.dims:
            raise DimensionsError, 'Units not consistent'
        else:
            return self.value>other.value
    def __le__(self, other):
        '''le method for units'''
        return not self.__gt__(other)
    def __sub__(self, other):
        '''subtract like units'''
        tmp=self.copy()
        if other.dims==tmp.dims:
            tmp.value=self.value-other.value
            return tmp
        else:
            raise DimensionsError, 'Units not consistent'
    def __mul__(self, other):
        '''multiply two units together'''
        # get list of dims used in both units
        try:
            tmp=Q(1,'')
            tmp.value=self.value*other.value
            superset=dict.fromkeys(self.dims.keys()+other.dims.keys()).keys()
            for dim in superset:
                tmp.dims[dim]=self.dims.get(dim,0)+ \
                                other.dims.get(dim,0)
                if abs(tmp.dims[dim] %1)<self.EXPTOL:
                    # This is a hack to eliminate creeping floating point error.
                    # It's not a real substitute for using a Rational
                    # number type but will suffice for now.
                    tmp.dims[dim]=int(round(tmp.dims[dim]))
                if tmp.dims[dim]==0:
                    del tmp.dims[dim]
            return tmp
        except AttributeError:
            # this should happen if we multiply by a number
            tmp=self.copy()
            tmp.value=self.value*other
            return tmp
    def __rmul__(self,other):
        '''multiply number by unit'''
        return self.__mul__(other)
    def __truediv__(self, other):
        '''divide one unit by another'''
        # get list of dims used in both units
        tmp=self.copy()
        try:    # if two Dim objects
            tmp.value=tmp.value/other.value
            superset=dict.fromkeys(self.dims.keys()+other.dims.keys()).keys()
            for dim in superset:
                tmp.dims[dim]=self.dims.get(dim,0)-other.dims.get(dim,0)
                if abs(tmp.dims[dim] %1)<self.EXPTOL:
                    # this is a hack to eliminate creeping floating point error
                    tmp.dims[dim]=int(round(tmp.dims[dim]))
                if tmp.dims[dim]==0:
                    del tmp.dims[dim]
        except AttributeError:  # if dividing by number
            tmp.value/=other
        return tmp
    def __div__(self,other):
        '''calls __truediv__'''
        return self.__truediv__(other)
    def __rdiv__(self,other):
        '''calls __rtruediv__'''
        return self.__rtruediv__(other)
    def __rtruediv__(self,other):
        tmp=self.copy()
        tmp.value=1/tmp.value
        for dim in tmp.dims:
            tmp.dims[dim]=-tmp.dims[dim]
        return other*tmp
    def __pow__(self,power):
        tmp=self.copy()
        for dim in tmp.dims:
            newexponent=power*tmp.dims[dim]
            if abs(newexponent%1)<self.EXPTOL:
                # this is a hack to eliminate creeping floating point error
                newexponent=int(round(newexponent))
            tmp.dims[dim]=newexponent
        tmp.value=tmp.value**power
        return tmp
    def sqrt(self):
        '''returns square root of self'''
        # Added for compatibility with std function in scipy/numpy
        return self.__pow__(0.5)
    def __hash__(self):
        '''hash method allows use of Dims as dict key.
        Manually modifying Dim attributes will break the dict
        so don't do that!'''
        return hash(self.value)^reduce(
              lambda x,y: x^y, [hash(item) for item in self.dims.items()],0)
    def __repr__(self):
        '''return a string representation'''
        # numerator string will be either 1 or a string of the dims
        numdims=[(dim,self.dims[dim]) for dim in self.dims
                                      if self.dims[dim]>0]
        numdims.sort()
        numstrlist=[]
        for dim,power in numdims:
            if power==1:
                numstrlist.append(dim)
            else:
                numstrlist.append(''.join([dim,'**',str(power)]))
        numstr='*'.join(numstrlist)
        dendims=[(dim,-self.dims[dim]) for dim in self.dims
                                      if self.dims[dim]<0]
        denstrlist=[]
        for dim,power in dendims:
            if power==1:
                denstrlist.append(dim)
            else:
                denstrlist.append(''.join([dim,'**',str(power)]))
        denstr='*'.join(denstrlist)
        if len(denstrlist)>1:
            denstr='(%s)' % denstr
        if len(numdims)==0 and len(dendims)==0:
            dimstr=''
        elif len(numdims)==0:
            dimstr='1/'+denstr
        elif len(dendims)==0:
            dimstr=numstr
        else:
            dimstr='%s/%s' % (numstr,denstr)
        return 'Q(%s, \'%s\')' % (self.value, dimstr)
    def __call__(self,otherdim, fmt=None):
        '''return value when expressed in otherdim dimensions'''
        o=Q(1,otherdim)
        if self.dims==o.dims:
            if fmt==None:
                return self.value/o.value
            else:
                return ''.join([fmt % (self.value/o.value),' [',
                        otherdim,']'])
        else:
            raise DimensionsError, 'Units not consistent'
    def str(self,dims,valfmt='%s',dimfmt=' [%s]'):
        '''return a string in dimensions (dims) using value format specifier
(valfmt) and dims format specifier (dimfmt)'''
        return ''.join(((valfmt % self(dims)),(dimfmt % dims)))

class UnitsDatabase(object):
    def __init__(self, base_types, prefixes):
        '''create a UnitsDatabase object'''
        # start creation of units dictionary
        self.units={}
        for base in base_types:
            self.units[base]=Q(1, base, utype='BASE')
        self.prefixes=prefixes
    def __getitem__(self, key):
        '''grab item from dictionary if it exists, otherwise try prefixes'''
        if key in self.units:
            return self.units[key]
        else:
            if len(key)==1: # don't look for prefix if one letter unit
                raise DimensionsError, 'unit %s not found' % key
            for prefix in self.prefixes:
                if key.startswith(prefix):
                    return self.prefixes[prefix]*self.units[key[len(prefix):]]
            raise DimensionsError, 'unit %s not found' % key
    def addUnit(self,name,utuple):
        '''add a unit to the unit database'''
        val=utuple[0]
        dims=utuple[1]
        self.units[name]=Q(val,dims)
    def addBase(self,name):
        '''add a base type to the unit database'''
        val=1
        self.units[name]=Q(val,name,utype='BASE')
    def addPrefix(self,name,val):
        '''add a prefix to the unit database'''
        self.prefixes[name]=val
    def find(self,s):
        '''lists units containing the substring s'''
        re_find=re.compile(r'.*%s.*' % s ,re.I)
        res=[key for key in units.units.keys() if re_find.match(key)]
        res.sort()
        for unit in res:
            print unit

# read the bases, prefixes and units from the dimensions.data file
execfile(os.path.join(os.path.dirname(__file__),'dimensions.data'))

units=UnitsDatabase(BASE_TYPES, PREFIXES)

for unit,tup in UNITS_LIST:
    units.addUnit(unit,tup)

BASE_TYPES=[]
PREFIXES={}
UNITS_LIST=[]

# now add any from the user.data file
try:
    execfile(os.path.join(os.path.dirname(__file__),'user.data'))
    for base in BASE_TYPES:
        units.addBase(base)
    for pref in PREFIXES:
        units.addPrefix(pref,PREFIXES[pref])
    for unit, dimtup in UNITS_LIST:
        units.addUnit(unit,dimtup)
except IOError:
    pass


if __name__=='__main__':
    # this is where the tests live
    D0=Q(3, 'mN*m/A')
    D1=Q(4, 'A')
    assert(repr(D0*D1)=="Q(0.012, 'kg*m**2/s**2')")
    D2=Q(0.25, '1/A')
    assert(repr(D0/D2)=="Q(0.012, 'kg*m**2/s**2')")

    D3=Q(1,'1/W**(1/2)')
    D4=Q(1,'1/W**(1/2.)')
    D5=Q(1,'1/W**(1./2)')
    D6=Q(1,'1/W**(1./2.)')
    assert(D3==D4)
    assert(D3==D5)
    assert(D3==D6)

    D7=Q(3.3,'N*cm/W**0.5')
    assert(repr(D7)=="Q(0.033, 'kg**0.5*m/s**0.5')")
    assert(repr(D7*D7)=="Q(0.001089, 'kg*m**2/s')")
    assert(repr(D7**2)=="Q(0.001089, 'kg*m**2/s')")

    T=Q(15.2,'mN*m')
    ke=Q(3.6,'V/krpm')
    assert(repr(T/ke)=="Q(0.442150077172, 'A')")

    vel=Q(4000,'rpm')
    P=T*vel
    assert(str(P)=="Q(6.36696111128, 'kg*m**2/s**3')")
    assert(str(P('W'))=="6.36696111128")
    assert(P('horsepower')==0.0085348004172591339)
    units.addBase('sample')
    srate=Q(36,'ksample/s')
    units.addBase('interrupt')
    irate=Q(600,'interrupt/s')
    assert(srate/irate==Q(60.0, 'sample/interrupt'))
    km=Q(2.035,'N*cm/W**0.5')
    assert(str((T/km)**2)== "Q(0.557902552989, 'kg*m**2/s**3')")
    assert(((T/km)**2)('W')==0.55790255298854785)

    AddedInconsistentDims=0
    try:
        Q(2,'ft')+Q(3,'s')
    except DimensionsError:
        AddedInconsistentDims=1
    assert(AddedInconsistentDims)

    SubtracedInconsistentDims=0
    try:
        Q(2,'ft')-Q(3,'s')
    except DimensionsError:
        SubtracedInconsistentDims=1
    assert(SubtracedInconsistentDims)

    assert (-Q(5,'')==Q(-5,''))
    assert (+Q(5,'')==Q(5,''))
    assert (abs(Q(-5,''))==Q(5,''))
    assert (abs(Q(5,''))==Q(5,''))
