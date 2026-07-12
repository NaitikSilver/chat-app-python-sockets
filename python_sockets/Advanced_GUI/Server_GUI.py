# Server GUI Chat room (admin)
import tkinter, socket, threading, json
from tkinter import DISABLED, VERTICAL, END, NORMAL
import chat_db  # this is our postgres logging module (only the server uses it)

# Define window
root = tkinter.Tk()
root.title("Chat Server")
root.geometry("600x600")
root.resizable(0,0)

# Define fonts and colors
my_font = ("SimSun", 14)
black = "#010101"
light_green = "#1fc742"
root.config(bg=black)

def get_lan_ip():
    """Return the real LAN IP of this machine.

    Uses the UDP-connect trick: connecting a UDP socket to a public IP
    assigns the local endpoint that would be used to reach the internet,
    without actually sending any packets. This reliably returns the real
    LAN IP (e.g. 192.168.x.x) on macOS/Windows/Linux, unlike
    socket.gethostbyname(socket.gethostname()) which often returns
    127.0.0.1 or a Bonjour/internal address on macOS.
    """
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    try:
        s.connect(("8.8.8.8", 80))
        return s.getsockname()[0]
    except Exception:
        return "127.0.0.1"
    finally:
        s.close()


# Creating a class to hold sockets and other info
class Connection():
    """will store a connection"""
    def __init__(self):
        self.host_ip = "0.0.0.0"
        self.lan_ip = get_lan_ip()
        self.encoder = "utf-8"
        self.bytesize = 1024

        self.client_sockets = []
        self.client_ips = []
        self.client_names = []
        self.banned_ips = []
        self.lock = threading.Lock()


# Define functions
def start_server(connection):
    """Start the server on a given port address"""
    # get port number to run the server and attach connection object
    connection.port = int(port_entry.get())

    # creating server socket
    connection.server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    connection.server_socket.bind((connection.host_ip, connection.port))
    connection.server_socket.listen()

    # hook up the postgres database so chat messages get saved
    try:
        chat_db.init_db()
        db_status = "DB connected"
    except Exception as e:
        db_status = f"DB failed: {e}"
        history_listbox.insert(0, db_status)

    # Update GUI
    history_listbox.delete(0, END)
    history_listbox.insert(0, f"Server started on {connection.lan_ip}:{connection.port} ({db_status})")
    end_button.config(state=NORMAL)
    self_broadcast_button.config(state=NORMAL)
    message_button.config(state=NORMAL)
    kick_button.config(state=NORMAL)
    ban_button.config(state=NORMAL)
    start_button.config(state=DISABLED)

    # Create a thread to continuously listen for connection from incoming clients
    connect_thread = threading.Thread(target=connect_client, args=(connection,))
    connect_thread.start()


def end_server(connection):
    """End the server"""
    message_packet = create_message("DISCONNECT", "Admin (broadcast)", "Server is  closing...", light_green)
    message_json = json.dumps(message_packet)
    broadcast_message(connection, message_json.encode(connection.encoder))

    # Update GUI
    history_listbox.insert(0, f"Server closing on port {connection.port}")
    end_button.config(state=DISABLED)
    self_broadcast_button.config(state=DISABLED)
    message_button.config(state=DISABLED)
    kick_button.config(state=DISABLED)
    ban_button.config(state=DISABLED)
    start_button.config(state=NORMAL)

    # Close all client sockets and clear shared state safely
    with connection.lock:
        sockets = list(connection.client_sockets)
        connection.client_sockets.clear()
        connection.client_ips.clear()
        connection.client_names.clear()
        client_listbox.delete(0, END)

    for client_sock in sockets:
        try:
            client_sock.close()
        except Exception:
            pass

    # Close server socket
    try:
        connection.server_socket.close()
    except Exception:
        pass

    # Shut down the database connection pool since we are done logging
    try:
        chat_db.close_db()
    except Exception:
        pass

