

import socket

# Not correct anymore '''Send messages in the form:  b'length msg',
#       where msg is the actual message and length is the number of bytes. The two are separated by one space.'''

HOST = "127.0.0.1"  # The server's hostname or IP address
PORT = 65432  # The port used by the server
MSG = "Hello World"

print("client starting - connecting to server at IP", HOST, "and port", PORT)
with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
    s.connect((HOST, PORT))
    print(f"connection established using client-side port {s.getsockname()[1]} at IP {s.getsockname()[0]}, sending message {MSG!r}")
    
    b_MSG = MSG.encode('utf-8')
    #s.sendall(len(b_MSG)+" "+b_MSG)
    s.sendall(b_MSG)
    print("message sent, waiting for reply")
    data = s.recv(1024)


print(f"Received response: {data!r}, [{len(data)} bytes], so sent close notification.")
print("client exiting.")
