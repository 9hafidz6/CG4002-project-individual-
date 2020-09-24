#laptop to ultra96 client
import os
import sys
import random
import time

import socket

import base64
import numpy as np
import pandas as pd
from Crypto.Cipher import AES
from Crypto import Random
import ntplib
import math
import threading

START = ' '
MESSAGE = ' '

def client_program(secret_key, port_num, dancer_id):
    host = '127.0.0.1'  # as both code is running on same pc
    #host = socket.gethostname()
    port = int(port_num)  # socket server port number

    client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)  # instantiate
    client_socket.connect((host, port))  # connect to the server

    #start_time = 0
    RTT = 0

    try:
        while client_socket.fileno() != -1:
            global START
            global MESSAGE

            #create a while loop to wait for start to get RTT time
            #once start flag received, break and receive message from beetle process
            while True:
                while START == ' ':
                    pass
                user_action = START
                timer = time.time()
                data = (f"#|{timer}")
                print(f"data")
                send_data(client_socket,secret_key,data)
                START = ' ' #empty START
                if user_action == '#':
                    message = recv_data(client_socket,secret_key)
                    print(f"message received: {message}\n") #receive NTP timing from ultraServer
                    break

            #create while loop for to receive all messsage from beetle process
            while True:
                while MESSAGE == ' ':
                    pass
                if MESSAGE == 'bye-bye, close':
                    data = (f"bye-bye, close")
                    send_data(client_socket,secret_key,data)
                    break
                data = (f"{MESSAGE}|{dancer_id}")
                send_data(client_socket,secret_key,data)
                MESSAGE = ' '
            break

    except (ConnectionError, ConnectionRefusedError):
        print("error, connection lost")
        client_socket.close()
        sys.exit(1)

    client_socket.close()  # close the connection
    print("client connection closed")

#listen to beetle process, localhost
def server_program():
    host = '127.0.0.1'
    port = 8081
    server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server_socket.bind((host, port))
    server_socket.listen(1)

    conn, address = server_socket.accept()
    try:
        while server_socket.fileno() != -1:
            global START
            global MESSAGE
            #wait for start flag
            while True:
                START = conn.recv(1024).decode('utf8')
                print(f"message from beetle part 1: {START}\n")
                if START == '#':
                    break
            #wait until all message from beetle process finish
            while True:
                MESSAGE = conn.recv(1024).decode('utf8')
                print(f"message from beetle part 2: {MESSAGE}\n")

                if MESSAGE == 'bye-bye, close':
                    break
            break
    except:
        conn.close()
    conn.close()
    print("server connection closed")

#====================================================================================================================================================================

#padding to make the message in multiples of 16
def padding(message):
    length = 16 - (len(message) % 16)
    message = message.encode()
    message += bytes([length])*length
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
    #print("\t\tdata encrypted")
    return encoded

#pad the data, encrypt and send
def send_data(conn, secret_key, data):
    data = padding(data)
    data = encrypt_message(data,secret_key)
    print(f"sending encrypted data: {data}")
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
    #hard coded for testing purposes, actual run will ask user to input
    dummy_key = b'0123456789ABCDEF'

    #dummy_key = input('enter key->')
    port_num = input('enter port number->')
    dancer_id = input('enter dancer ID->')

    #client_program(dummy_key, port_num, dancer_id)
    t1 = threading.Thread(target=client_program,args=(dummy_key, port_num, dancer_id))
    t2 = threading.Thread(target=server_program,args=())
    t1.start()
    t2.start()

    t1.join()
    t2.join()

    print("done!!")

if __name__ == '__main__':
    main()
