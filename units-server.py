#!/usr/bin/env python3

import socket
from print_helper import str_addr
from unit_manager import Quantity, units, re
# Importing the units dictionary seems ugly. Is there a better way?

'''
Units are case sensitve. 
Commas in numbers are ignored.
Can handle any number formats that python float() recognizes as numeric (ex: -1.23e4). I also remove commas, so 5,000 works.'''
# Future Improvements: 
# - Remove dependence on spaces in parsing.
#       Easier midway step: leave the spaces between unit and number, but allow for no spaces between algebriac symbol and number? (What about the case 1 cm + -2 m? ) - The algebriac symbol is one char long.
# - Should I be using ValueError or TypeError when the two units have type 'str' but represent the wrong type of unit (ex: distance + mass)?

# Need to add:
# * unit conversion
trace = True

def define(str):
    ''' 
    Valid definitions are in the form: "new_unit = number old_units", ex: "kJ = 1e+3 kg.m.m/s/s"  or  "cm = 0.01 m". \n
    See parse_unit for details of valid units specifications.
    Returns string message indicating success, or raises ValueError on failure.
    '''
    new_unit, definition = str.split(" = ", maxsplit=1)

    try:
        unit = Quantity.parse_quantity(definition)
    except ValueError as exc:
        exc.add_note("This error was encountered while attempting to define a new unit: " + str)
        raise

    # Run some checks:
    if new_unit in units:
        if units[new_unit] == unit: # TODO Check if it is one of the basis units!
            return "This unit already "
    else:
        units[new_unit] = unit
        return str + " added to units dictionary."
    
def total(str):
    '''Adds or subtracts a sequence of quantities with commensurable units. \n
    Valid Format: quantities separated by " + " or " - ". Whitespace is required.
    Ex: "1 cm + 2 m - 10 m"'''
    ### STEP 1: Parse into Quantities and " + " or " - " operations.
    equation = str.split(r"\s+([+-])\s+", str) # Split into a list of quantities and operations.
    # Every even element is an add or subtract operation:
    operations = equation[1::2] # using slice indexing, start:stop:step
    # Note: They will all be either "+" or "-", because that's how the split function was set up.

    # Every odd element of the equation is a quantity. 
    try:
        # map() returns a generator (lazy evaluation), I convert to list so any parsing failures will occur here rather than later.
        quantities = list(map(Quantity.parse_quantity, equation[::2]))
    except ValueError as err:
        err.add_note("This parsing failure occured while parsing the summation: " + str)
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
    return total

def product(str):
    '''Multiplies or divides a sequence of quantities. \n
    Valid Format: quantities separated by " * " or " / ". Whitespace is required.
    Cannot handle parantheses.
    Ex: "3.00e+8 m/s / 4.30e+14 Hz * 2" \n
    Great for dimensional analysis!'''
    ### STEP 1: Parse into Quantities and " * " or " / " operations.
    # Split into a list of quantities and operations:
    equation = str.split(r"\s+([*/])\s+", str) 
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
        err.add_note("This parsing failure occured while parsing the multiplication: " + str)
        raise
    
    ### STEP 2: Calculate the product.
    # Start with the first quantity, then multipy or divide the following ones.
    total = quantities[0] # First quantity
    for op, quantitiy in zip(operations, quantities[1:]): 
        if op == '+':              # Add
            total += quantitiy
        else:  # op == '-'         # Subtract
            total -= quantitiy
    return total

def parse(str):
    '''Commands must be in one of the following forms: \n
    Definition: \n "new_unit = numeric known_unit" \n
    For instance, "cm = 0.01 m", or "kJ = 1e+3 kg.m.m/s/s". Spaces are necessary.\n'''
    definition = re.fullmatch(r"(?P<new unit>\S+) = (?P<coef>[+-,e\d\.]+) (?P<known units>\S+)", str)
    if definition:
        if trace: print("requested operation: Define ", str)
        define(definition.group("new unit"), 
               definition.group("coef"),
               definition.group("known units"))
        return ""
    math = re.split(r"\s", str)
    # A string matches math_pattern if the string is in the form: 
    #         <value> <algebraic symbol> <value>, where the last two can be repeated any number of times.
    #  A value is a number optionally followed by a unit. There must be a space between number and unit.
    #  For instance: "2 * 3 m" or "3e8 m / 1 sec / 700 nm"

    # [+-,e\d\.]+ Matches a number containing digits and symbols (ex: "+1.02e-7" or "1,000"). 
    #             It also matches to invalid numbers like "-e,+". I'll handle that later using Python's float() casting method.
    # [+-,e\d\.]+(?: \S+)? Matches a number, followed by an optional unit. There must be a space between number and unit.
    # [+\-*/] Matches an algebraic symbol ("+", "-", "*", or "/").
    math_pattern = re.compile(r"[+-,e\d\.]+(?: \S+)?(?: [+\-*/] [+-,e\d\.]+(?: \S+)?)+")
    #math_pattern = re.compile(r"([+-,e\d\.]+(?: \S+)?)(?: ([+\-*/]) ([+-,e\d\.]+(?: \S+)?))+")




# _____________________________________________________________________________________________________
HOST = "127.0.0.1"  # Standard loopback interface address (localhost)
PORT = 65432  # Port to listen on (non-privileged ports are > 1023)

print("server starting.")
with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
    s.bind((HOST, PORT)) # bind to a known address (on server computer) for clients to reach out to.
    s.listen() # Enter a listening state.
    print("now listening for connections at ", str_addr(HOST, PORT))
    conn, addr = s.accept() # Block execution until a connection is made.
    with conn:
        print(f"Connected established with client {str_addr(*addr)}, using a new socket with server address: {str_addr(*conn.getsockname())}")
        # Every message must start with a length so we can know when a complete message has been sent.
        known_length = None # We haven't received the length yet.
        # Possible states:
        #                 'length': server is in the process of recieving the message length
        #                 'msg':    server knows how long the complete message is, will start processing the message as soon as it reaches that length.
        #                 '
        accum = b''
        while True:
            data = conn.recv(1024)
            if not data: # The close notification b'' registers as False.
                print(f"Client sent close notification {data!r}") # !r is a conversion flag specifying that the data should be 
                break                                             # converted ito string using repr(), which retains more type 
                                                                  # information and is useful for debugging.

            accum += data # The message can be sent in pieces. This puts them back together.
            # The message should be in the form: b'length msg', so we know when a complete message has been sent.
            if not known_length:
                if b' ' in data: # Has the client finished sending us the length (So we see a space character)?
                    # Great! Now we know how much longer to listen until we start processing the message:
                    accum = accum.lstrip() # In case the client accidentally stuck some whitespace in front. I want to be minimally nitpicky.
                    if 
                    known_length = int(accum.find)

            # Safety check: Not sure if this could actually help... But it won't get in the way of normal usage.
            if len(accum) > 1024:
                print("Message got too long. There is no reason for it to be longer than 1 KB, the client might be planning to overwhelm the server. The message is tossed.")
                accum = b''
                conn.sendall("Message got too long (> 1 KB). Message dropped, try again.")
            # Useful? bytes.isascii()
            print(f"Received client message: {data!r}, [{len(data)} bytes]")
            print(f"echoing {data!r} back to client")
            conn.sendall(data)

print("server exiting.")
