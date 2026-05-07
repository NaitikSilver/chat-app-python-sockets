# Chat client side

import socket

# some constants
DEST_IP = socket.gethostbyname(socket.gethostname())
DEST_PORT = 54321
ENCODER = "utf-8"
BYTESIZE = 1024

# creating a client side socket and connecting to server

client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
client_socket.connect((DEST_IP, DEST_PORT))

while True:
    # recieve info from server
    message = client_socket.recv(BYTESIZE).decode(ENCODER)

    # quit if message is quit otherwise keep on recieving
    if message == "quit":
        client_socket.send("quit".encode(ENCODER))
        print("\nquiting...")
        break
    else:
        print(message)
        message = input("Message: ")
        client_socket.send(message.encode(ENCODER))


# end program
client_socket.close()