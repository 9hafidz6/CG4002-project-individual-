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

ACTIONS = ['start', 'zigzag', 'rocket', 'hair', 'shouldershrug', 'zigzag', 'rocket']
POSITIONS = ['1', '2', '3', '1', '2', '1']

def client_program(secret_key, port_num, dancer_id):
    host = '127.0.0.1'  # as both code is running on same pc
    #host = socket.gethostname()
    port = int(port_num)  # socket server port number

    client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)  # instantiate
    client_socket.connect((host, port))  # connect to the server

    index = 0

    #wait for the start of dance move
    while True:
        if ACTIONS[index] == 'start':
            message = message = ('#1|' + ACTIONS[index] + '|' + dancer_id)
            message = padding(message)
            message = encrypt_message(message,secret_key)
            send_message(message,client_socket)
            index += 1
            break

    try:
        while client_socket.fileno() != -1:
            message = ('#' + POSITIONS[index] + '|' + ACTIONS[index] + '|' + dancer_id)

            message = padding(message)

            message = encrypt_message(message, secret_key)
            send_message(message,client_socket) #send the encrypted message

            data = client_socket.recv(1024).decode()    #wait to receive message from server
            data = decrypt_message(data,secret_key)
            start_time = request_time()
            data = data[:-data[-1]]    #remove padding

            data = data.decode('utf8')    #to remove b'1|rocketman|' more specifically b'...'
            print('received from server: ' + str(data) + '\n')

            position, action = str(data[1:]).split('|')    #to segregate each data
            print('\nposition: ' + position + '\naction: ' + action)

            if index == 4: #this should be a closing action from the message, decode the message action
                message = 'bye-bye, close'
                message = padding(message)
                message = encrypt_message(message, secret_key)
                send_message(message, client_socket)
                break

            index += 1

    except (ConnectionError, ConnectionRefusedError):
        print("error, connection lost")
        client_socket.close()
        sys.exit(1)

    client_socket.close()  # close the connection
    print("connection closed")

def padding(message):
        #padding to make the message in multiples of 16
        length = 16 - (len(message) % 16)
        message = message.encode()
        message += bytes([length])*length
        print("\t\tpadded message: " + str(message))

        return message

def decrypt_message(message,key):
    print("decrpyting message")
    decoded_message = base64.b64decode(message)
    iv = decoded_message[:16]

    cipher = AES.new(key, AES.MODE_CBC, iv)
    decrypted_message = cipher.decrypt(decoded_message[16:])

    #print(str(decrypted_message))

    return decrypted_message

def encrypt_message(message, key):
    #encrypt messages
    print("\t\tencrypting message")
    iv = Random.new().read(AES.block_size)
    cipher = AES.new(key, AES.MODE_CBC, iv)
    encoded = base64.b64encode(iv + cipher.encrypt(message))

    print("\t\tmessage encrypted")

    return encoded

def send_message(message, client_socket):
    #send message
    print("\t\tsending encrypted message:" + str(message))
    client_socket.send(message)
    print("\t\tsent"+ '\n')

def request_time():
    c= ntplib.NTPClient()
    response = c.request('pool.ntp.org', version = 3)
    #for attr in dir(response):
        #print("remote.%s = %r" % (attr, getattr(response, attr)))
    return response.orig_time

def main():
    dummy_key = b'0123456789ABCDEF'

    if len(sys.argv) < 3:
        print("enter port number [PORT] and dancer id [DANCER_ID]")
        sys.exit()

    port_num = sys.argv[1]
    dancer_id = sys.argv[2]

    client_program(dummy_key, port_num, dancer_id)

if __name__ == '__main__':
    main()
