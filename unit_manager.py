import re
import copy

'''
Manages units in multiplication or addition operations.  It is a great tool for dimensional analysis!
It comes with a set of predefined units, the user can define new ones as combinations of these. 
All calculated results are returned as combinations of basis SI units: kg, m, s, C, K, for
 mass, distance, time, electric charge, and temperature. 
 Cost $ is also a defined basis unit, so it’s possible to have calculations like cost per unit mass.
'''

trace = True

class Quantity:
    '''A unit, or a number with optional units. 
    
    Every unit is represented as a 6-dimensional vector in terms of the basis units, with a numeric coefficient. 
    The number in each dimension represents the power to which that basis unit is raised in the definition of a given unit. 
    For instance, newtons are kilograms times meters per second squared.  
    That is: 1 N = 1 [1,1,-2,0,0,0], in the basis ['kg', 'm', 's', 'C', 'K', '$']. 
    A foot is 0.3048 meters, so 1 ft = 0.3048 [0,1,0,0,0,0]. 
    This backend representation allows for quick and easy comparison of units: 
      if you want to check that two units are commensurable (they represent the same physical quantity), simply check if 
      the unit vectors are equal. Add the coefficients to add them. If you want to multiply two units, simply add the unit 
      vectors and multiply the coefficients. It is also easy to define new units, you just need to determine the unit vector 
      and coefficient. This representation is simple and elegant. '''
    def __init__(self, value, vec):
        self.value = value
        self.vec = vec

    def commensurable(self, quantity2):
        '''Returns true if the two quantities can be added or subtracted. (Their units are compatible.)'''
        return self.vec == quantity2.vec # The unit vectors must be the same.
   
    def __add__(self, quantity2):
        '''Adds "+" two Quantity objects by adding their values if the unit vectors are the same. Otherwise, raises ValueError '''
        # First check that they have compatible units:
        if self.commensurable(quantity2):
            return Quantity(self.value + quantity2.value, self.vec)
        else:
            raise ValueError("Incompatible units.") # TODO: Make a printing function so I can say something informative in this error message.     
        
    def __sub__(self, quantity2):
        # First check that they have compatible units:
        if self.commensurable(quantity2):
            return Quantity(self.value - quantity2.value, self.vec)
        else:
            raise ValueError("Incompatible units.") # TODO: Make a printing function so I can say something informative in this error message.

    def __mul__(self, quantity2):
        # Add the unit vectors and multiply the values:
        return Quantity(
            value= self.value * quantity2.value,
            vec= [u1 + u2 for u1, u2 in zip(self.vec,  quantity2.vec)] # self.vec + quantity2.vec with numpy arrays
        )
    
    def __truediv__(self, quantity2):
        '''Implement division operator "/": Subtract the unit vectors and take the quotient of the values'''
        return Quantity(
            value= self.value / quantity2.value,
            vec= [u1 - u2 for u1, u2 in zip(self.vec,  quantity2.vec)] # self.vec - quantity2.vec with numpy arrays
        )

    def _str_vec(self): # TODO The string concatenation is slow as implemented. Is this worth doing better?
        '''Returns a string representation of the units represented by the unit vector. For instance, a unit vector [1,0,0,0,0,0] will return 'kg' (unless the basis has been modified).'''
        string = ""
        for dim, basis_unit in zip(self.vec, Units.basis()): # dim = how many factors of this basis unit are in self
            if dim > 0:
                string = ('.' + basis_unit) * dim + string # Prepend multiplication
            elif dim < 0:
                string += ('/' + basis_unit) * -dim # Append division (so you aren't stuck with "/s.C" when you want "C/s")
        return string[1:] # Drop that leading "." that I decided was easier to remove later than avoid adding in the first place.
    
    def __str__(self): # TODO Control how many digits of precision are shown?
        return str(self.value) + " " + self._str_vec()

    @staticmethod
    def parse_unit(str):
        '''Parse a string specification of units into Quantity. \n
        Valid specifications are separated by '.' or '*' for multiplication, and '/' for division. No spaces allowed. \n
        For instance: meters squared is written as 'm.m', kilograms times meters per second squared is 'kg.m/s/s'\n 
        raises ValueError on failure.''' # TODO Add capacity for powers (ex: m^2)?
        spec = re.split(r"([*./])", str) # Specification of units
        # Every odd element of the list spec is a unit, this iterates over the list with step size 2
        unit_names = list(map(lambda s: s.strip(), spec[::2])) # using slice indexing, start:stop:step
        # Every even element of spec is a multiply or divide operation:
        operations = spec[1::2]
        # First check that all units are known:
        for unit in unit_names: 
            if not Units.knows(unit):
                raise ValueError(f"'{unit}' is not a unit known to this program." + 
                                 " Please define it using the define function." + 
                        ("\nThis unit was encountered while parsing the string: " + str if unit != str else ""))
        # If they are all known units:
        # Start with the first unit, then multipy or divide the following units as specficied:
        quantity = Units.get(unit_names[0]) # First unit
        for op, name in zip(operations, unit_names[1:]): 
            if op == '.' or op == '*': # Multiply
                quantity *= (Units.get(name))
            else:  # op == '/'         # Divide
                quantity /= (Units.get(name))
        return quantity

    @staticmethod
    def parse_quantity(input):
        '''Parse a string value into Quantity. \n
        ex: "4.30e+14 Hz", "30 m/s", or "10" \n
        If the value is not unitless, 
        the numerical amount, e.g. "30", must be separated from the unit specification, e.g. "m/s", by whitespace. No other whitespace allowed.
        Valid unit specifications are separated by '.' or '*' for multiplication, and '/' for division. \n
        For instance: meters squared is written as 'm.m', kilograms times meters per second squared is 'kg.m/s/s' \n
        rasies ValueError raises ValueError on failure. ''' # TODO Add capacity for powers (ex: m^2)?
        # Nested Helper:
        def parse_amount(str_amount):
            '''Uses Python's float() function'''
            try:
                # I want the user to be able to use commas, but python's float function can't handle them. 
                # I simply remove the commas (which is not ideal: "10,0,3,2" works but it probably shouldn't).
                return float(str_amount.replace(",", "")) 
            except ValueError: # Modify the error message to be more meaningful.
                raise ValueError(f"Could not convert the string {str_amount} to a number in the quantity {input}.") from None

         # Strip leading & trailing whitespace. The presence of whitespace is used to decide whether the
         #  quantity is a unitless number, or a whitespace-separated number and unit. Avoids getting 
         #  confused by other whitespace.
        input = input.strip() 
        # First check if there are two parts by checking for whitespace in str.
        if re.search(r"\s", input):                   # If there is an amount and unit:
            amount, unit_name = re.split(r"\s", input, maxsplit=1)
            # Parse the unit specification into a Quantity:
            try:
                quantity = Quantity.parse_unit(unit_name)
            except ValueError as err:
                err.add_note("This error was encountered while parsing the quantity " + input)
                raise
            # Parse the amount and multiply the Quantity by it:
            quantity.value *= parse_amount(amount)
        else:                                      # If there is only an amount or a unit.
            # Try parsing it as an amount:
            try:
                quantity = Quantity(parse_amount(input), [0,0,0,0,0,0]) # Unitless Scalar
            except ValueError as err:
                err.add_note(f"Attempting to parse {input} as a unit instead.")
                # Try parsing it as a unit:
                quantity = Quantity.parse_unit(input) # If this fails, there will be error-chaining.

        return quantity