def connect_client(connection):
    """Connection client to the server"""
    while True:
        try:
            client_socket, client_address = connection.server_socket.accept()
        except Exception:
            break

        try:
            # check if the ip that is being connected to is banned
            with connection.lock:
                is_banned = client_address[0] in connection.banned_ips

            if is_banned:
                message_packet = create_message("DISCONNECT", "Admin (private)", "You have been banned...", light_green)
                message_json = json.dumps(message_packet)
                try:
                    client_socket.send(message_json.encode(connection.encoder))
                except Exception:
                    pass
                client_socket.close()
            else:
                # Send a message packet to recieve client info
                message_packet = create_message("INFO", "Admin (private)", "Please send your name", light_green)
                message_json = json.dumps(message_packet)
                client_socket.send(message_json.encode(connection.encoder))

                # Wait for confirmation message to be sent
                message_json = client_socket.recv(connection.bytesize)
                if not message_json:
                    client_socket.close()
                else:
                    process_message(connection, message_json, client_socket, client_address)
        except Exception:
            # A bad handshake for one client must not crash the accept loop
            try:
                client_socket.close()
            except Exception:
                pass

def create_message(flag, name, message, color):
    """Return a message packet to be sent"""
    message_packet = {
        "flag": flag, 
        "name": name,
        "message":message,
        "color":color
    }
    return message_packet

def log_to_db(name, message, color, flag, ip_address=None):
    """Save a message to the postgres db so we can look at chat history later.

    Wrapped in try/except so if the db has a problem the chat still works fine.
    """
    try:
        chat_db.log_message(name, message, color, flag, ip_address)
    except Exception as e:
        history_listbox.insert(0, f"DB error: {e}")

def _ip_for_socket(connection, client_socket):
    """Find the ip address for a given client socket (or None if not found)."""
    with connection.lock:
        if client_socket in connection.client_sockets:
            index = connection.client_sockets.index(client_socket)
            return connection.client_ips[index]
    return None

def process_message(connection, message_json, client_socket, client_address=(0,0)):
    """Update server info based on packet flag"""
    message_packet = json.loads(message_json) # decode and turn into dict
    flag = message_packet["flag"]
    name = message_packet["name"]
    message = message_packet["message"]
    color = message_packet["color"]

    if flag == "INFO":
        # add the new client information to appropriate lists (atomically)
        with connection.lock:
            connection.client_sockets.append(client_socket)
            connection.client_ips.append(client_address[0])
            connection.client_names.append(name)
            client_listbox.insert(END, f"Name: {name}      IP Addr: {client_address[0]}")

        # Broadcast the new client joining
        message_packet = create_message("MESSAGE", "Admin (broadcast)", f"{name} has joined the chat!", light_green)
        message_json = json.dumps(message_packet)
        broadcast_message(connection, message_json.encode(connection.encoder))

        # log the join event to the database
        log_to_db("Admin (broadcast)", f"{name} has joined the chat!", light_green, "INFO", ip_address=client_address[0])

        # A client has been established, start a thread to listen for messages from them constantly
        recieve_thread = threading.Thread(target=recieve_message, args=(connection, client_socket,))
        recieve_thread.start()

    elif flag == "MESSAGE":
        # Broadcast the given message
        broadcast_message(connection, message_json)

        # Update server UI
        history_listbox.insert(0, f"{name}: {message}")
        history_listbox.itemconfig(0, fg=color)

        # save the actual chat message to the db (look up the senders ip too)
        sender_ip = _ip_for_socket(connection, client_socket)
        log_to_db(name, message, color, "MESSAGE", ip_address=sender_ip)

    elif flag == "DISCONNECT":
        # Close and remove client_socket (and notify everyone)
        _drop_client(connection, client_socket, name)

    else:
        # catch for errors 
        history_listbox.insert(0, "ERROR processing message...")

def broadcast_message(connection, message_json):
    """Broadcast message to all connected client.

    A dropped client mid-broadcast no longer aborts the loop for everyone else:
    we snapshot the socket list under the lock, send to each outside the lock,
    and cleanly remove any socket that fails.
    """
    with connection.lock:
        sockets = list(connection.client_sockets)

    dead = []
    for client_sock in sockets:
        try:
            client_sock.send(message_json)
        except Exception:
            dead.append(client_sock)

    for client_sock in dead:
        _drop_client(connection, client_sock)


