#!/usr/bin/env python3

import socket
from print_helper import str_addr
from unit_manager import parse

'''
This server provides access to the functionality of unit_manager. More details there.
'''
# Future Improvements: 
# - Remove dependence on spaces in parsing.
#       Easier midway step: leave the spaces between unit and number, but allow for no spaces between algebriac symbol and number? (What about the case 1 cm + -2 m? ) - The algebriac symbol is one char long.
# - Should I be using ValueError or TypeError when the two units have type 'str' but represent the wrong type of unit (ex: distance + mass)?
# - Add unit conversion to user specified type.
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

        while True:
            data = conn.recv(1024).decode()
            if not data: # The close notification b'' registers as False.
                print(f"Client sent close notification {data!r}") # !r is a conversion flag specifying that the data should be 
                break                                             # converted ito string using repr(), which retains more type 
                                                                  # information and is useful for debugging.
            print(f"\nReceived client message: {data!r}. \n Attempting to parse.")
            result = parse(data)
            print(f"Sending result {result!r} back to client!")
            conn.sendall(result.encode('utf-8'))

print("server exiting.")
