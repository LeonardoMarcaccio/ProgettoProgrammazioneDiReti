import socket
import threading

# Impostazioni del server
HOST = '127.0.0.1'
PORT = 12345

# Dizionario delle stanze, con i nomi delle stanze come chiavi e liste di client come valori
rooms = {'general': []}
# Dizionario dei client connessi, con i socket come chiavi e user name come valori
clients = {}
usernames = set()

# Funzione per inviare messaggi a tutti i client in una stanza
def broadcast(message, room, sender_socket):
    for client in rooms[room]:
        try:
            client.send(message)
        except:
            client.close()
            rooms[room].remove(client)

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
        rooms[current_room].append(client_socket)
        client_socket.send(f"JOINED {current_room}".encode('utf-8'))
        broadcast(f"{username} è entrato nella stanza {current_room}".encode('utf-8'), current_room, client_socket)

        while True:
            try:
                message = client_socket.recv(1024).decode('utf-8')
                if message:
                    # Parsing del messaggio con un dizionario di funzioni
                    command, *args = message.split(' ', 1)
                    switcher = {
                        '/join': join_room,
                        '/create': create_room,
                        'default': default_message
                    }
                    switcher.get(command, switcher['default'])(client_socket, args, current_room)
                else:
                    break
            except:
                break
    except Exception as e:
        print(f"Errore nel gestire il client: {e}")
    finally:
        if client_socket in clients:
            username = clients[client_socket]
            usernames.remove(username)
            del clients[client_socket]
            for room in rooms.values():
                if client_socket in room:
                    room.remove(client_socket)
                    broadcast(f"{username} ha lasciato la chat.".encode('utf-8'), room, None)
        client_socket.close()

def join_room(client_socket, args, current_room):
    username = clients[client_socket]
    new_room = args[0] if args else 'general'
    if new_room not in rooms:
        rooms[new_room] = []
    rooms[current_room].remove(client_socket)
    rooms[new_room].append(client_socket)
    current_room = new_room
    client_socket.send(f"JOINED {current_room}".encode('utf-8'))
    broadcast(f"{username} è entrato nella stanza {current_room}".encode('utf-8'), current_room, client_socket)

def create_room(client_socket, args, current_room):
    username = clients[client_socket]
    new_room = args[0] if args else 'general'
    if new_room not in rooms:
        rooms[new_room] = []
    rooms[current_room].remove(client_socket)
    rooms[new_room].append(client_socket)
    current_room = new_room
    client_socket.send(f"CREATED {new_room} AND JOINED {current_room}".encode('utf-8'))
    broadcast(f"{username} ha creato e si è unito alla stanza {current_room}".encode('utf-8'), current_room, client_socket)

def default_message(client_socket, args, current_room):
    username = clients[client_socket]
    message = ' '.join(args)
    broadcast(f"{username}: {message}".encode('utf-8'), current_room, client_socket)

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
