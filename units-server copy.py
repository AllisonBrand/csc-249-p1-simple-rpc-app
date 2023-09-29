#!/usr/bin/env python3

import socket
from print_helper import str_addr
from unit_manager import parse

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
        # # Every message must start with a length so we can know when a complete message has been sent.
        # known_length = None # We haven't received the length yet.
        # # Possible states:
        # #                 'length': server is in the process of recieving the message length
        # #                 'msg':    server knows how long the complete message is, will start processing the message as soon as it reaches that length.
        # #                 '
        # accum = b''
        while True:
            data = conn.recv(1024).decode()
            if not data: # The close notification b'' registers as False.
                print(f"Client sent close notification {data!r}") # !r is a conversion flag specifying that the data should be 
                break                                             # converted ito string using repr(), which retains more type 
                                                                  # information and is useful for debugging.
            print(f"Received client message: {data!r}. \n Attempting to parse.")
            result = parse(data)
            print(f"Sending result {result!r} back to client!")
            conn.sendall(result.encode('utf-8'))
            ## accum += data # The message can be sent in pieces. This puts them back together.
            ## # The message should be in the form: b'length msg', so we know when a complete message has been sent.
            ## if not known_length:
            ##     if b' ' in data: # Has the client finished sending us the length (So we see a space character)?
            ##         # Great! Now we know how much longer to listen until we start processing the message:
            ##         accum = accum.lstrip() # In case the client accidentally stuck some whitespace in front. I want to be minimally nitpicky.
            ##         if 
            ##         known_length = int(accum.find)

            ## Safety check: Not sure if this could actually help... But it won't get in the way of normal usage.
            ##if len(accum) > 1024:
            ##    print("Message got too long. There is no reason for it to be longer than 1 KB, the client might be planning to overwhelm the server. The message is tossed.")
            ##    accum = b''
            ##    conn.sendall("Message got too long (> 1 KB). Message dropped, try again.")
            ### Useful? bytes.isascii()

print("server exiting.")


# Comments removed from unit_manger before submission.

# import sys
# sys.path.insert(1, 'c:/users/allis/anaconda3')
# import numpy as np
# The lists representing unit vectors for a Quantity used to be numpy arrays (they have fized size and make for pretty code when I add or subtract them).
# I was getting ModuleNotFoundError: No module named 'numpy' when I tried to import it, despite conda list numpy saying it was there. 
# I tried messing with sys.path, but got other errors. I tried updating it: nothing. I tried uninstalling and reinstalling: nothing. 
# I tried deactivating the conda environment and installing numpy from there. Still nothing. 