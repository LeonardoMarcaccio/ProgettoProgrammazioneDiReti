import socket
import threading

# Impostazioni del server
HOST = '127.0.0.1'
PORT = 12345

# Lista dei client connessi
clients = []
usernames = []

# Funzione per gestire i messaggi ricevuti dai client
def broadcast(message, sender_socket):
    for client in clients:
        if client != sender_socket:
            try:
                client.send(message)
            except:
                # Se inviare il messaggio fallisce, rimuovi il client dalla lista
                client.close()
                clients.remove(client)

# Funzione per gestire i client
def handle_client(client_socket):
    while True:
        try:
            message = client_socket.recv(1024)
            if not message:
                break
            broadcast(message, client_socket)
        except:
            clients.remove(client_socket)
            client_socket.close()
            break

# Funzione principale del server
def server():
    server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server_socket.bind((HOST, PORT))
    server_socket.listen()

    print(f"Server avviato su {HOST}:{PORT}")

    while True:
        client_socket, client_address = server_socket.accept()
        print(f"Connessione accettata da {client_address}")

        clients.append(client_socket)

        # Avvia un nuovo thread per gestire il client
        thread = threading.Thread(target=handle_client, args=(client_socket,))
        thread.start()

if __name__ == "__main__":
    server()
