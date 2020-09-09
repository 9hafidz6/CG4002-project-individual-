#multithread server_socket
import socket
import os
from _thread import *

ServerSocket = socket.socket()
host = '127.0.0.1'
port = 1233
ThreadCount = 0
try:
    ServerSocket.bind((host, port))
except socket.error as e:
    print(str(e))

print('Waitiing for a Connection..')
ServerSocket.listen(5)


def threaded_client(connection, secret_key):
    connection.send(str.encode('Welcome to the Server\n'))
    print(f"{secret_key}")
    while True:
        data = connection.recv(2048)
        reply = 'Server Says: ' + data.decode('utf-8')
        print(data.decode())
        if not data or data.decode() == 'bye-bye':
            break
        connection.sendall(str.encode(reply))
    print('close connection')
    connection.close()

secret_key = 'test123'

while True:
    Client, address = ServerSocket.accept()
    print('Connected to: ' + address[0] + ':' + str(address[1]))
    start_new_thread(threaded_client, (Client, secret_key))
    ThreadCount += 1
    print('Thread Number: ' + str(ThreadCount))
ServerSocket.close()
