# Client GUI Chat room
import tkinter, socket, threading, json
from tkinter import DISABLED, VERTICAL, END, NORMAL, StringVar

# Define a base window
root = tkinter.Tk()
root.title("Chat Client")
root.geometry("650x660")
root.resizable(0,0)

# Define some fonts and colors
my_font = ("Helvetica", 14)
black = "#010101"
light_green = "#1fc742"
white = "#ffffff"
red = "#ff3855"
orange = "#ffaa1d"
yellow = "#fff700"
green = "#1fc742"
blue = "#5dadec"
purple = "#9c51b6"
root.config(bg=black)

# Define socket constants
ENCODER = "utf-8"
BYTESIZE = 1024

# Class Connection
class Connection():
    """a class to store connection info"""
    def __init__(self):
        self.encoder = "utf-8"
        self.bytesize = 1024

# Define Functions
def connect(connection):
    """Connect to a server with a ip and port address"""
    my_listbox.delete(0, END)

    # Get required information from input fields
    connection.name = name_entry.get()
    connection.target_ip = ip_entry.get()
    connection.port = int(port_entry.get())
    connection.color = color.get()

    try:
        # Create a client socket
        connection.client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        connection.client_socket.connect((connection.target_ip, connection.port))

        # Recieve a incoming message packet  
        message_json = connection.client_socket.recv(connection.bytesize)
        process_message(connection, message_json)

    except:
         my_listbox.insert(0, "Connection not established...")


def disconnect(connection):
    """Disconnect with the server"""
    # Create a message packet to be sent
    message_packet = create_message("DISCONNECT", connection.name, "I am Leaving.", connection.color)
    message_json = json.dumps(message_packet)
    try:
        connection.client_socket.send(message_json.encode(connection.encoder))
    except Exception:
        pass
    try:
        connection.client_socket.close()
    except Exception:
        pass

    #Disable GUI
    gui_end()

def gui_start():
    """Start connection by updating GUI Buttons and Entries"""
    connect_button.config(state=DISABLED)
    disconnect_button.config(state=NORMAL)
    send_button.config(state=NORMAL)
    name_entry.config(state=DISABLED)
    ip_entry.config(state=DISABLED)
    port_entry.config(state=DISABLED)

    for button in color_buttons:
        button.config(state=DISABLED)
    

def gui_end():
    """End connection by updating GUI"""
    connect_button.config(state=NORMAL)
    disconnect_button.config(state=DISABLED)
    send_button.config(state=DISABLED)
    name_entry.config(state=NORMAL)
    ip_entry.config(state=NORMAL)
    port_entry.config(state=NORMAL)

    for button in color_buttons:
        button.config(state=NORMAL)


def create_message(flag, name, message, color):
    """Returns a message packet to be sent"""
    message_pack = {
        "flag":flag,
        "name":name,
        "message":message,
        "color":color
    }
    return message_pack


def process_message(connection, message_json):
    """Update message and process info"""
    message_packet = json.loads(message_json) # decode and turn into dict
    flag = message_packet["flag"]
    name = message_packet["name"]
    message = message_packet["message"]
    color = message_packet["color"]
    

    if flag == "INFO":
        # server is asking for information to verify connection
        message_packet = create_message("INFO", connection.name, "Joins the server!", connection.color)
        message_json = json.dumps(message_packet)
        connection.client_socket.send(message_json.encode(connection.encoder))

        # Enable GUI for Chat
        gui_start()

        # Create a thread to continuiesly recieve messages from server
        recieve_thread = threading.Thread(target=recieve_message, args=(connection,))
        recieve_thread.start()

    elif flag == "MESSAGE":
        # Server has sent a message so display it
        my_listbox.insert(0, f"{name} : {message}")
        my_listbox.itemconfig(0, fg=color)

    elif flag == "DISCONNECT":
        # Server is asking you to leave
        my_listbox.insert(0, f"{name}: {message}")
        my_listbox.itemconfig(0, fg=color)
        disconnect(connection)


    else: 
        my_listbox.insert(0, "ERROR processing message...")
 
def send_message(connection):
    """Send a message to the server"""
    message_packet = create_message("MESSAGE", connection.name, input_entry.get(), connection.color)
    message_json = json.dumps(message_packet)
    connection.client_socket.send(message_json.encode(connection.encoder))

    # Clear the input entry
    input_entry.delete(0, END)

def recieve_message(connection):
    """Recieve a message from the server"""
    while True:
        try:
            message_json = connection.client_socket.recv(connection.bytesize)
        except Exception:
            # Can not recieve message close connection
            my_listbox.insert(0, "Connection has been closed...")
            gui_end()
            break

        if not message_json:
            # Server closed the connection cleanly
            my_listbox.insert(0, "Connection has been closed...")
            gui_end()
            break

        try:
            process_message(connection, message_json)
        except Exception:
            my_listbox.insert(0, "ERROR processing message...")

