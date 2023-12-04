import socket
import threading
import sqlite3

DATABASE_FILE = "chat_database.db"

def create_database():
    conn = sqlite3.connect(DATABASE_FILE)
    cursor = conn.cursor()
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT NOT NULL,
            password TEXT NOT NULL
        )
    ''')
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS messages (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            sender TEXT NOT NULL,
            receiver TEXT NOT NULL,
            message TEXT NOT NULL
        )
    ''')
    conn.commit()
    conn.close()

def register_user(username, password):
    conn = sqlite3.connect(DATABASE_FILE)
    cursor = conn.cursor()
    cursor.execute("INSERT INTO users (username, password) VALUES (?, ?)", (username, password))
    conn.commit()
    conn.close()

def login_user(username, password):
    conn = sqlite3.connect(DATABASE_FILE)
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM users WHERE username=? AND password=?", (username, password))
    user = cursor.fetchone()
    conn.close()
    return user

def save_message(sender, receiver, message):
    conn = sqlite3.connect(DATABASE_FILE)
    cursor = conn.cursor()
    cursor.execute("INSERT INTO messages (sender, receiver, message) VALUES (?, ?, ?)", (sender, receiver, message))
    conn.commit()
    conn.close()

def get_messages(user1, user2):
    conn = sqlite3.connect(DATABASE_FILE)
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM messages WHERE (sender=? AND receiver=?) OR (sender=? AND receiver=?)",
                   (user1, user2, user2, user1))
    messages = cursor.fetchall()
    conn.close()
    return messages

def register_new_user(client_socket):
    username = client_socket.recv(1024).decode('utf-8')
    password = client_socket.recv(1024).decode('utf-8')

    conn = sqlite3.connect(DATABASE_FILE)
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM users WHERE username=?", (username,))
    existing_user = cursor.fetchone()

    if existing_user:
        client_socket.send(bytes("Username already taken. Please choose a different username.", 'utf-8'))
    else:
        register_user(username, password)
        client_socket.send(bytes("Registration successful. You can now log in.", 'utf-8'))

    conn.close()

def handle_client(client_socket, username, lock):
    while True:
        try:
            message = client_socket.recv(1024).decode('utf-8')
            if message == 'exit':
                break
            receiver, msg_content = message.split(':', 1)
            
            with lock:
                save_message(username, receiver, msg_content)
                print(f"Message from {username} to {receiver}: {msg_content}")

        except Exception as e:
            print(e)
            break

    client_socket.close()

def main():
    create_database()

    server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server.bind(('127.0.0.1', 5555))
    server.listen(5)

    while True:
        client_socket, addr = server.accept()
        print(f"Accepted connection from {addr}")

        action = client_socket.recv(1024).decode('utf-8')

        if action == "login":
            username = client_socket.recv(1024).decode('utf-8')
            password = client_socket.recv(1024).decode('utf-8')

            user = login_user(username, password)

            if user:
                client_socket.send(bytes("Login successful", 'utf-8'))
                threading.Thread(target=handle_client, args=(client_socket, username)).start()
            else:
                client_socket.send(bytes("Login failed", 'utf-8'))
                client_socket.close()
        elif action == "register":
            register_new_user(client_socket)
            client_socket.close()

if __name__ == "__main__":
    main()
