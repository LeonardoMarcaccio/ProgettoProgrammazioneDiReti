#!/usr/bin/env python3
"""Script Python per la realizzazione di un Server multithread
per connessioni CHAT asincrone."""

from socket import AF_INET, socket, SOCK_STREAM
from threading import Thread

# Dizionari per gestire i client e gli indirizzi
clients = {}
indirizzi = {}

# Impostazioni del server
HOST = "localhost"
PORT = 53000
BUFSIZ = 1024
ADDR = (HOST, PORT)

# Creazione del socket del server
SERVER = socket(AF_INET, SOCK_STREAM)
SERVER.bind(ADDR)

"""Accetta connessioni in entrata e avvia un thread per ciascun client."""
def accetta_connessioni_in_entrata():
    while True:
        try:
            client, client_address = SERVER.accept()
            print(f"{client_address} si è collegato.")
            client.send("Salve! Digita il tuo Nome seguito dal tasto Invio!".encode("utf8"))
            indirizzi[client] = client_address
            Thread(target=gestice_client, args=(client,)).start()
        except Exception as e:
            print(f"Errore nell'accettare connessioni: {e}")

"""Gestisce un singolo client."""
def gestice_client(client):
    try:
        nome = client.recv(BUFSIZ).decode("utf8")
        benvenuto = f'Benvenuto {nome}! Se vuoi lasciare la Chat, scrivi {{quit}} per uscire.'
        client.send(benvenuto.encode("utf8"))
        msg = f"{nome} si è unito alla chat!"
        broadcast(msg.encode("utf8"))
        clients[client] = nome

        while True:
            msg = client.recv(BUFSIZ)
            if msg != bytes("{quit}", "utf8"):
                broadcast(msg, f"{nome}: ")
            else:
                client.send(bytes("{quit}", "utf8"))
                client.close()
                del clients[client]
                broadcast(f"{nome} ha abbandonato la Chat.".encode("utf8"))
                break
    except Exception as e:
        print(f"Errore nel gestire il client: {e}")
    finally:
        if client in clients:
            nome = clients[client]
            del clients[client]
            broadcast(f"{nome} ha abbandonato la Chat.".encode("utf8"))

"""Invia un messaggio in broadcast a tutti i client."""
def broadcast(msg, prefisso=""):
    for utente in clients:
        try:
            utente.send(prefisso.encode("utf8") + msg)
        except Exception as e:
            print(f"Errore nell'invio del messaggio: {e}")
            utente.close()
            del clients[utente]

if __name__ == "__main__":
    SERVER.listen(5)
    print("In attesa di connessioni...")
    ACCEPT_THREAD = Thread(target=accetta_connessioni_in_entrata)
    ACCEPT_THREAD.start()
    ACCEPT_THREAD.join()
    SERVER.close()
