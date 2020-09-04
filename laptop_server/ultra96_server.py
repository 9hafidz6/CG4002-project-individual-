#ultra96 server
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
import ntplib

ACTIONS = ['zigzag', 'rocket', 'hair', 'shouldershrug', 'zigzag', 'rocket']
POSITIONS = ['1 2 3', '3 2 1', '2 3 1', '3 1 2', '1 3 2', '2 1 3']

file = open("raw_data.txt", "a+")

def server_program(secret_key, port_num):
    # get the hostname
    #host = socket.gethostname()
    host = '127.0.0.1'
    port = int(port_num)  # initiate port no above 1024

    server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)  # get instance
    # look closely. The bind() function takes tuple as argument
    server_socket.bind((host, port))  # bind host address and port together

    # configure how many client the server can listen simultaneously
    server_socket.listen(3)
    conn, address = server_socket.accept()  # accept new connection
    print("Connection from: " + str(address) + '\n')

    index = 0
    start_time = 0
    end_time = 0
    delay = 0
    try:
        while server_socket.fileno() != -1:
            # receive data stream. it won't accept data packet greater than 1024 bytes
            data = conn.recv(1024).decode()
            end_time = time.clock_gettime(time.CLOCK_REALTIME)

            if start_time != 0:
                delay = 1000 * (end_time - start_time)
                delay = round(delay,2)

            message = decrypt_message(data,secret_key)
            message = message[:-message[-1]]    #remove padding

            print("received from client: " + str(message))

            message = message.decode('utf8')    #to remove b'1|rocketman|2.3', b''
            if message == 'bye-bye, close':
                break

            position, action, dancer_id = str(message[1:]).split('|')    #to segregate each data
            print( '\ndancer id: ' + dancer_id + '\nposition: ' + position + '\naction: ' + action + '\ndelay: '+ str(delay) + 'ms')
            file.write('index:' + str(index) + '\n' + position + ',' + action + ',' + dancer_id + ',' + str(delay) + '\n\n')

            #data = input(' -> ')
            data = ('#' + POSITIONS[index] + '|' + ACTIONS[index])
            data = padding(data)
            data = encrypt_message(data,secret_key)
            #conn.send(data.encode())  # send data to the client
            send_message(data,conn)
            start_time = time.clock_gettime(time.CLOCK_REALTIME)
            index += 1

    except (ConnectionError, ConnectionRefusedError):
        print("error, connection lost")
        conn.close()
        file.close()
        sys.exit(1)

    conn.close()  # close the connection
    file.close()
    print("connection closed")

def padding(data):
        #padding to make the message in multiples of 16
        length = 16 - (len(data) % 16)
        data = data.encode()
        data += bytes([length])*length
        print("\t\tpadded message: " + str(data))

        return data

def decrypt_message(cipher_text, key):
    print("decrpyting message")
    decoded_message = base64.b64decode(cipher_text)
    iv = decoded_message[:16]

    cipher = AES.new(key, AES.MODE_CBC, iv)
    decrypted_message = cipher.decrypt(decoded_message[16:])    #removed the strip() function

    #print(str(decrypted_message))

    return decrypted_message

def encrypt_message(message, secret_key):
    #encrypt messages
    print("\t\tencrypting message")
    iv = Random.new().read(AES.block_size)
    cipher = AES.new(secret_key, AES.MODE_CBC, iv)

    encoded = base64.b64encode(iv + cipher.encrypt(message))

    print("\t\tmessage encrypted")

    return encoded

def send_message(message, server_socket):
    print("\t\tsending encrypted message: " + str(message))
    server_socket.send(message)
    print("\t\tmessage sent" + '\n')

def main():
    secret_key = b'0123456789ABCDEF'

    if len(sys.argv) < 2:
        print("enter port number: [PORT]")
        sys.exit()

    port_num = sys.argv[1]

    server_program(secret_key, port_num)

if __name__ == '__main__':
    main()