def _drop_client(connection, client_socket, name=None):
    """Remove a client from shared state and notify everyone they left.

    Safe to call multiple times for the same socket (idempotent). Used by the
    DISCONNECT handler, by recieve_message on a hard drop, and by
    broadcast_message when a send fails.
    """
    with connection.lock:
        if client_socket not in connection.client_sockets:
            return
        index = connection.client_sockets.index(client_socket)
        if name is None:
            name = connection.client_names[index]
        # grab the ip before we remove them, so we can log who left
        left_ip = connection.client_ips[index]
        connection.client_sockets.pop(index)
        connection.client_ips.pop(index)
        connection.client_names.pop(index)
        client_listbox.delete(index)

    try:
        client_socket.close()
    except Exception:
        pass

    # Alert all remaining users that a client has left the chat
    message_pack = create_message("MESSAGE", "Admin (broadcast)", f"{name} has left the chat...", light_green)
    message_json = json.dumps(message_pack)
    broadcast_message(connection, message_json.encode(connection.encoder))

    # Update the server UI
    history_listbox.insert(0, f"Admin (broadcast): {name} has left the server...")

    # log the leave event to the database
    log_to_db("Admin (broadcast)", f"{name} has left the chat...", light_green, "DISCONNECT", ip_address=left_ip)


def recieve_message(connection, client_socket):
    """Recieve message from client"""
    while True:
        try:
            message_json = client_socket.recv(connection.bytesize)
        except Exception:
            # Network error -> client is gone, clean up and stop listening
            _drop_client(connection, client_socket)
            break

        if not message_json:
            # recv returned b'' -> peer closed the connection cleanly
            _drop_client(connection, client_socket)
            break

        try:
            process_message(connection, message_json, client_socket)
        except Exception:
            # A malformed packet should not kill the listener or the server
            history_listbox.insert(0, "ERROR processing message...")

def self_broadcast(connection):
    """Broadcast a special admin message to all clients"""
    # Create a message packet
    message_packet = create_message("MESSAGE", "Admine (broadcast)", input_entry.get(), light_green)
    message_json = json.dumps(message_packet)
    broadcast_message(connection, message_json.encode(connection.encoder))

    # log the admin broadcast to the db
    log_to_db("Admine (broadcast)", input_entry.get(), light_green, "MESSAGE")

    # Clear input entry
    input_entry.delete(0, END)

def private_message(connection):
    """Send a private message to a specific client"""
    try:
        index = client_listbox.curselection()[0]
    except Exception:
        return

    with connection.lock:
        if index >= len(connection.client_sockets):
            return
        client_socket = connection.client_sockets[index]
        client_ip = connection.client_ips[index]

    # Create a message packet and send
    message_packet = create_message("MESSAGE", "Admin (private)", input_entry.get(), light_green)
    message_json = json.dumps(message_packet)
    try:
        client_socket.send(message_json.encode(connection.encoder))
    except Exception:
        _drop_client(connection, client_socket)
        return

    # log the private message to the db (with the target ip)
    log_to_db("Admin (private)", input_entry.get(), light_green, "MESSAGE", ip_address=client_ip)

    # Clear input entry
    input_entry.delete(0, END)


def kick_client(connection):
    """Kick a specific client from Chat"""
    try:
        index = client_listbox.curselection()[0]
    except Exception:
        return

    with connection.lock:
        if index >= len(connection.client_sockets):
            return
        client_socket = connection.client_sockets[index]

    # Create the message packet
    message_packet = create_message("DISCONNECT", "Admin (private)", "You have been kicked...", light_green)
    message_json = json.dumps(message_packet)
    try:
        client_socket.send(message_json.encode(connection.encoder))
    except Exception:
        _drop_client(connection, client_socket)


