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

ACTIONS = ['zigzag', 'rocket', 'hair', 'shouldershrug', 'zigzag', 'bye-bye, close']
POSITIONS = ['1', '2', '3', '1', '2', '1']

def client_program(secret_key, port_num, dancer_id):
    host = '127.0.0.1'  # as both code is running on same pc
    #host = socket.gethostname()
    port = int(port_num)  # socket server port number

    client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)  # instantiate
    client_socket.connect((host, port))  # connect to the server

    index = 0
    start_time = 0

    try:
        while client_socket.fileno() != -1:
            message = client_socket.recv(1024).decode()  #wait to receive message from server
            timer = time.time()
            message = decrypt_message(message,secret_key)
            message = message[:-message[-1]]    #remove padding
            message = message.decode('utf8')    #to remove b'1|rocketman|' more specifically b'...'
            print(f"received from server: {message} \n")
            position, action, ntp_time = str(message[1:]).split('|')    #to segregate each data
            print(f"position : {position} \naction: {action} \nNTP time: {ntp_time}\n")
            offset = timer - float(ntp_time)

            #wait for the start of dance move, FOR TESTING
            while True:
                flag = input('->')
                if flag == 'start':
                    start_time = time.time()
                    break
                else:
                    print("not the starting move")

            delay = start_time - timer - offset
            data = (f"#{POSITIONS[index]}|{ACTIONS[index]}|{dancer_id}|{delay}")
            send_data(client_socket,secret_key,data)

            if ACTIONS[index] == 'bye-bye, close':
                break

            index += 1

    except (ConnectionError, ConnectionRefusedError):
        print("error, connection lost")
        client_socket.close()
        sys.exit(1)

    client_socket.close()  # close the connection
    print("connection closed")

#====================================================================================================================================================================
def padding(message):
        #padding to make the message in multiples of 16
        length = 16 - (len(message) % 16)
        message = message.encode()
        message += bytes([length])*length
        print(f"\t\tpadding: {message}")
        return message

def decrypt_message(message,key):
    print("decrpyting message")
    decoded_message = base64.b64decode(message)
    iv = decoded_message[:16]
    cipher = AES.new(key, AES.MODE_CBC, iv)
    decrypted_message = cipher.decrypt(decoded_message[16:])
    print(f"{decrypt_message}")
    return decrypted_message

def encrypt_message(message, key):
    #encrypt messages
    print("\t\tencrypting data")
    iv = Random.new().read(AES.block_size)
    cipher = AES.new(key, AES.MODE_CBC, iv)
    encoded = base64.b64encode(iv + cipher.encrypt(message))
    print("\t\data encrypted")
    return encoded

def send_data(conn, secret_key, data):
    data = padding(data)
    data = encrypt_message(data,secret_key)
    print(f"\t\tsending encrypted data: {data}")
    conn.send(data)
    print("\t\tsent data\n")

def request_time():
    c= ntplib.NTPClient()
    response = c.request('pool.ntp.org', version = 3)
    #for attr in dir(response):
        #print("remote.%s = %r" % (attr, getattr(response, attr)))
    return response.orig_time

#====================================================================================================================================================================
def main():
    dummy_key = b'0123456789ABCDEF'
    '''
    if len(sys.argv) < 3:
        print("enter port number [PORT] and dancer id [DANCER_ID]")
        sys.exit()

    port_num = sys.argv[1]
    dancer_id = sys.argv[2]
    '''
    #dummy_key = input('enter key->')
    port_num = input('enter port number->')
    dancer_id = input('enter dancer ID->')

    client_program(dummy_key, port_num, dancer_id)

if __name__ == '__main__':
    main()