# Define GUI Layout
# Creating frames
info_frame = tkinter.Frame(root, bg=black)
color_frame = tkinter.Frame(root, bg=black)
output_frame = tkinter.Frame(root, bg=black)
input_frame = tkinter.Frame(root, bg=black)

info_frame.pack()
color_frame.pack()
output_frame.pack()
input_frame.pack()

# Info Frame Layout
name_label = tkinter.Label(info_frame, text="Client Name", font=my_font, fg=light_green, bg=black)
name_entry = tkinter.Entry(info_frame, borderwidth=3, font=my_font)
ip_label = tkinter.Label(info_frame, text="Host IP:", font=my_font, fg=light_green, bg=black)
ip_entry = tkinter.Entry(info_frame, borderwidth=3, font=my_font)
port_label = tkinter.Label(info_frame, text="Port Num:", font=my_font, fg=light_green, bg=black)
port_entry = tkinter.Entry(info_frame, borderwidth=3, font=my_font, width=10)
connect_button = tkinter.Button(info_frame, text="Connect", font=my_font, bg=light_green, borderwidth=5, width=10, command=lambda:connect(my_connection))
disconnect_button = tkinter.Button(info_frame, text="Disconnect", font=my_font, bg=light_green, borderwidth=5, width=10, state=DISABLED, command=lambda:disconnect(my_connection))

name_label.grid(row=0, column=0, padx=2, pady=10)
name_entry.grid(row=0, column=1, padx=2, pady=10)
port_label.grid(row=0, column=2, padx=2, pady=10)
port_entry.grid(row=0, column=3, padx=2, pady=10)
ip_label.grid(row=1, column=0, padx=2, pady=5)
ip_entry.grid(row=1, column=1, padx=2, pady=5)
connect_button.grid(row=1, column=2, padx=4, pady=5)
disconnect_button.grid(row=1, column=3, padx=4, pady=5)

# Color frame layout
color = StringVar()
color.set(white)
white_button = tkinter.Radiobutton(color_frame, width=5, text="White", variable=color, value=white, bg=black, fg=light_green, font=my_font)
red_button = tkinter.Radiobutton(color_frame, width=5, text="Red", variable=color, value=red, bg=black, fg=light_green, font=my_font)
orange_button = tkinter.Radiobutton(color_frame, width=5, text="Orange", variable=color, value=orange, bg=black, fg=light_green, font=my_font)
yellow_button = tkinter.Radiobutton(color_frame, width=5, text="Yellow", variable=color, value=yellow, bg=black, fg=light_green, font=my_font)
green_button = tkinter.Radiobutton(color_frame, width=5, text="Green", variable=color, value=green, bg=black, fg=light_green, font=my_font)
blue_button = tkinter.Radiobutton(color_frame, width=5, text="Blue", variable=color, value=blue, bg=black, fg=light_green, font=my_font)
purple_button = tkinter.Radiobutton(color_frame, width=5, text="White", variable=color, value=purple, bg=black, fg=light_green, font=my_font)
color_buttons = [white_button, red_button, orange_button, yellow_button, green_button, blue_button, purple_button]

white_button.grid(row=1, column=0, padx=2)
red_button.grid(row=1, column=1, padx=2)
orange_button.grid(row=1, column=2, padx=2)
yellow_button.grid(row=1, column=3, padx=2)
green_button.grid(row=1, column=4, padx=2)
blue_button.grid(row=1, column=5, padx=2)
purple_button.grid(row=1, column=6, padx=2)


# Output frame layout
my_scrollbar = tkinter.Scrollbar(output_frame, orient=VERTICAL )
my_listbox = tkinter.Listbox(output_frame, height=20, width=55, borderwidth=3, bg=black, fg=light_green, font=my_font)
my_scrollbar.config(command=my_listbox.yview)

my_listbox.grid(row=0, column=0)
my_scrollbar.grid(row=0, column=1, sticky="NS")

# Input frame layout
input_entry = tkinter.Entry(input_frame, width=45, borderwidth=3, font=my_font)
send_button = tkinter.Button(input_frame, text="Send", borderwidth=5, width=10, font=my_font, bg=light_green, state=DISABLED, command=lambda:send_message(my_connection))
input_entry.grid(row=0, column=0, padx=5)
send_button.grid(row=0, column=1, padx=5, pady=5)

# Run the root window's mainloop() and creating connection object
my_connection = Connection()
root.mainloop()