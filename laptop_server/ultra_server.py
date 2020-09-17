#ultra96 server
import os
import sys
import random
import time

import socket
from _thread import *

import base64
import numpy as np
import pandas as pd
from Crypto.Cipher import AES
from Crypto import Random
import math
import ntplib

ACTIONS = ['zigzag', 'rocket', 'hair', 'shouldershrug', 'zigzag', 'rocket']
POSITIONS = ['1 2 3', '3 2 1', '2 3 1', '3 1 2', '1 3 2', '2 1 3']

def threaded_client(conn, secret_key, server_socket):
    file = open("raw_data.txt", "a+")
    index = 0

    start_time = 0
    delay = 0

    try:
        while server_socket.fileno() != -1:
            start_time = request_time()
            data = (f"#{POSITIONS[index]}|{ACTIONS[index]}|{start_time}")
            send_data(conn,secret_key,data)
            #print("message sent")

            # receive data stream. it won't accept data packet greater than 1024 bytes
            data = conn.recv(1024).decode()

            message = decrypt_message(data,secret_key)
            message = message[:-message[-1]]    #remove padding
            #print("received from client: " + str(message))
            message = message.decode('utf8')    #to remove b'1|rocketman|2.3', b''

            position, action, dancer_id, delay = str(message[1:]).split('|')    #to segregate each data
            print(f"\ndancer id: {dancer_id} \nposition: {position} \naction: {action} \ndelay: {delay}s \n")
            file.write(position + ',' + action + ',' + dancer_id + ',' + str(delay) + '\n')

            if action == 'bye-bye, close':
                break

            index += 1

    except (ConnectionError, ConnectionRefusedError):
        print("error, connection lost")
        conn.close()
        file.close()
        sys.exit(1)

    conn.close()  # close the connection
    file.close()
    print("connection closed")

#====================================================================================================================================================================
def padding(data):
        #padding to make the message in multiples of 16
        length = 16 - (len(data) % 16)
        data = data.encode()
        data += bytes([length])*length
        print("\t\tpadding: " + str(data))
        return data

def decrypt_message(cipher_text, key):
    print("decrpyting message")
    decoded_message = base64.b64decode(cipher_text)
    iv = decoded_message[:16]
    cipher = AES.new(key, AES.MODE_CBC, iv)
    decrypted_message = cipher.decrypt(decoded_message[16:])    #removed the strip() function
    print(f"{decrypted_message}")
    return decrypted_message

def encrypt_message(message, secret_key):
    #encrypt messages
    print("\t\tencrypting data")
    iv = Random.new().read(AES.block_size)
    cipher = AES.new(secret_key, AES.MODE_CBC, iv)
    encoded = base64.b64encode(iv + cipher.encrypt(message))
    print(f"\t\data encrypted: {encoded}")
    return encoded

def send_data(conn, secret_key, data):
    data = padding(data)
    data = encrypt_message(data,secret_key)
    conn.send(data)
    print("data sent")

def request_time():
    c= ntplib.NTPClient()
    response = c.request('pool.ntp.org', version = 3)
    #for attr in dir(response):
        #print("remote.%s = %r" % (attr, getattr(response, attr)))
    return response.orig_time
#====================================================================================================================================================================
def main():
    ThreadCount = 0
    secret_key = b'0123456789ABCDEF'

    if len(sys.argv) < 2:
        print("enter port number: [PORT]")
        sys.exit()

    port_num = sys.argv[1]
    #host = socket.gethostname()
    host = '127.0.0.1'

    server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)  # get instance
    try:
        server_socket.bind((host, int(port_num)))  # bind host address and port together
    except socket.error as e:
        print(str(e))
    print('waiting for connection')
    # configure server into listen mode
    server_socket.listen(3)

    #threading
    try:
        while server_socket.fileno() != -1:
            if ThreadCount > 3:
                break

            conn, address = server_socket.accept()  # accept new connection
            print('Connected to: ' + address[0] + ':' + str(address[1]))
            start_new_thread(threaded_client, (conn, secret_key, server_socket))
            ThreadCount += 1
            print('Thread Number: ' + str(ThreadCount))

    except:
        print("closing connection")
        server_socket.close()

if __name__ == '__main__':
    main()
