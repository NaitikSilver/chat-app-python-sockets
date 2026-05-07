# Chat server side

import socket

# define some constants

HOST_IP = socket.gethostbyname(socket.gethostname())
HOST_PORT = 54321
ENCODER = "utf-8"
BYTESIZE = 1024

# Create a server side IPV4 TCP socket and binding

server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
server_socket.bind((HOST_IP, HOST_PORT))

# accept any incoming connections and user feedback
server_socket.listen()
print("Server is up and running...\n")

client_socket, client_address = server_socket.accept()
client_socket.send("You are connected to server...\n".encode(ENCODER))

# send and recieve messages
while True:
    # recieve info from client socket
    message = client_socket.recv(BYTESIZE).decode(ENCODER)

    if message == "quit":
        client_socket.send("quit".encode(ENCODER))
        print("\nquiting")
        break
    else: 
        print(message)
        message = input("Message: ")  
        client_socket.send(message.encode(ENCODER))

# ending socket
server_socket.close()