class Units:
    '''Stores units dictionary, provides controlled access for editing and reading.'''
    units = {
        # Basis:
        'kg': Quantity(1, [1,0,0,0,0,0]), # mass, 1 kilogram
        'm':  Quantity(1, [0,1,0,0,0,0]), # distance,  1 meter
        's':  Quantity(1, [0,0,1,0,0,0]), # time, 1 second
        'C':  Quantity(1, [0,0,0,1,0,0]), # charge, 1 coulomb
        'K':  Quantity(1, [0,0,0,0,1,0]), # temperature, 1 Kelvin
        '$':  Quantity(1, [0,0,0,0,0,1]), # cost, 1 dollar
        
        # Others:
        'Hz': Quantity(1, [0,0,-1,0,0,0]), # frequency, 1 hertz
        'J':  Quantity(1, [1,2,-2,0,0,0]), # energy, 1 joule
        'N':  Quantity(1, [1,1,-2,0,0,0]), # force, 1 newton
        
        '':   Quantity(1, [0,0,0,0,0,0]) # Unitless
    }

    # Index in array is the associated index in unit vector.
    # Useful for converting from Quantity to string 
    _basis = ['kg', 'm', 's', 'C', 'K', '$']

    description = {
        # TODO: when you define a new unit, allow for an addition to description dictionary
        'kg': 'mass',
        'm':  'distance',
        's':  'time',
        'C':  'electric charge',
        'K':  'temperature',
        '$':  'cost',

        'Hz': 'frequency',
        'J': 'energy',
        'N': 'force',
    }

    # TODO: description work when you change basis? key in terms of basis units (str_unit), value is a string describing what the unit represents,
    # for unit in _basis:
    #     description[unit] = units[unit]

    # TODO Implement metric prefix system so the below isn't necessary:
    units['g'] = units['kg'] / Quantity(1000, [0, 0, 0, 0, 0, 0])
    units['cm'] = units['m'] / Quantity(100, [0, 0, 0, 0, 0, 0])
    units['km'] = units['m'] * Quantity(1000, [0, 0, 0, 0, 0, 0])

    @staticmethod
    def define(name:str, quantity:Quantity) -> None:
        Units.units[name] = quantity

    @staticmethod
    def get(name:str):
        '''Returns a copy rather than a reference so that the dictionary elements cannot be modified accidentally.'''
        return copy.deepcopy(Units.units[name])
    
    @staticmethod
    def knows(name:str):
        return name in Units.units
    
    @staticmethod
    def basis():
        ''' Returns a list of string unit names for each unit in the basis. Order corresponds to the order
        represented by a Quantity's unit vector.
        Returns a copy rather than a reference so that it cannot be modified accidentally.'''
        return copy.copy(Units._basis)


