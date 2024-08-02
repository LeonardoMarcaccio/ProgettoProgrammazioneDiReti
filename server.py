#!/usr/bin/env python3
"""Script Python per la realizzazione di un Server multithread per connessioni CHAT asincrone."""
from socket import AF_INET, socket, SOCK_STREAM
from threading import Thread
import package
import time

# Dizionari per gestire i client e gli indirizzi
clients = {}
indirizzi = {}
rooms = {"General": []}

# Impostazioni del server
HOST = "localhost"
PORT = 53000
BUFSIZ = 1024
ADDR = (HOST, PORT)

# Creazione del socket del server
SERVER = socket(AF_INET, SOCK_STREAM)
SERVER.bind(ADDR)

"""Accetta connessioni in entrata e avvia un thread per ciascun client."""
def connection_acceptance():
    while True:
        try:
            client, client_address = SERVER.accept()
            print(f"{client_address} si è collegato.")
            response_package = package.Package("Message","Salve! Digita il tuo Nome seguito dal tasto Invio!")
            client.send(response_package.toJSON().encode("utf8"))
            indirizzi[client] = client_address
            Thread(target=manage_client, args=(client,)).start()
        except Exception as e:
            print(f"Errore nell'accettare connessioni: {e}")

"""Gestisce un singolo client."""
def manage_client(client):
    try:
        while True:
            response_package = package.Package.fromJSON(client.recv(BUFSIZ).decode("utf8"))
            if response_package.code == "Message":
                message = response_package.content
                if message.startswith("/"):
                    error_package = package.Package("Message","Uno Username non puo iniziare con il carattere \"/\".")
                    client.send(error_package.toJSON().encode("utf8"))
                else:
                    nome = message.strip()
                    if nome in clients.values():
                        error_package = package.Package("Message","Nome già in uso o Errato. Scegli un altro nome.")
                        client.send(error_package.toJSON().encode("utf8"))
                    else:
                        connection_accepted_package = package.Package("Message",f"Benvenuto {nome}! Se vuoi lasciare la Chat, scrivi /quit per uscire.")
                        client.send(connection_accepted_package.toJSON().encode("utf8"))
                        rooms["General"].append(client)
                        clients[client] = nome
                        break

        while True:
            client = client = next((client_addr for client_addr, client_name in clients.items() if client_name == nome), None)
            if client:
                response_package = package.Package.fromJSON(client.recv(BUFSIZ).decode("utf8"))
                if response_package.code == "Message":
                    message = response_package.content
                    if message:
                        if message.startswith("/"):
                            parse_command(message, client)
                        else:
                            broadcast(get_client_room(client) ,message, nome + ": ")
            else:
                break

    except Exception as e:
        print(f"Errore nel gestire il client: {e}")
        client_shutdown_procedure(client)

def parse_command(message, client):
    """Analizza e gestisce i comandi speciali."""
    try:
        if not message:
            error_package = package.Package("Message", "Nessun comando fornito.")
            client.send(error_package.toJSON().encode("utf8"))
            return

        command = message[1:].partition(' ')[0].lower()
        args = message[len(command)+1:].split()
        nome = clients.get(client)

        match command:
            case "create":
                if len(args) < 1:
                    create_error_package = package.Package("Message", "Specifica il nome della stanza da creare quando lanci il comando.")
                    client.send(create_error_package.toJSON().encode("utf8"))
                else:
                    room_name = " ".join(args)
                    if room_name in rooms:
                        create_error_package = package.Package("Message", f"La stanza {room_name} esiste già.")
                        client.send(create_error_package.toJSON().encode("utf8"))
                    else:
                        client_room_exit(client)
                        rooms.update({room_name: [client]})
                        create_update_package = package.Package("Update", {"Room Name": room_name})
                        client.send(create_update_package.toJSON().encode("utf8"))
                        time.sleep(1)
                        create_response_package = package.Package("Message", f"Hai creato e sei entrato nella stanza {room_name}.")
                        client.send(create_response_package.toJSON().encode("utf8"))

            case "join":
                if len(args) < 1:
                    create_error_package = package.Package("Message", "Specifica il nome della stanza a cui ti vuoi aggiungere quando lanci il comando.")
                    client.send(create_error_package.toJSON().encode("utf8"))
                else:
                    room_name = " ".join(args)
                    if room_name in rooms:
                        client_room_exit(client)
                        rooms[room_name].append(client)
                        join_update_package = package.Package("Update", {"Room Name": room_name})
                        client.send(join_update_package.toJSON().encode("utf8"))
                        time.sleep(1)
                        join_response_package = package.Package("Message", f"Sei entrato nella stanza {room_name}.")
                        client.send(join_response_package.toJSON().encode("utf8"))
                    else:
                        join_error_package = package.Package("Message", "Stanza non trovata.")
                        client.send(join_error_package.toJSON().encode("utf8"))

            case "list":
                if rooms:
                    available_rooms = ', '.join(rooms.keys())
                    list_response_package = package.Package("Message", f"Stanze disponibili: {available_rooms}")
                    client.send(list_response_package.toJSON().encode("utf8"))
                else: 
                    list_error_package = package.Package("Message", "Nessuna stanza disponibile.")
                    client.send(list_error_package.toJSON().encode("utf8"))

            case "quit":
                client_shutdown_procedure(client)

            case _:
                error_package = package.Package("Message","Comando non riconosciuto.")
                client.send(error_package.toJSON().encode("utf8"))

    except Exception as e:
        print(f"Errore nel parsing del comando: {e}")
        client_shutdown_procedure(client)


"""Invia un messaggio in broadcast a tutti i client."""
def broadcast(room, msg, prefisso=""):
    for client in rooms[room]:
        try:
            broadcast_package = package.Package("Message", prefisso + msg)
            client.send(broadcast_package.toJSON().encode("utf8"))
        except Exception as e:
            print(f"Errore nell'invio del messaggio: {e}")
            client_shutdown_procedure(client)

def client_shutdown_procedure(client):
    client_room_exit(client)
    response_package = package.Package("Quit")
    client.send(response_package.toJSON().encode("utf8"))
    del clients[client]
    client.close()

def client_room_exit(client):
    to_check = rooms.copy().keys()
    for room in to_check:
        client_list = rooms[room]
        if client in client_list:
            broadcast(room, f"{clients[client]} ha abbandonato la chat.")
            client_list.remove(client)
            if room != "General" and len(client_list)==0:
                del rooms[room]

def get_client_room(client):
    for room in rooms:
        client_list = rooms[room]
        if client in client_list:
            return room

if __name__ == "__main__":
    SERVER.listen(5)
    print("In attesa di connessioni...")
    ACCEPT_THREAD = Thread(target=connection_acceptance)
    ACCEPT_THREAD.start()
    ACCEPT_THREAD.join()
    SERVER.close()