def ban_client(connection):
    """Ban a client based on ip address"""
    try:
        index = client_listbox.curselection()[0]
    except Exception:
        return

    with connection.lock:
        if index >= len(connection.client_sockets):
            return
        client_socket = connection.client_sockets[index]
        client_ip = connection.client_ips[index]
        connection.banned_ips.append(client_ip)

    # Create the message packet
    message_packet = create_message("DISCONNECT", "Admin (private)", "You have been banned...", light_green)
    message_json = json.dumps(message_packet)
    try:
        client_socket.send(message_json.encode(connection.encoder))
    except Exception:
        _drop_client(connection, client_socket)


# Define GUI Layout
# Creating the basic frams
connection_frame = tkinter.Frame(root, bg=black)
history_frame = tkinter.Frame(root, bg=black)
client_frame = tkinter.Frame(root, bg=black)
message_frame = tkinter.Frame(root, bg=black)
admin_frame = tkinter.Frame(root, bg=black)

connection_frame.pack(pady=5)
history_frame.pack()
client_frame.pack(pady=5)
message_frame.pack()
admin_frame.pack()

# Connection Frame Layout
port_label = tkinter.Label(connection_frame, text="Port Number:", font=my_font, bg=black, fg=light_green)
port_entry = tkinter.Entry(connection_frame, width=10,  borderwidth=3, font=my_font)
start_button = tkinter.Button(connection_frame, text="Start Server", borderwidth=5, width=15, font=my_font, bg=light_green, command=lambda:start_server(my_connection))
end_button = tkinter.Button(connection_frame, text="End Server", borderwidth=5, width=15, font=my_font, bg=light_green, state=DISABLED, command=lambda:end_server(my_connection)) 

port_label.grid(row=0, column=0, padx=2, pady=10)
port_entry.grid(row=0, column=1, padx=2, pady=10)
start_button.grid(row=0, column=2, padx=5, pady=10)
end_button.grid(row=0, column=3, padx=5, pady=10)

# History Frame Layout
history_scrollbar = tkinter.Scrollbar(history_frame, orient=VERTICAL)
history_listbox = tkinter.Listbox(history_frame, height=10, width=55, borderwidth=3, font=my_font, bg=black, fg=light_green, yscrollcommand=history_scrollbar.set)
history_scrollbar.config(command=history_listbox.yview)

history_listbox.grid(row=0, column=0)
history_listbox.grid(row=0, column=1, sticky="NS")

# Client Frame Layout
client_scrollbar = tkinter.Scrollbar(client_frame, orient=VERTICAL)
client_listbox = tkinter.Listbox(client_frame, height=10, width=55, borderwidth=3, font=my_font, bg=black, fg=light_green, yscrollcommand=client_scrollbar.set)
client_scrollbar.config(command=client_listbox.yview)

client_listbox.grid(row=0, column=0)
client_listbox.grid(row=0, column=1, sticky="NS")

# Message Frame Layout
input_entry = tkinter.Entry(message_frame, width=40,  borderwidth=3, font=my_font)
self_broadcast_button = tkinter.Button(message_frame, text="Broadcast", width=13, borderwidth=5, font=my_font, bg=light_green, state=DISABLED, command=lambda:self_broadcast(my_connection))

input_entry.grid(row=0, column=0, padx=5, pady=5)
self_broadcast_button.grid(row=0, column=1, padx=5, pady=5)

# Admin Frame Layout
message_button = tkinter.Button(admin_frame, text="PM", borderwidth=5, width=15, font=my_font, bg=light_green, state=DISABLED, command=lambda:private_message(my_connection))
kick_button = tkinter.Button(admin_frame, text="Kick", borderwidth=5, width=15, font=my_font, bg=light_green, state=DISABLED, command=lambda:kick_client(my_connection))
ban_button = tkinter.Button(admin_frame, text="Ban", borderwidth=5, width=15, font=my_font, bg=light_green, state=DISABLED, command=lambda:ban_client(my_connection))

message_button.grid(row=0, column=0, padx=5, pady=5)
kick_button.grid(row=0, column=1, padx=5, pady=5)
ban_button.grid(row=0, column=2, padx=5, pady=5)

# Run the root window and create Connection object
my_connection = Connection()
root.mainloop() 
