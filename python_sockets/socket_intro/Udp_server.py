# UDP server side
import socket

# create a server side socket using IPV4 (AF_INET) and UDP (SOCK_DGRAM)
server_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

# bind our socket to a Ip address and port address
server_socket.bind((socket.gethostbyname(socket.gethostname()), 54321))

# Udp is connections so no need to listen
message, address = server_socket.recvfrom(1024)
print(message.decode("utf-8"))
print(address)