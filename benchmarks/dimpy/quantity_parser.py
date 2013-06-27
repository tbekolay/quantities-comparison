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

Defines the QuantityParser and ParseHistory classes, aswell as the function parse(string) which will parse string using a new instance of
QuantityParser and a blank history.
"""
from derived_units import *
from flyquant import *

class ParseError(Exception):
    pass

class QuantityParser:
    '''
    A parser for the language of quantities.

    ARRTIBUTES:
    QuantityParser.TOK_...     --- tokens for the parser
    QuantityParser.SI_PREFIXES, SI_PREFIXES_SHORT      --- dictionaries.  stores the SI prefixes
    QuantityParser.WORD_NUMBERS            --- a dictionary.  stores some words and their values
    QuantityParser.ALL_UNITS        --- a dictionary. units from the units and derived_units modules : values
    QuantityParser.UNIT_SYMBOLS     --- a dictionary. unit symbol : unit names (a string)
    self.history        --- the ParseHistory we should use during parsing
    self.string     --- the string to be parsed
    self.pos        --- an integer, the current character to be parsed in self.string
    self.output_string      --- the interpretation of self.string i.e. if self.string - "3 meters", self.output_string = "3*meter"
                            --- one is generated for each expression in a query
    self.fly_variables      --- the Flyquants created during a parse are stored in this as name:value pairs
    self.dict           --- the content of all the other dictionaries are copied into this    
    self.false_requests     --- bool, if we should allow things like 3 meters in miles per hour DEFAULT:False
    self.on_the_fly         --- bool, allow on the_fly_defining of variables                    DEFAULT:True
    self.html               --- bool, format output using html                                  DEFAULT:False
    
    
    METHODS:
    self.parse(string, history)     --- parses string with ParseHistory history.  Will automaticaly update history.
                                        Other methods are a consequence of this.
    
    This is an infix parser that will also handle terms that look like 3m, 3m**2, 3m^2, 3m2 (to mean 3m^2), 3millimeter,
    3mm, ten thousand.  Accepts "per" to mean divide and "in" to mean a conversion ("meters in miles").
    Be aware that there are two types of multiplication:
        The * operator has the same precedence as a standard infix calculator.
        A space between words i.e. meter second or ten million is parsed first.  This is important when asking for a division:
            1/ten*million = (1/ten)*million
            1/ten million = 1/(ten million)        

    Grammar (BNF):
        query      := expression (ws query_op expression)*
        query_op   := [in,=]
        expression := term (ws [+-] ws term)*
        term       := factor (ws [*/] ws factor)*
        factor     := powterm (ws ('**'|'^') ws powterm)*
        powterm    := '(' ws expression ws ')' | [+-] ws powterm | number | (number)? ws sentence
        sentence   := (word ws (number|('**'|'^') ws number)?)+
        word       := an alphabetic string (i.e. all characters pass isalpha())
        number     := integer | real
        integer    := digit+
        real       := ((digit+ ('.' digit*)?) | ('.' digit+)) ([eE] [+-]? digit+)?
        digit      := [0-9]
        ws         := [ \t\r\n]*
    '''
    
    #Define Tokens    
    TOK_PLUS  = 0
    TOK_MINUS = 1
    TOK_STAR  = 2
    TOK_SLASH = 3
    TOK_CARET = 4
    
    TOK_IN = 5
    TOK_EQU = 6   
    
    SI_PREFIXES = {"yocto":10**-24,"zepto":10**-21,"atto":10**-18,"femto":10**-15,"pico":10**-12,"nano":10**-9,"micro":10**-6,"milli":10**-3,
    "centi":10**-2,"deci":10**-1,"hecto":10**2,"kilo":10**3,"mega":10**6,"giga":10**9,"tera":10**12,\
    "peta":10**15,"exa":10**18,"zetta":10**21,"yotta":10**24}
    SI_PREFIXES_SHORT = {"y":10**-24,"z":10**-21,"a":10**-18,"f":10**-15,"p":10**-12,"n":10**-9,"u":10**-6,"m":10**-3,\
    "c":10**-2,"d":10**-1,"h":10**2,"k":10**3,"M":10**6,"G":10**9,"T":10**12,"P":10**15,"E":10**18,"Z":10**21,"Y":10**24}
    WORD_NUMBERS = {"one":1,"two":2,"three":3,"four":4,"five":5,"six":6,"seven":7,"eight":8,"nine":9,"ten":10,"hundred":100,"thousand":10**3,\
        "million":10**6,"billion":10**9,"trillion":10**12}
    ALL_UNITS = {}  #of the form {unit_name:value}
    UNIT_SYMBOLS = {}   #of the form {unit_symbol:unit_name}
    #add the units to the dictionary
    for u in Quantity.all_unit_names:
        exec "v = "+u
        ALL_UNITS[u] = v
        UNIT_SYMBOLS[str(v)]=u
        
    def __init__(self, html = False, on_the_fly = True, false_requests = False):
        self.fly_variables = {}        #this contains both on_the_fly variables, and those variables defined interms of previous variables
        self.dict = {}
        #allow on the fly units?
        self.on_the_fly = on_the_fly
        self.false_requests = false_requests
        
        #format output_string using html?
        self.html = html
        
    def parse(self, string, history):
        '''
        Parses a string input using a infix notation.
        
        Returns a list with 3 entries.
        The first is the value of the parsed input (i.e. of type Quantity, Unit, Flydim etc.).
        The second is a standard format string representation of what is parsed (this is the output the user sees when running in __main__.
        The third is the string that replaces a history reference, i.e. "#0" is replaced by "3*meter".
        
        >>> p = QuantityParser()
        >>> h = ParseHistory()
        >>> p.parse("3 meters in miles", h)
        [3.0 m, '3*meter = 0.00186411357671 * mile', '3*meter']
        >>> h.prnt()
        0: 3 meters in miles
        '''        
        self.history = history
        self.fly_variables = {}
        self.string = string.strip()
        self.history.add(self.string)
        self.pos = 0
        self.output_string = ""
        self.imperial()
        self.string = self.string.replace(" in "," % ")
        self.string = self.string.replace(" per ","/")
        
        return self.parse_query()
    
    def imperial(self):
        '''
        Quick fix so that there are a variety of ways to enter "Imperial gallon" etc.
        '''
        s = " "+self.string+" "
        s = s.replace("Imperial","imperial")
        s = s.replace(" U.S. "," US ")
        s = s.replace(" U.S "," US ")
        s = s.replace(" oz. "," ounce ")
        s = s.replace(" oz "," ounce ")
        s = s.replace(" fl. "," fluid ")
        s = s.replace(" fl "," fluid ")
        s = s.replace("imperial gallon","impGal")
        s = s.replace("US gallon","usGal")
        s = s.replace("US gallon","usGal")
        s = s.replace("gallon","impGal")
        s = s.replace("imperial fluid ounce","impFlOz")
        s = s.replace("US fluid ounce","usFlOz")
        s = s.replace("fluid ounce","impFlOz")
        
        self.string = s.strip()
        
    def parse_query(self):
        """
        query := expression (ws query_op expression)?
        
        Returns a list [value, formatted_string, history_string]
        Where value is the required value, formatted_string is printed to the string, and history_string is put into formatted_string
        when the parser finds a history request
        """
        initial_expression = self.parse_expression()
        lhs_string = self.output_string
        self.output_string = ""
         
        if self.check_query_op():
            op = self.parse_query_op()
            if op == self.TOK_EQU:
                #we have an assignment to make
                variable_name = self.string[:self.pos-1]
                variable_name = variable_name.replace(" ","")
                self.history.defined_variables[variable_name] = self.parse_expression()
                if self.html:
                    return [self.history.defined_variables[variable_name], "<font color = 'lime'>"+variable_name + "</font> = " + self.output_string,\
                    variable_name + " = " + self.output_string]
                return [self.history.defined_variables[variable_name], variable_name + " = " + self.output_string,\
             "<font color = 'lime'>"+variable_name + "</font>"]
            elif op == self.TOK_IN:
                #we have a conversion
                position = self.pos
                target_quantity = self.parse_expression()
                if (not self.false_requests) and (not (initial_expression/target_quantity).is_dimensionless()):
                    raise DimensionMismatchError("Illegal conversion", get_dimensions(initial_expression), get_dimensions(target_quantity))
                string = str(initial_expression/target_quantity)
                if self.html and not (initial_expression/target_quantity).is_dimensionless():
                    counter = 0
                    while string[counter].isdigit() or string[counter] == ".":
                        counter += 1
                    units = string[counter:]
                    string = string[:counter]+"<font color = blue>"+units+"</font>"
                return [initial_expression, lhs_string +" = "+ string +" * "+self.output_string, lhs_string]
            
        return [initial_expression, lhs_string +" = "+ str(initial_expression), lhs_string]
            
    def parse_query_op(self, increment = True):
        """
        query_op := [in,=]
        """
        if self.pos >= len(self.string):
            raise ParseError, "Query operator expected at position %i"%self.pos
            
        if self.string[self.pos] == "=":
            if increment:
                self.pos += 1
            return self.TOK_EQU
        
        if self.string[self.pos] == "%":
            if increment:
                self.pos += 1
            return self.TOK_IN
        
        raise ParseError, "Query operator expected at position %i"%self.pos
        
    def check_query_op(self):
        self.skip_whitespace()
        try:
            self.parse_query_op(False)
        except ParseError:
            return False
        return True
        
    def parse_operator(self, increment = True, add_to_string = True):
        """
        integer := [0-9]+
        """
        if self.pos >= len(self.string):
            raise ParseError, "Operator expected at position %i"%self.pos
        
        if self.string[self.pos] == '*' and self.pos < len(self.string)-1 and self.string[self.pos+1] == '*':
            if increment:
                self.pos += 2
                self.output_string += "^"
            return self.TOK_CARET
        try:
            operator = {
                '+': self.TOK_PLUS,
                '-': self.TOK_MINUS,
                '*': self.TOK_STAR,
                '/': self.TOK_SLASH,
                '^': self.TOK_CARET
            }[self.string[self.pos]]
        except KeyError, IndexError:
            raise ParseError, "Operator expected at position %i"%self.pos
                
        if increment:
            self.output_string += self.string[self.pos] #this needs to go here,
                                                        #otherwise we would be adding to the output string when checking for an operator
            self.pos += 1
        return operator
        
    def check_plus(self):
        """
        We check if the next non-whitespace character is '+' or '-'
        """
        self.skip_whitespace()
        try:
            op = self.parse_operator(False)
        except ParseError:
            return False
        if op == self.TOK_PLUS or op == self.TOK_MINUS:
            return True
        else:
            return False
        
    def check_times(self):
        """
        We check if the next non-whitespace character is '*' or '/'
        """
        self.skip_whitespace()
        try:
            op = self.parse_operator(False)
        except ParseError:
            return False
        if op == self.TOK_STAR or op == self.TOK_SLASH:
            return True
        else:
            return False
    
    def check_power(self):
        """
        We check if the next non-whitespace character is '**' or '^'
        """
        self.skip_whitespace()
        try:
            op = self.parse_operator(False)
        except ParseError:
            return False
        if op == self.TOK_CARET:
            return True
        else:
            return False
        
    def check_alpha(self):
        """
        We check if the next non whitespace character is alphabetic
        """
        self.skip_whitespace()
        
        return self.pos < len(self.string) and self.string[self.pos].isalpha()
        
    def check_number(self):
        """
        We check if the next non-whitespace character is a number.
        
        number := integer | real
        """
        self.skip_whitespace()
        return self.pos < len(self.string) and (self.string[self.pos].isdigit() or self.string[self.pos]==".")      
        
    def parse_expression(self):
        """
        expression := term (ws [+-] ws term)*
        """
        if self.pos >= len(self.string):
            raise ParseError, "End of input reached before finished parsing"
            
        leading_term = self.parse_term()
        
        while self.check_plus():
            self.skip_whitespace()
            op = self.parse_operator()
            self.skip_whitespace()
            term = self.parse_term()
            
            if op == self.TOK_PLUS:
                leading_term += term
            elif op == self.TOK_MINUS:
                leading_term -= term
            else:
                #this will never happen, sanity check
                raise ParseError, "expected '+' or '-' between terms"
        
        return leading_term
            
    def parse_term(self):
        """
        term := factor (ws [*/] ws factor)*
        """
        leading_factor = self.parse_factor()
        while self.check_times():
            self.skip_whitespace()
            op = self.parse_operator()
            self.skip_whitespace()
            factor = self.parse_factor()
            if op == self.TOK_STAR:
                leading_factor *= factor
            elif op == self.TOK_SLASH:
                leading_factor /= factor
            else:
                #this will never happen, sanity check
                raise ParseError, "expected '*' or '/' between factors"
                
        return leading_factor
                
    def parse_factor(self):
        """
        factor := powterm (ws ('**'|'^') ws powterm)*
        """
        leading_powterm = self.parse_powterm()
        if self.check_power():
            return leading_powterm ** self.get_exponent()
        else:
            return leading_powterm
    
    def get_exponent(self):
        """
        Used when calculating factors of the form 2^2^2^2
        """
        self.skip_whitespace()
        op = self.parse_operator()
        self.skip_whitespace()
        powterm = self.parse_powterm()
        if self.check_power():
            return powterm ** self.get_exponent()
        else:
            return powterm
    
    def parse_powterm(self):
        """
        powterm := '(' ws expression ws ')' | [+-] ws powterm | number | (number)? ws sentence | '#' number
        """
        if self.string[self.pos] == "(":
            self.output_string += "("
            start_index = self.pos  #recorded for error message
            self.pos += 1
            self.skip_whitespace()
            expr = self.parse_expression()
            self.skip_whitespace()
            if self.pos < len(self.string) and self.string[self.pos]==")":
                self.output_string += ")"
                self.pos += 1
                return expr
            else:
                raise ParseError, "expected ')' after expression "+self.string[start_index:self.pos]+" at position %i"%self.pos
        elif self.string[self.pos] == "#":
            #then we need to substitute in the value in the history
            self.pos += 1
            if self.check_number():
                numb = self.parse_integer()
            else:
                raise ParseError, "expected an integer after # at position %i"%self.pos
            new_p = QuantityParser()
            answer = new_p.parse(self.history.read(numb), self.history.copy())
            if answer[2][0] == "(" and answer[2][-1] == ")":
                self.output_string += answer[2]
            else:
                self.output_string += "("+ answer[2] +")"
            return answer[0]
        elif self.check_number():
            numb = self.parse_number()
            #need to see if we have a sentence next
            self.skip_whitespace()
            if self.check_alpha():
                self.output_string += "*"
                sent = self.parse_sentence()
                return numb*sent
            return numb
        elif self.check_alpha():
            return self.parse_sentence()
        elif self.check_plus():
            op = self.parse_operator()
            self.skip_whitespace()
            if op == self.TOK_PLUS:
                return self.parse_powterm()
            else:
                return -self.parse_powterm()
        else:
            #sanity check
            raise ParseError, "expected '(expression)', a number, a unit or a powerterm at at position %i"%self.pos
         
    def parse_sentence(self):
        """
         sentence   := (word ws (number|('**'|'^') ws number)?)+
        """
        sentence = 1
        count = 0
        temp_string = ""
        while self.check_alpha():
            if count > 0:
                temp_string += "*"
            count += 1
            word = self.parse_word()
            string = word[1]
            word = word[0]
            if self.check_number():
                power = self.parse_number(False)
                string = "("+string+")"+"^"+str(power)
                word = word ** power
            elif self.check_power():
                self.parse_operator(True, False)
                self.skip_whitespace()
                power = self.parse_number(False)
                string = "("+string+")"+"^"+str(power)
                word = word ** power
            sentence *= word
            temp_string += string
        
        if count > 1:
            temp_string = "("+temp_string+")"
        self.output_string += temp_string
        return sentence
        
    def parse_word(self):
        """        
        word := an alphabetic string (i.e. all characters pass isalpha())
        
        Returns (value, formatted_string)
        """
        word = ""
        while self.pos < len(self.string) and (self.string[self.pos].isalpha() or self.string[self.pos] == "_"):
            word += self.string[self.pos]
            self.pos += 1
        
        self.dict = {}
        self.dict.update(self.ALL_UNITS)
        self.dict.update(self.WORD_NUMBERS)
        self.dict.update(self.fly_variables)
        self.dict.update(self.history.defined_variables)
        imperial = {"impGal":"(Imperial gallon)","usGal":"(US gallon)","impFlOz":"(Imperial fluid ounce)","usFlOz":"(US fluid ounce)"}
          
        if word in self.dict.keys():
            if word in imperial.keys():
                return (self.dict[word], imperial[word])
            if self.html and word in self.history.defined_variables.keys():
                #we need this infront of the fly_variables, as when the new unit is defined, it is first put into the fly_variables dictionary
                return (self.dict[word], "<font color='lime'>"+word+"</font>")
            if self.html and word in self.fly_variables.keys():
                return (self.dict[word], "<font color='red'>"+word+"</font>")
            return (self.dict[word], word)
        
        if word in self.UNIT_SYMBOLS.keys():
            return (self.ALL_UNITS[self.UNIT_SYMBOLS[word]], self.UNIT_SYMBOLS[word])    
                
        if word[-1] == "s" and word[:-1] in self.dict.keys():
            if word[:-1] in imperial.keys():
                return (self.dict[word[:-1]], imperial[word[:-1]])
            if self.html and word[:-1] in self.fly_variables.keys():
                return (self.dict[word[:-1]], "<font color='red'>"+word[:-1]+"</font>")
            return (self.dict[word[:-1]], word[:-1])
        
        for key in self.SI_PREFIXES:            
            if word.startswith(key) and word[len(key):] in self.UNIT_SYMBOLS.keys():
                return (self.SI_PREFIXES[key]*self.dict[self.UNIT_SYMBOLS[word[len(key):]]],\
             str(self.SI_PREFIXES[key])+"*"+self.UNIT_SYMBOLS[word[len(key):]])
            if word[len(key):] in imperial.keys():
                return (self.SI_PREFIXES[key]*self.dict[word[len(key):]], str(self.SI_PREFIXES[key])+"*"+imperial[word[len(key):]])
            if word.startswith(key) and word[len(key):] in self.dict.keys():
                if self.html and word[len(key):] in self.fly_variables.keys():
                    return (self.SI_PREFIXES[key]*self.dict[word[len(key):]], str(self.SI_PREFIXES[key])+"*<font color = 'red'>"+\
                    word[len(key):]+"</font>")
                return (self.SI_PREFIXES[key]*self.dict[word[len(key):]], str(self.SI_PREFIXES[key])+"*"+word[len(key):])
            if word[-1] == "s" and word.startswith(key) and word[len(key):-1] in self.dict.keys():
                if self.html and word[len(key):-1] in self.fly_variables.keys():
                    return (self.SI_PREFIXES[key]*self.dict[word[len(key):-1]], str(self.SI_PREFIXES[key])+"*<font color = 'red'>"+\
                    word[len(key):-1]+"</font>")
                return (self.SI_PREFIXES[key]*self.dict[word[len(key):-1]], str(self.SI_PREFIXES[key])+"*"+word[len(key):-1])
                if word[len(key):-1] in imperial.keys():
                    return (self.SI_PREFIXES[key]*self.dict[word[len(key):-1]], str(self.SI_PREFIXES[key])+"*"+imperial[word[len(key):-1]])
            
        for key in self.SI_PREFIXES_SHORT:            
            if word.startswith(key) and word[len(key):] in self.UNIT_SYMBOLS.keys():
                return (self.SI_PREFIXES_SHORT[key]*self.dict[self.UNIT_SYMBOLS[word[len(key):]]],\
             str(self.SI_PREFIXES_SHORT[key])+"*"+self.UNIT_SYMBOLS[word[len(key):]])
            if word[len(key):] in imperial.keys():
                return (self.SI_PREFIXES_SHORT[key]*self.dict[word[len(key):]], str(self.SI_PREFIXES_SHORT[key])+"*"+imperial[word[len(key):]])
            if word.startswith(key) and word[len(key):] in self.dict.keys():
                if self.html and word[len(key):] in self.fly_variables.keys():
                    return (self.SI_PREFIXES_SHORT[key]*self.dict[word[len(key):]],\
                    str(self.SI_PREFIXES_SHORT[key])+"*<font color = 'red'>"+word[len(key):]+"</font>")
                return (self.SI_PREFIXES_SHORT[key]*self.dict[word[len(key):]], str(self.SI_PREFIXES_SHORT[key])+"*"+word[len(key):])
            if word[-1] == "s" and word.startswith(key) and word[len(key):-1] in self.dict.keys():
                if self.html and word[len(key):-1] in self.fly_variables.keys():
                    return (self.SI_PREFIXES_SHORT[key]*self.dict[word[len(key):-1]],\
                    str(self.SI_PREFIXES_SHORT[key])+"*<font color = 'red'>"+word[len(key):-1]+"</font>")
                if word[len(key):-1] in imperial.keys():
                    return (self.SI_PREFIXES_SHORT[key]*self.dict[word[len(key):-1]], str(self.SI_PREFIXES_SHORT[key])+"*"+imperial[word[len(key):-1]])
                return (self.SI_PREFIXES_SHORT[key]*self.dict[word[len(key):-1]], str(self.SI_PREFIXES_SHORT[key])+"*"+word[len(key):-1])
            
        if self.on_the_fly:
            self.fly_variables[word] = Flydim(word)
            if self.html:
                return (self.fly_variables[word], "<font color = 'red'>"+word+"</font>")
            return (self.fly_variables[word], word)
        
        raise ParseError, "'"+word+"' not found in dictionary (occoured at position %i)"%(self.pos-1)

    def parse_number(self, add_to_string = True):
        """
        number     := integer | real
        real       := ((digit+ ('.' digit*)?) | ('.' digit+)) ([eE] [+-]? digit+)?
        """
        integer_part = 0
        decimal_part = 0.0
        power_part = 0
        
        if not self.string[self.pos] == ".":
            integer_part = self.parse_integer()         
        
        if self.pos == len(self.string):
            if add_to_string:
                self.output_string += str(integer_part)
            return integer_part
        
        flag_decimal_part = False
        if self.string[self.pos] == ".":
            flag_decimal_part = True
            self.pos += 1
            if not self.string[self.pos].isdigit():
                raise ParseError, "expected digit after decimal point at position %i"%self.pos
            temp = self.parse_integer()
            counter = 10
            while counter < temp:
                counter *= 10
            decimal_part = float(temp)/float(counter)
        
        if self.pos == len(self.string):
            if add_to_string:
                self.output_string += str(integer_part + decimal_part)
            return integer_part + float(decimal_part)   #need float(decimal_part) for when decimal_part = 0
        
        if self.string[self.pos] in "eE":
            self.pos += 1
            op = False
            if self.check_plus():
                op = self.parse_operator()
            if op == self.TOK_PLUS:
                power_part = self.parse_integer()
            elif op == self.TOK_MINUS:
                power_part = -self.parse_integer()
            else:
                power_part = self.parse_integer()
        
        if flag_decimal_part:
            integer_part += float(decimal_part)     #need float(decimal_part) for when decimal_part = 0
        if add_to_string:
            self.output_string += str(integer_part)
        if (not power_part == 0) and add_to_string:
            self.output_string += "*10^"+str(power_part)
        return (integer_part)*10**power_part
        
    def parse_integer(self):
        """
        integer := digit+
        digit   := [0-9]
        """
        if (self.pos >= len(self.string)) or (self.string[self.pos] < '0') or (self.string[self.pos] > '9'):
            raise ParseError, "Integer expected at position %i"%self.pos

        start = self.pos
        while (self.pos < len(self.string)) and (self.string[self.pos] >= '0') and (self.string[self.pos] <= '9'):
            self.pos += 1
        return int(self.string[start:self.pos])
    
    def skip_whitespace(self):
        """
        ws := [ \t\r\n]*
        """
        while (self.pos < len(self.string)) and (self.string[self.pos] in ' \t\r\n'):
            self.pos += 1
            
class ParseHistory:
    """
    Stores the most recent 200 requests for recall.
    ATTRIBUTES:
        self.history            --- a list of the most recent strings.  An entry with a smaller index is older.
        self.defined_variables  --- a dictionary of variable_name:variable_value pairs so that we can have different variables for each user
    METHODS:
        self.add(string)        --- add a string to the end of self.history
        self.delete(position)   --- delete the entry with index position
        self.read(position)     --- read the entry at position
        self.length()           --- return the number of entries
        self.prnt()             --- print the entires
        self.copy()             --- returns a copy
    """
    def __init__(self):
        self.history = []    #stores the input string of previous requests
        self.defined_variables = {}   #stores the variables that are defined by the user, {variable_name:value}
    def add(self, string):
        self.history.append(string)
        if len(self.history) > 200:
            del self.history[0]
    def delete(self, pos):
        del self.history[pos]
    def read(self, pos):
        if not 0 <= pos < self.length():
            raise ParseError, "History retrieval out of range.  The valid range is 0-"+str(self.length()-1)
        return self.history[pos]
    def length(self):
        return len(self.history)
    def prnt(self):
        for i in range(self.length()):
            print str(i)+": "+str(self.history[i])
    def copy(self):
        '''
        Returns a copy of self.
        '''
        new_history = ParseHistory()
        new_history.history = self.history + []
        new_history.defined_variables = self.defined_variables.copy()
        return new_history
    

def parse(string):
    '''
    Parses string and returns the value, but we do not consider a history.
    '''
    temporary_parser = QuantityParser()
    return temporary_parser.parse(string, ParseHistory())[0]
    
if __name__ == '__main__':
    import doctest
    doctest.testmod()
    import readline
    p = QuantityParser()
    h = ParseHistory()
    while True:
        try:
            inpt = raw_input("---> ")
            if inpt == "history()":
                h.prnt()
            elif inpt.startswith("delete(") and inpt.endswith(")"):
                #we need to delete a history
                number = int(inpt[7:-1])
                h.delete(number)
            elif inpt == "illegal_requests()":
                p.false_requests = not p.false_requests
            else:
                print p.parse(inpt,h)[1]
        except ParseError, message:
            print 'Parse error:', message
        except DimensionMismatchError, message:
            print 'Dimension error:', message
