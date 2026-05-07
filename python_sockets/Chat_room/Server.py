#Server side Chat room

import socket, threading

# defining constants
HOST_IP = socket.gethostbyname(socket.gethostname())
print(HOST_IP)
HOST_PORT = 65432
ENCODER = "utf-8"
BYTESIZE = 1024

# creating server socket
server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
server_socket.bind((HOST_IP, HOST_PORT))
server_socket.listen()

# creating a list to hold all info on different clients
client_socket_list = []
client_name_list = []

# defining some functions

def broadcast_message(message):
    """Send a message to all clients connected to the server"""
    for client_socket in client_socket_list:
        client_socket.send(message)

def recieve_message(client_socket):
    """Recieve message from a specific client and forward message to the broadcast function"""
    while True:
        try:
            #getting the name using socket index in socket_list
            index = client_socket_list.index(client_socket)
            name = client_name_list[index]

            # recieve message from client
            message = client_socket.recv(BYTESIZE).decode(ENCODER)
            message = f"{name}:{message}".encode(ENCODER)
            broadcast_message(message)

        except:
            """we will kick the client if error occures"""
            # getting name using socket index in name_list
            index = client_socket_list.index(client_socket)
            name = client_name_list[index]

            # removing client from client list
            client_socket_list.remove(client_socket)
            client_name_list.remove(name)

            # kicking the client
            client_socket.close()

            #broadcast that that client has left the chat
            broadcast_message(f"{name} has left the chat".encode(ENCODER))
            break


def connect_client():
    """Connect the incoming client to the server"""
    while True:
        # accept any connections
        cleint_socket, client_address = server_socket.accept()
        print(f"Connected with {client_address}...")

        #ask the client for their name
        cleint_socket.send("NAME".encode(ENCODER))
        cleint_name = cleint_socket.recv(BYTESIZE).decode(ENCODER)

        # add new client socket and client name to the appropriate lists
        client_socket_list.append(cleint_socket)
        client_name_list.append(cleint_name)

        # update server, the aforementioned client and all the client currently in the chat
        # server
        print(f"Name of the client is {cleint_name}...\n")

        # individual client
        cleint_socket.send(f"{cleint_name}, You have successfully connected to the server!".encode(ENCODER))
        
        # everybody in the room
        broadcast_message(f"{cleint_name} has just joined the chat".encode(ENCODER))

        # creating a new thread to recieve info
        recieve_thread = threading.Thread(target=recieve_message, args=(cleint_socket,))
        recieve_thread.start()

# calling the function 
print("listening...")
connect_client()