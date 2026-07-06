# Client side Chat room

import socket, threading

# Creating constants
DEST_IP = input("Enter the server IP address: ")
DEST_PORT = 65432
ENCODER = "utf-8"
BYTESIZE = 1024

#creating client socket
client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
client_socket.connect((DEST_IP, DEST_PORT))

def send_message():
    """Send message to server to be broadcast to all other clients"""
    while True:
        message = input("")
        client_socket.send(message.encode(ENCODER))

def recieve_message():
    """Recieve message from the server"""
    while True:
        try:
            # recieve message from server
            message = client_socket.recv(BYTESIZE).decode(ENCODER)

            # checks if server sent the NAME flag to ask the user for their name
            if message == "NAME":
                name = input("What is your name: ")
                client_socket.send(name.encode(ENCODER))
            else:
                print(message)
        except:
            # serious error occured, close the socket and connection
            print("error")
            client_socket.close()
            break


# create thread to run 2 functions at once
recieve_thread = threading.Thread(target=recieve_message)
send_thread = threading.Thread(target=send_message)

# start the program
recieve_thread.start()
send_thread.start()