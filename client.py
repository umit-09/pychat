import socket
import threading

def receive_messages(client_socket):
    while True:
        try:
            message = client_socket.recv(1024).decode('utf-8')
            print(message)
        except Exception as e:
            print(e)
            break

def main():
    client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    client.connect(('127.0.0.1', 5555))

    action = input("Enter 'login' or 'register': ")
    client.send(bytes(action, 'utf-8'))

    if action == "login":
        username = input("Enter your username: ")
        password = input("Enter your password: ")
        client.send(bytes(username, 'utf-8'))
        client.send(bytes(password, 'utf-8'))

        response = client.recv(1024).decode('utf-8')
        print(response)

        if response == "Login successful":
            threading.Thread(target=receive_messages, args=(client,)).start()
    elif action == "register":
        username = input("Enter your desired username: ")
        password = input("Enter your desired password: ")
        client.send(bytes(username, 'utf-8'))
        client.send(bytes(password, 'utf-8'))

        response = client.recv(1024).decode('utf-8')
        print(response)

    client.close()

if __name__ == "__main__":
    main()
