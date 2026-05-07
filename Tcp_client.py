# TCP client side

import socket

# create a client side IPV4 socket (AF_INET) and TCP (SOCK_STREAM)
client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

# connect socket to already made server socket at a given IP address and port
client_socket.connect((socket.gethostbyname(socket.gethostname()), 54321))

# recieving a message from server, make sure to specify how many max bytes the socket should expect (1024 for now)
message = client_socket.recv(1024)
message = message.decode("utf-8")
print(message)

# close client socket
client_socket.close()