# Borrowed code from https://github.com/bcheikes/csc-249-p1-simple-rpc-app/blob/main/p1-simple-test-client.py 

'''Runs an interactive session with the client.'''

import socket

HOST = "127.0.0.1"  # This is the loopback address
PORT = 65432        # The port used by the server

def run_client():
    print("client starting - connecting to server at IP", HOST, "and port", PORT)
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.connect((HOST, PORT))
        print(f"connection established using client-side port {s.getsockname()[1]} at IP {s.getsockname()[0]}")
        while True:
            # get user input and talk to server until the user asks to quit
            if not talk_to_server(s):
                print("Sent close notification to server.")
                break

def talk_to_server(sock):
    msg = input("\nWhat message would you like to send to the server? (\"quit\" to close session.) \n > ")
    if msg == 'quit':
        print("Client quitting at operator request")
        return False
    elif msg.strip() == '':
        print('Please input a request.')
        return True # To restart evaluation loop.
    print(f"sending message '{msg}' to server")
    sock.sendall(msg.encode('utf-8'))
    print("message sent, waiting for reply")
    reply = sock.recv(1024).decode()
    if not reply:
        return False
    else:
        print(f"\nReceived reply '{reply}' from server\n")
        return reply

if __name__ == "__main__":
    run_client()
    print("client exiting.")