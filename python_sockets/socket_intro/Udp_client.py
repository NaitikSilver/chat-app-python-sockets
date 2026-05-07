# UDP client side
import socket 

# create a UDP IPV4 socket
client_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM) 

# send some info through Udp

client_socket.sendto("Hello You!!".encode("utf-8"), 
                     (socket.gethostbyname(socket.gethostname()), 5321))