def try_process(func, *args, **kwargs):
    '''Try to process the input. If there is an error, simply returns the string error message.'''
    try:
        return func(*args, **kwargs)
    except Exception as err:
        err_msg = str(err)
        if hasattr(err, '__notes__'):
            err_msg += " " + " ".join(err.__notes__)
        return err_msg


def define(input:str) -> str:
    ''' 
    Valid definitions are in the form: "new_unit = number old_units", ex: "kJ = 1e+3 kg.m.m/s/s"  or  "cm = 0.01 m". \n
    See parse_unit for details of valid units specifications.
    Returns string message indicating success, or raises ValueError on failure.
    '''
    new_unit, definition = input.split(" = ", maxsplit=1)
    
    # Run some checks:
    if Units.knows(new_unit): # TODO Allow the user to redefine non basis units, check if the new definition has commesurable units to the old
                          # to inform the user. Could send a double check message and act on the respnse.
        return "Define request failed. This unit already exists as " + str(Units.get(new_unit))
        # if units[new_unit] == unit: # TODO Check if it is one of the basis units!
        #     return "This unit already "
    
    # If the unit is not already defined:
    try:
        unit = Quantity.parse_quantity(definition)
    except ValueError as exc:
        exc.add_note("This error was encountered while attempting to define a new unit: " + input)
        raise

    Units.define(new_unit, unit)
    return input + " added to units dictionary."
    
def total(input:str) -> str:
    '''Adds or subtracts a sequence of quantities with commensurable units. \n
    Valid Format: quantities separated by " + " or " - ". Whitespace is required.
    Ex: "1 cm + 2 m - 10 m"'''
    ### STEP 1: Parse into Quantities and " + " or " - " operations.
    equation = re.split(r"\s+([+-])\s+", input) # Split into a list of quantities and operations.
    # Every even element is an add or subtract operation:
    operations = equation[1::2] # using slice indexing, start:stop:step
    # Note: They will all be either "+" or "-", because that's how the split function was set up.

    # Every odd element of the equation is a quantity. 
    try:
        # map() returns a generator (lazy evaluation), I convert to list so any parsing failures will occur here rather than later.
        quantities = list(map(Quantity.parse_quantity, equation[::2]))
    except ValueError as err:
        err.add_note("This parsing failure occured while parsing the summation: " + input)
        raise
    
    ### STEP 2: Calculate the total.
    # TODO: Catch an error when two quantities are incommensurable, indicate where the 
    #       failure occured in input str.
    # Start with the first quantity, then add or subtract or divide the following ones.
    total = quantities[0] # First quantity
    for op, quantitiy in zip(operations, quantities[1:]): 
        if op == '+':              # Add
            total += quantitiy
        else:  # op == '-'         # Subtract
            total -= quantitiy
    return str(total)

