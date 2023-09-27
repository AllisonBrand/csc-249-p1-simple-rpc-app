import numpy as np
import re

class Quantity:
    def __init__(self, value, vec):
        self.value = value
        self.vec = vec

    def commensurable(self, quantity2):
        '''Returns true if the two quantities can be added or subtracted. (Their units are compatible.)'''
        return np.array_equal(self.vec, quantity2.vec) # The unit vectors must be the same.
   
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
            vec= self.vec + quantity2.vec
        )
    
    def __truediv__(self, quantity2):
        '''Implement division operator "/": Subtract the unit vectors and take the quotient of the values'''
        return Quantity(
            value= self.value / quantity2.value,
            vec= self.vec - quantity2.vec
        )

    def _str_vec(self): # TODO The string concatenation is slow as implemented. Is this worth doing better?
        '''Returns a string representation of the units represented by the unit vector. For instance, a unit vector [1,0,0,0,0,0] will return 'kg' (unless the basis has been modified).'''
        str = ""
        for dim, basis_unit in zip(self.vec, _basis): # dim = how many factors of this basis unit are in self
            if dim > 0:
                str += ('.' + basis_unit) * dim
            elif dim < 0:
                str += ('/' + basis_unit) * -dim
        return str[1:] # Drop that leading "." or "/" that I decided was easier to remove later than avoid adding.
    
    def __str__(self): # TODO Control how many digits of precision are shown?
        return str(self.value) + " " + self._str_vec

    @staticmethod
    def parse_unit(str):
        '''Parse a string specification of units into Quantity. \n
        Valid specifications are separated by '.' or '*' for multiplication, and '/' for division. No spaces allowed. \n
        For instance: meters squared is written as 'm.m', kilograms times meters per second squared is 'kg.m/s/s'\n 
        raises ValueError on failure.''' # TODO Add capacity for powers (ex: m^2)?
        spec = re.split(r"([*./])", str) # Specification of units
        # Every odd element of the list spec is a unit, this iterates over the list with step size 2
        unit_names = spec[::2] # using slice indexing, start:stop:step
        # Every even element of spec is a multiply or divide operation:
        operations = spec[1::2]
        # First check that all units are known:
        for unit in unit_names: 
            if not unit in units:
                raise ValueError(f"{unit} is not a unit known to this program." + 
                                 "Please define it using the define function." + 
                        ("\nThis unit was encountered while parsing the string: " + str if unit != str else ""))
        # If they are all known units:
        # Start with the first unit, then multipy or divide the following units as specficied:
        quantity = units[unit_names[0]] # First unit
        for op, name in zip(operations, unit_names[1:]): 
            if op == '.' or op == '*': # Multiply
                quantity *= (units[name])
            else:  # op == '/'         # Divide
                quantity /= (units[name])
        return quantity

    @staticmethod
    def parse_quantity(str):
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
                raise ValueError(f"Could not convert the string {str_amount} to a number in the quantity {str}.")

         # Strip leading & trailing whitespace. The presence of whitespace is used to decide whether the
         #  quantity is a unitless number, or a whitespace-separated number and unit. Avoids getting 
         #  confused by other whitespace.
        str = str.strip() 
        # First check if there are two parts by checking for whitespace in str.
        if re.search(r"\s", str):                   # If there is an amount and unit:
            amount, unit_name = re.split("\s", str, maxsplit=1)
            # Parse the unit specification into a Quantity:
            try:
                quantity = Quantity.parse_unit(unit_name)
            except ValueError as err:
                err.add_note("This error was encountered while parsing the quantity " + str)
                raise
            # Parse the amount and multiply the Quantity by it:
            quantity.value *= parse_amount(amount)
        else:                                      # If there is only an amount or a unit.
            # Try parsing it as an amount:
            try:
                quantity = Quantity(parse_amount(str), np.array([0,0,0,0,0,0])) # Unitless Scalar
            except ValueError as err:
                err.add_note(f"Attempting to parse {str} as a unit instead.")
                # Try parsing it as a unit:
                quantity = Quantity.parse_unit(unit_name)

        return quantity

units = {
    # Basis:
    'kg': Quantity(1, np.array([1,0,0,0,0,0])), # mass, 1 kilogram
    'm':  Quantity(1, np.array([0,1,0,0,0,0])), # distance,  1 meter
    's':  Quantity(1, np.array([0,0,1,0,0,0])), # time, 1 second
    'C':  Quantity(1, np.array([0,0,0,1,0,0])), # charge, 1 coulomb
    'K':  Quantity(1, np.array([0,0,0,0,1,0])), # temperature, 1 Kelvin
    '$':  Quantity(1, np.array([0,0,0,0,0,1])), # cost, 1 dollar
    
    # Others:
    'Hz': Quantity(1, np.array([0,0,-1,0,0,0])), # frequency, 1 hertz
    'J':  Quantity(1, np.array([1,2,-2,0,0,0])), # energy, 1 joule
    'N':  Quantity(1, np.array([1,1,-2,0,0,0])), # force, 1 newton
    
    '':   Quantity(1, np.array([0,0,0,0,0,0])) # Unitless
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