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
                print("Connessione chiusa dal server.")
                break
        except Exception as e:
            print(f"Errore nella ricezione del messaggio: {e}")
            client_socket.close()
            break

# Funzione principale del client
def client():
    client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    try:
        client_socket.connect((HOST, PORT))
        print("Connesso al server.")
        
        # Richiedi e invia l'user name univoco
        while True:
            username = input("Inserisci il tuo username: ")
            client_socket.send(username.encode('utf-8'))
            response = client_socket.recv(1024).decode('utf-8')
            if response == "JOINED general":
                print(f"Sei entrato nella stanza 'general' come {username}.")
                break
            elif response == "INVALID_USERNAME":
                print("Username già in uso, scegline un altro.")
        
        # Avvia un thread per ricevere i messaggi
        receive_thread = threading.Thread(target=receive_messages, args=(client_socket,))
        receive_thread.start()

        # Ciclo per inviare messaggi al server
        while True:
            message = input()
            if message:
                client_socket.send(message.encode('utf-8'))
            else:
                print("Connessione chiusa dal client.")
                break
    except Exception as e:
        print(f"Errore nella connessione al server: {e}")
    finally:
        client_socket.close()

if __name__ == "__main__":
    client()
