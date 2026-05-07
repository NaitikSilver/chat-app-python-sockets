#TCP server side

import socket

# create a server side socket using IPV4 (AF_INET) and TCP (SOCK_STREAM)
server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

# get IP address dynamically
# print(socket.gethostname()) # hostname
# print(socket.gethostbyname(socket.gethostname()))

# bind the socket to a tuple
server_socket.bind((socket.gethostbyname(socket.gethostname()), 54321))

# listen forever for any connections
server_socket.listen()

while True:
    # accept all connections and store info
    client_socket, client_address = server_socket.accept()
    # print(type(client_socket))
    # print(client_socket)  
    # print(type(client_address))
    # print(client_address)

    # send a message to the client that connected
    client_socket.send("you are connected".encode("utf-8"))

    # close socket
    server_socket.close()
    break
