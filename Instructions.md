# CSC 249 – Project 1 – Simple RPC Client-Server App

Building distributed network applications in Python is fun!

For your first experience building a simple network application in Python, you will start with Python code taken from an online tutorial: _Socket Programming in Python (Guide)_ by Nathan Jennings, available online at https://realpython.com/python-sockets/. 

The Jennings tutorial opens with the design and implementation of an “Echo Client and Server.” In this simple application, the server is launched first on the local machine and makes calls to the Python sockets library to wait for a new connection. In a separate process on the same machine, the client establishes a network connection to the server and sends a single text message, “Hello, world” (you knew that was coming, right?) The server receives this message and sends it right back (“echoes”) to the client. The server exits after echoing the message, and the client exits after receiving the echo message. You are strongly encouraged to study the code, try running it, and make sure you understand how it works. I’ve placed (a slightly modified version of) the code in this Git repo [https://github.com/bcheikes/csc249-p1-simple-rpc-app], which you are welcome to clone.

The echo application makes for a fine capability demonstration but isn’t very interesting. For this exercise, I want you to build something more interesting so you can get some practical experience with encoding, transmitting, receiving, decoding, and processing more complex messages.

What you will do is extend the echo-server into a “remote procedure call” (RPC) server. Conceptually, a RPC server accepts incoming network requests to perform some kind of computation, typically expressed as a “requested operation” along with one or more arguments. For example, a “basic math” RPC server could process one of four requested operations: add, subtract, multiply, or divide. Such a server might accept two integer arguments and reply to the client with a message containing the result of adding, subtracting, multiplying or dividing the arguments.

The main challenges for you in this exercise will be:

* Coming up with a creative set of requested operations that your RPC server will process.
* Designing a method for encoding client requests and arguments into a Python bytes object for transmission.
* Designing a method for decoding client requests on the server, processing them, and returning a response.
* Building in appropriate error handling.

Like the echo application, your server should terminate after successfully processing a client message, and your client should terminate after successfully receiving a response to its request.

## Design Requirements

Your server must be able to process at least two different requested operations (i.e., it must understand at least two "verbs"). This means that an indication of the requested operation needs to be passed from client to server.

* Each requested operation must take at least two arguments ("nouns"). This means that you need to encode each argument in the request message, with an indication of where one argument “ends” and the next one “begins”.
* Your client must obtain the desired operation and its arguments either interactively from keyboard input or from the terminal command line.
* As they run, the client and the server applications must generate tracing messages that document significant program milestones, e.g., when connections are made, when messages and sent and received, and what was sent and what was received. (Good examples of tracing messages can be found in the sample code provided.)
* The client and server should be designed to anticipate and gracefully handle reasonable errors which could occur at either end of the communication channel. For example, the client should attempt to prevent malformed requests to the server, and the server should avoid crashing if it receives a malformed request. Remember, in the real world there is no guarantee that your server will only have to deal with communications from your (presumably friendly) client!
* Source code of your client and server must be appropriately documented. Comments should be sufficient to allow a third party to understand your code, run it, and confirm that it works.

## Deliverables

Your work on this project must be submitted for grading by **Wednesday Sep 27th at 11:59PM**. Extensions may be obtained by following the late submission policy [https://drive.google.com/file/d/16DYyy_WhaoNdPRo8foJcQhUzPsh3_jG6/view?usp=drive_link].

All work must be submitted in Gradescope. (Link is posted in Moodle.)

You must submit these work products:

1. Source code for your client and server. Ideally, this will be a link to your public Git code repo. (Use of Git is encouraged but not required; you may instead upload your individual Python files directly to Gradescope without involving Git.)
2. A document with a written description of your client-server message format (that is, a description of all implemented client and server messages, and how the various components of each message are represented). This document must also briefly summarize what your client-server application does, and provide examples of expected output for all implemented RPC operations. Your goal in writing this document should be to convey enough information in enough detail to allow a competent programmer **without access to your source code** to write either a new client that communicates properly with your server, or a new server that communicates properly with your client. This document should include at least five sections: Overview of Application, Client->Server Message Format, Server->Client Message Format, Example Output, Acknowledgments.
3. A command-line trace showing the client and server in operation. 

## Example of Client and Server Command Line Traces

Below we illustrate command line traces for a client-server application in which the server response to requests to perform simple math operations.

### Client Trace

% python3 simple-math-client.py add 1 3 5

client starting - connecting to math server at IP 127.0.0.1 and port 65432

connection established, sending request '+1:3:5'

message sent, waiting for reply

Received reply: '1+3+5=9' [7 bytes]

client is done!

### Server Trace
% python3 simple-math-server.py

basic math server starting - listening for connections at IP 127.0.0.1 and port 65432

connected established with ('127.0.0.1', 53740)

received client message: '+1:3:5' [6 bytes]

requested operation is addition

request includes 3 arguments: 1 3 5

result of operation: 9

sending result message '1+3+5=9' back to client

server is done!

## Teamwork Policy

**For this project, all work must be performed individually – no team submissions will be allowed**. You are free to collaborate and exchange ideas, but each student must submit their own original work. To the extent you obtain ideas and feedback from other students, you should give them proper credit in the Acknowledgments section of your specification document. For example, "Jane Austen helped me think through the different messages that my ATM server might need to be able to handle", "Sophia Smith helped me understand the purpose of the htons() function". During class we will discuss the "rules of engagement" - what is ok and not ok in terms of collaboration with others. The key objective of this exercise is to give each student the opportunity to work with the Python sockets library, then design and implement a simple message protocol.

## Getting Help

There is plenty of self-help material out there to help you understand socket programming in Python. 

* Socket Programming in Python (Guide) by Nathan Jennings [https://realpython.com/python-sockets/]
* Python sockets library documentation [https://docs.python.org/3/library/socket.html]
* LinkedIn Learning (Smith College offers free access) – search “python sockets”
* Python sockets tutorials on YouTube [for example, try https://www.youtube.com/watch?v=3QiPPX-KeSc]. There are many!
* Slack messages in the #questions channel. Students are encouraged to help each other out – this is part of what “participation and engagement” means in the overall course grading rubric.
* Instructor and TA office hours!

## Grading Rubric

Your work on this project will be graded on a five-point scale. Fractional points may be awarded.

_0 pts:_ No deliverables were received by the due date or requested extension date.

_1 pt:_ Incomplete deliverables were received by the due date or extension date.

_2 pts:_ Required deliverables were received but are deficient in various ways (e.g., incomplete documentation, code doesn’t run)

_3 pts:_ Complete and adequate deliverables. Code runs but is deficient in various ways.

_4 pts:_ Code runs and does most but not all of what is required.

_5 pts:_ Nailed it. Complete deliverables, code runs and does what is required.
