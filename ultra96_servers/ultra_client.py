#TCP client
import os
import sys
import random
import time

import socket
import threading

import base64
import numpy as np
import pandas as pd
from Crypto.Cipher import AES
from Crypto import Random
import math

ACTIONS = ['zigzag', 'rocket', 'hair', 'shouldershrug', 'elbowlock']
POSITIONS = ['3 2 1', '1 2 3', '2 3 1', '3 1 2', '1 3 2']
DELAY = ['1.89','2.43','1.5','0.54','2']
#dancer_id = ['1','2','3','1','2']

def threaded_client(ser_addr, ser_port, secret_key):
    #connect to eval server
    client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)  # TCP socket
    client_socket.connect((ser_addr, ser_port))  # connect to the server

    try:
        index = 0
        user_prompt = input('->')
        while client_socket.fileno() != -1 and index < len(POSITIONS) - 1:
            data = (f"#{POSITIONS[index]}|{ACTIONS[index]}|{DELAY[index]}")
            send_data(client_socket, secret_key, data)

            message = client_socket.recv(1024).decode()
            print(f"{message}")
            index += 1

    except (ConnectionError, ConnectionRefusedError):
        print("error, connection lost")
        client_socket.close()
    print("closing connection")
    client_socket.close()

def dashboard_client():
    #connect to dashboard MongoDB atlas
    print("test")

#====================================================================================================================================================================

#padding to make the message in multiples of 16
def padding(message):
    length = 16 - (len(message) % 16)
    message = message.encode()
    message += bytes('\n', 'utf8')*length   #if padding of \0x10 for example, the evaluation server will not unpad properly
    print(f"padding: {message}")
    return message

#decrypt the message
def decrypt_message(message,key):
    #print("decrpyting message")
    decoded_message = base64.b64decode(message)
    iv = decoded_message[:16]
    cipher = AES.new(key, AES.MODE_CBC, iv)
    decrypted_message = cipher.decrypt(decoded_message[16:])
    #print(f"{decrypt_message}")
    return decrypted_message

#encrypt the message
def encrypt_message(message, key):
    #print("\t\tencrypting data")
    iv = Random.new().read(AES.block_size)
    cipher = AES.new(key, AES.MODE_CBC, iv)
    encoded = base64.b64encode(iv + cipher.encrypt(message))
    print(f"sending encrypted data: {encoded}")
    return encoded

#pad the data, encrypt and send
def send_data(conn, secret_key, data):
    data = padding(data)
    data = encrypt_message(data,secret_key)
    conn.send(data)
    print("sent data\n")

#receive message from ultra96, decrypt, unpad and decode
def recv_data(client_socket, secret_key):
    message = client_socket.recv(1024).decode()  #wait to receive message
    message = decrypt_message(message,secret_key)
    message = message[:-message[-1]]    #remove padding
    message = message.decode('utf8')    #to remove b'1|rocketman|'
    return message

#====================================================================================================================================================================
def main():
    ser_addr = input('server address->')
    ser_port = input('server port->')

    #dash_addr = input('dashboard address->')
    #dash_port = input('dashboard port->')

    secret_key = b'0123456789ABCDEF' #dummy secret key, 16 bytes
    '''
    evaluation_thread = Client(ser_addr, int(ser_port), secret_key)
    evaluation_thread.start() #start the thread
    '''
    t1 = threading.Thread(target=threaded_client, args=(ser_addr, int(ser_port), secret_key))
    #t2 = threading.Thread(target=threaded_client, args=(' ', ' ', secret_key))
    #t3 = threading.Thread()

    t1.start()
    #t2.start()
    #t3.start()

    t1.join()
    #t2.join()
    #t3.join()

    print("done!")

if __name__ == '__main__':
    main()
