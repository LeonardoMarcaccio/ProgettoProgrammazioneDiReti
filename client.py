import socket
import threading

# Impostazioni del client
HOST = '127.0.0.1'
PORT = 12345

# Funzione per ricevere messaggi dal server
def receive_messages(client_socket):
    while True:
        try:
            message = client_socket.recv(1024).decode('utf-8')
            if message:
                print(message)
            else:
                break
        except:
            print("Errore nella ricezione del messaggio.")
            client_socket.close()
            break

# Funzione principale del client
def client():
    client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    client_socket.connect((HOST, PORT))

    print("Connesso al server.")

    # Avvia un thread per ricevere i messaggi
    receive_thread = threading.Thread(target=receive_messages, args=(client_socket,))
    receive_thread.start()

    # Ciclo per inviare messaggi al server
    while True:
        message = input()
        if message:
            client_socket.send(message.encode('utf-8'))

if __name__ == "__main__":
    client()
