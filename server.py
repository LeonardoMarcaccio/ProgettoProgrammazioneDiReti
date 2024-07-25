import socket
import threading

# Impostazioni del server
HOST = '127.0.0.1'
PORT = 12345

# Dizionario delle stanze, con i nomi delle stanze come chiavi e liste di client come valori
chatrooms = {'general': []}
# Dizionario dei client connessi, con i socket come chiavi e user name come valori
clients = {}
usernames = set()

# Funzione per inviare messaggi a tutti i client in una stanza
def broadcast(message, chatroom, sender_socket):
    for client in chatrooms[chatroom]:
        if client != sender_socket:
            try:
                client.send(message)
            except:
                client.close()
                chatrooms[chatroom].remove(client)

# Funzione per gestire i client
def handle_client(client_socket):
    try:
        # Richiedi l'user name e verifica la sua unicità
        while True:
            client_socket.send("USERNAME".encode('utf-8'))
            username = client_socket.recv(1024).decode('utf-8')
            if username and username not in usernames:
                usernames.add(username)
                clients[client_socket] = username
                break
            else:
                client_socket.send("INVALID_USERNAME".encode('utf-8'))
        
        # Unisci il client alla stanza 'general'
        current_room = 'general'
        chatrooms[current_room].append(client_socket)
        client_socket.send(f"JOINED {current_room}".encode('utf-8'))
        
        while True:
            try:
                message = client_socket.recv(1024).decode('utf-8')
                if message:
                    if message.startswith('/join '):
                        new_chatroom = message.split()[1]
                        if new_chatroom not in chatrooms:
                            chatrooms[new_chatroom] = []
                        chatrooms[current_room].remove(client_socket)
                        chatrooms[new_chatroom].append(client_socket)
                        current_room = new_chatroom
                        client_socket.send(f"JOINED {current_room}".encode('utf-8'))
                    else:
                        broadcast(f"{clients[client_socket]}: {message}".encode('utf-8'), current_room, client_socket)
                else:
                    break
            except:
                break
    except Exception as e:
        print(f"Errore nel gestire il client: {e}")
    finally:
        if client_socket in clients:
            usernames.remove(clients[client_socket])
            del clients[client_socket]
        for room in chatrooms.values():
            if client_socket in room:
                room.remove(client_socket)
        client_socket.close()

# Funzione principale del server
def server():
    server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    try:
        server_socket.bind((HOST, PORT))
        server_socket.listen()
        print(f"Server avviato su {HOST}:{PORT}")
        
        while True:
            try:
                client_socket, client_address = server_socket.accept()
                print(f"Connessione accettata da {client_address}")

                # Avvia un nuovo thread per gestire il client
                thread = threading.Thread(target=handle_client, args=(client_socket,))
                thread.start()
            except Exception as e:
                print(f"Errore nell'accettare connessioni: {e}")
    except Exception as e:
        print(f"Errore nell'avviare il server: {e}")
    finally:
        server_socket.close()

if __name__ == "__main__":
    server()
