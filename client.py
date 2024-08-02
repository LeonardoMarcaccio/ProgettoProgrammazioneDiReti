#!/usr/bin/env python3
"""Script relativa alla chat del client utilizzato per lanciare la GUI Tkinter."""
from socket import AF_INET, socket, SOCK_STREAM
from threading import Thread
import tkinter as tkt
import sys
import package
import json

"""La funzione che segue ha il compito di gestire la ricezione dei messaggi."""
def receive():
    while exit_flag == False:
        try:
            incoming_package = package.Package.fromJSON(client_socket.recv(BUFSIZ).decode("utf8"))
            if incoming_package:
                if isinstance(incoming_package, package.Package):
                    match incoming_package.code:
                        case "Message":
                            msg_list.insert(tkt.END, incoming_package.content)
                        case "Update":
                            msg_list.delete(0,tkt.END)
                            finestra.title(incoming_package.content["Room Name"])
                        case "Quit":
                            shut()
        except OSError:
            break

"""La funzione che segue gestisce l'invio dei messaggi."""
def send(event=None):
    msg = my_msg.get()
    my_msg.set("")
    if(msg):
        upload_package = package.Package("Message", msg)
        client_socket.send(upload_package.toJSON().encode("utf8"))

def shut():
    finestra.destroy()
    exit_flag = True
    sys.exit()

"""La funzione che segue viene invocata quando viene chiusa la finestra della chat."""
def on_closing(event=None):
    my_msg.set("/quit")
    send()

exit_flag = False

finestra = tkt.Tk()
finestra.withdraw()
finestra.resizable(True, True)
finestra.title("General")

#creiamo il Frame per contenere i messaggi
messages_frame = tkt.Frame(finestra)
#creiamo una variabile di tipo stringa per i messaggi da inviare.
my_msg = tkt.StringVar()
#indichiamo all'utente dove deve scrivere i suoi messaggi
my_msg.set("Scrivi qui i tuoi messaggi.")
#creiamo una scrollbar per navigare tra i messaggi precedenti.
scrollbar = tkt.Scrollbar(messages_frame)

# La parte seguente contiene i messaggi.
msg_list = tkt.Listbox(
    messages_frame,
    height=30,
    width=150,
    xscrollcommand=scrollbar.set,
    yscrollcommand=scrollbar.set
)
scrollbar.pack(side=tkt.RIGHT, fill=tkt.Y)
msg_list.pack(side=tkt.LEFT, fill=tkt.BOTH)
msg_list.pack()
messages_frame.pack()

#Creiamo il campo di input e lo associamo alla variabile stringa
entry_field = tkt.Entry(finestra, textvariable=my_msg)
# leghiamo la funzione send al tasto Return
entry_field.bind("<Return>", send)

entry_field.pack()
#creiamo il tasto invio e lo associamo alla funzione send
send_button = tkt.Button(finestra, text="Invio", command=send)
#integriamo il tasto nel pacchetto
send_button.pack()

finestra.protocol("WM_DELETE_WINDOW", on_closing)

#----Connessione al Server----
HOST = input('Inserire il Server host: ')
PORT = input('Inserire la porta del server host: ')
if not HOST:
    HOST = "localhost"

if not PORT:
    PORT = 53000
else:
    PORT = int(PORT)

BUFSIZ = 1024
ADDR = (HOST, PORT)

client_socket = socket(AF_INET, SOCK_STREAM)
try:
    client_socket.connect(ADDR)
except Exception as e:
    print("Tenstativo di connessione fallito, riavviare il client ed inserire correttamente i dati relativi al server")

finestra.deiconify()

receive_thread = Thread(target=receive)
receive_thread.start()
# Avvia l'esecuzione della Finestra Chat.
tkt.mainloop()
