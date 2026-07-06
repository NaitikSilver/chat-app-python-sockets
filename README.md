# chat-app-python-sockets
A chat app made in python with full client side and server side implementation. Done using threading, sockets.

## Running the chatroom (Advanced_GUI)
The complete chatroom lives in `python_sockets/Advanced_GUI/`.

### Start the server (on your computer)
1. Run `python_sockets/Advanced_GUI/Server_GUI.py`
2. Enter a port (e.g. `65432`) and click **Start Server**
3. The server window shows your LAN IP (e.g. `192.168.1.5:65432`) — share it with your friends

### Connect as a client (your friends)
1. Run `python_sockets/Advanced_GUI/Client_GUI.py`
2. Enter your name, the server's IP, and the same port
3. Click **Connect**

### Requirements
- Everyone must be on the same WiFi network
- The network must allow device-to-device traffic (guest/corporate WiFi often blocks this — use a personal hotspot or home router instead)
- Python 3 with `tkinter` (on macOS install via `brew install python-tk`)
- Allow Python through the firewall when prompted

## Previous progress
Earlier iterations are kept in `python_sockets/archive/` to document how this project was built up:
- `socket_intro/` — intro TCP/UDP socket scripts
- `Chat_room/` — command-line chat room
- `Basic_GUI_chat_room/` — first GUI version

## To do
- finish implementing SQL so we can query for chat data and do analysis
- fix any bugs or gui scaling problems
