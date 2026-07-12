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
- PostgreSQL running locally (the server logs every message to it)
- Allow Python through the firewall when prompted

### PostgreSQL setup (one time)
The server stores all chat logs in a local PostgreSQL database. Only the server
talks to the database — clients never do.

1. Install PostgreSQL (on macOS, [Postgres.app](https://postgresapp.com/) is easy)
2. Make sure the server is running (`pg_isready` should say `accepting connections`)
3. Create the database once:
   ```
   createdb chat_logs
   ```
4. Install the Python driver:
   ```
   pip install -r requirements.txt
   ```

That's it. When you click **Start Server**, it connects to the `chat_logs`
database and creates the tables automatically. The server window shows
`DB connected` (or a `DB failed: ...` message if something went wrong).

If your PostgreSQL uses different connection details, set them with env vars
before launching the server:
```
export CHAT_DB_NAME=chat_logs
export CHAT_DB_USER=your_user
export CHAT_DB_PASSWORD=your_password
export CHAT_DB_HOST=localhost
export CHAT_DB_PORT=5432
```

### Querying the chat logs
Everything is stored in two tables: `users` (one row per person) and `messages`
(the actual chat log). Some useful queries:

```
# last 20 messages
psql chat_logs -c "SELECT created_at, sender_name, message FROM messages ORDER BY created_at DESC LIMIT 20;"

# who has sent the most messages
psql chat_logs -c "SELECT sender_name, COUNT(*) FROM messages WHERE flag='MESSAGE' GROUP BY sender_name ORDER BY count DESC;"

# everything a specific person said
psql chat_logs -c "SELECT created_at, message FROM messages WHERE sender_name='alex' ORDER BY created_at;"
```

## Previous progress
Earlier iterations are kept in `python_sockets/archive/` to document how this project was built up:
- `socket_intro/` — intro TCP/UDP socket scripts
- `Chat_room/` — command-line chat room
- `Basic_GUI_chat_room/` — first GUI version

## To do
- finish implementing SQL so we can query for chat data and do analysis (DONE: chat logs are now stored in PostgreSQL, see above)
- fix any bugs or gui scaling problems
