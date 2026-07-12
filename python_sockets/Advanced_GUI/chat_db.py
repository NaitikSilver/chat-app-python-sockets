# This file handles all the PostgreSQL database stuff for the chat server.
# Only the server uses this, the client never talks to the database.
import os
import psycopg2
from psycopg2 import pool
from psycopg2.extras import DictCursor

# These are the settings we use to connect to postgres.
# I read them from env vars so u can change them without editing code,
# but they have defaults that work on a normal local install.
DB_NAME = os.environ.get("CHAT_DB_NAME", "chat_logs")
DB_USER = os.environ.get("CHAT_DB_USER", os.environ.get("USER", "postgres"))
DB_PASSWORD = os.environ.get("CHAT_DB_PASSWORD", "")
DB_HOST = os.environ.get("CHAT_DB_HOST", "localhost")
DB_PORT = os.environ.get("CHAT_DB_PORT", "5432")

# This holds our pool of connections so multiple threads dont fight over one.
# It starts as None and gets made in init_db().
_connection_pool = None


def init_db():
    """Connect to postgres and make the tables if they arent there yet."""
    global _connection_pool

    # make a little pool of connections (min 1, max 5 is plenty for a lan chat)
    _connection_pool = pool.ThreadedConnectionPool(
        1, 5,
        dbname=DB_NAME,
        user=DB_USER,
        password=DB_PASSWORD,
        host=DB_HOST,
        port=DB_PORT,
    )

    conn = _connection_pool.getconn()
    try:
        with conn.cursor() as cur:
            # users table: one row per person who has ever joined
            cur.execute("""
                CREATE TABLE IF NOT EXISTS users (
                    id SERIAL PRIMARY KEY,
                    username TEXT UNIQUE NOT NULL,
                    created_at TIMESTAMPTZ DEFAULT NOW()
                );
            """)

            # messages table: this is the actual chat log, every msg goes here
            cur.execute("""
                CREATE TABLE IF NOT EXISTS messages (
                    id SERIAL PRIMARY KEY,
                    user_id INTEGER REFERENCES users(id),
                    sender_name TEXT NOT NULL,
                    message TEXT,
                    color TEXT,
                    flag TEXT,
                    ip_address TEXT,
                    created_at TIMESTAMPTZ DEFAULT NOW()
                );
            """)
        conn.commit()
    finally:
        # always put the connection back so the pool doesnt run out
        _connection_pool.putconn(conn)


def close_db():
    """Close everything down when the server stops."""
    global _connection_pool
    if _connection_pool is not None:
        _connection_pool.closeall()
        _connection_pool = None


def _get_user_id(conn, username):
    """Find a user by name, or make a new row if they dont exist yet."""
    with conn.cursor() as cur:
        # first try to find them
        cur.execute("SELECT id FROM users WHERE username = %s;", (username,))
        row = cur.fetchone()
        if row is not None:
            return row[0]

        # not found, so add them and grab the new id
        cur.execute(
            "INSERT INTO users (username) VALUES (%s) RETURNING id;",
            (username,),
        )
        return cur.fetchone()[0]


def log_message(name, message, color, flag, ip_address=None):
    """Save one chat message into the database.

    This gets called from the server whenever a message comes in. If the
    database isnt connected it just skips it so the chat doesnt break.
    """
    if _connection_pool is None:
        # db was never set up, just ignore instead of crashing the chat
        return

    conn = _connection_pool.getconn()
    try:
        # look up (or create) the user, then store the message
        user_id = _get_user_id(conn, name)
        with conn.cursor() as cur:
            cur.execute("""
                INSERT INTO messages
                    (user_id, sender_name, message, color, flag, ip_address)
                VALUES
                    (%s, %s, %s, %s, %s, %s);
            """, (user_id, name, message, color, flag, ip_address))
        conn.commit()
    except Exception:
        # if the db messes up we rollback so nothing gets half saved
        conn.rollback()
        raise
    finally:
        _connection_pool.putconn(conn)


def recent_messages(limit=50):
    """Return the last few messages, newest first. Handy for debugging."""
    if _connection_pool is None:
        return []

    conn = _connection_pool.getconn()
    try:
        with conn.cursor(cursor_factory=DictCursor) as cur:
            cur.execute("""
                SELECT sender_name, message, color, flag, ip_address, created_at
                FROM messages
                ORDER BY created_at DESC
                LIMIT %s;
            """, (limit,))
            return [dict(row) for row in cur.fetchall()]
    finally:
        _connection_pool.putconn(conn)