def product(input:str) -> str:
    '''Multiplies or divides a sequence of quantities. \n
    Valid Format: quantities separated by " * " or " / ". Whitespace is required.
    Cannot handle parantheses.
    Ex: "3.00e+8 m/s / 4.30e+14 Hz * 2" \n
    Great for dimensional analysis!'''
    ### STEP 1: Parse into Quantities and " * " or " / " operations.
    # Split into a list of quantities and operations:
    equation = re.split(r"\s+([*/])\s+", input) 
    # Every even element is a multiply or divide operation:
    operations = equation[1::2] # using slice indexing, start:stop:step
    # Note: They will all be either "*" or "/", because that's how the 
    #   split function was set up.

    # Every odd element of the equation is a quantity. 
    try:
        # map() returns a generator (lazy evaluation), 
        #  I convert to list so any parsing failures will occur here rather than later.
        quantities = list(map(Quantity.parse_quantity, equation[::2]))
    except ValueError as err:
        err.add_note("This parsing failure occurred while parsing the multiplication: " + input)
        raise
    
    ### STEP 2: Calculate the product.
    # Start with the first quantity, then multipy or divide the following ones.
    product = quantities[0] # First quantity
    for op, quantity in zip(operations, quantities[1:]): 
        if op == '*':              # Multiply
            product *= quantity
        else:  # op == '/'         # Divide
            product /= quantity
    return str(product)

def parse(input):
    '''Commands must be in one of the following forms: \n
    Definition: \n "new_unit = numeric known_unit" \n
    For instance, "cm = 0.01 m", or "kJ = 1e+3 kg.m.m/s/s". Spaces are necessary.\n
    It's okay for it to be unitless, i.e. "pi = 3.14159"\n
    Product: \n quantities separated by " * " or " / ". A quantity is a unit, or a number with optional units. 
    Whitespace is required.
    Cannot handle parantheses.
    Ex: "3.00e+8 m/s / 4.30e+14 Hz * 2" \n
    Total: \n quantities separated by " + " or " - " 
    Ex: "1 cm + 2 m - 10 m"\n
    Repeat Back:\n
     Just a single quantity. '''
    input = input.strip() # Strip whitespace to remove an irritating failure mechanism.
    definition_pattern = re.compile(r"(?P<new_unit>\S+) = (?P<coef>[+\-,e\d\.]+)(?P<known_units> \S+)?")
    if re.fullmatch(definition_pattern, input):
        if trace:
            return " ".join(["requested operation: Define ", input, "\n", try_process(define, input)])
        else: 
            return try_process(define, input)
    # Matches a single quantity (a unit, or a number with optional units). 
    echo_pattern = re.compile(r"[+\-,e\d\.]+ \S+|\S+")
    # [+\-,e\d\.]+ Matches a number containing digits and symbols (ex: "+1.02e-7" or "1,000"). 
    #             It also matches to invalid numbers like "-e,+". I'll handle that later using 
    #             Python's float() casting method.
    # [+\-,e\d\.]+(?: \S+)? Matches a number, followed by an optional unit. There must be a space 
    #             between number and unit.
    if re.fullmatch(echo_pattern, input):
        # Will attempt to process it and repeat back
        # to the client in terms of basis units.
        if trace:
            return " ".join(["requested operation: Repeat back ", input, "\n", str(try_process(Quantity.parse_quantity, input))])
        else: 
            return str(try_process(Quantity.parse_quantity, input)) # Convert to string because Quantity.parse_quantity gives a Quantity
    # Matches a string expressing addition and subtraction of quantities
    add_pattern = re.compile(r"(?:[+\-,e\d\.]+ \S+|\S+)(?: [+\-] (?:[+\-,e\d\.]+ \S+|\S+))+")
    # The string must be in the form: 
    #         <value> <+ or -> <value>, where the last two can be repeated any number of times.
    #  A value is a number optionally followed by a unit. There must be a space between number and unit.
    #  For instance: "2 cm + 3 m - 1 m"
    if re.fullmatch(add_pattern, input):
        if trace:
            return " ".join(["requested operation: Total ", input, "\n", try_process(total, input)])
        else: 
            return try_process(total, input)
    # Matches a string representing multiplication and division of quantities
    #  For instance: "2 * 3 m" or "3e8 m / 1 sec / 700 nm"
    multiply_pattern = re.compile(r"(?:[+\-,e\d\.]+ \S+|\S+)(?: [*/] (?:[+\-,e\d\.]+ \S+|\S+))+")
    if re.fullmatch(multiply_pattern, input):
        if trace:
            return " ".join(["requested operation: Product ", input, "\n", try_process(product, input)])
        else: 
            return try_process(product, input)
    ##math_pattern = re.compile(r"([+\-,e\d\.]+(?: \S+)?)(?: ([+\-*/]) ([+\-,e\d\.]+(?: \S+)?))+")
    
    # At this point, the string has failed to conform to any known operations.
    print("Invalid request: ", input)
    return "The received string does not conform to any known operations."


# Debugging:
#print(parse("1 N"))
#print(define("h = 6.626e-34 J.s"))