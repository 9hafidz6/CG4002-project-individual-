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
POSITIONS = ['1 2 3', '3 2 1', '2 3 1', '3 1 2', '1 3 2', '2 1 3']
NUM_MOVE_PER_ACTION = 4
N_TRANSITIONS = 6
MESSAGE_SIZE = 3 # position, 1 action, sync

class Client(threading.Thread):
    def __init__(self,ser_addr, port_num, secret_key):
        super(Client, self).__init__()
        self.key = secret_key

        # setup moves
        self.actions = ACTIONS
        self.position = POSITIONS
        self.n_moves = int(NUM_MOVE_PER_ACTION)

        #creating socket
        self.s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.setup_connection(ser_addr, port_num)

    def padding(self,message):
        #pad the message to size of 16
        length = 16 - (len(message) % 16)
        message = message.encode()
        message += bytes('\n', 'utf8')*length   #if padding of \0x10 for example, the evaluation server will not unpad properly
        print("padded message: " + str(message))

        return message

    def encrypt_message(self, message):
        #encrypt the message with address
        print("encrypting message")
        iv = Random.new().read(AES.block_size)
        cipher = AES.new(self.key, AES.MODE_CBC, iv)

        encoded = base64.b64encode(iv + cipher.encrypt(message))

        return encoded

    def setup_connection(self, ser_addr, port_num):
        #connect to server via TCP
        print("connection setup")
        try:
            self.s.connect((ser_addr,port_num))
        except:
            print("unable to connect to server")
        else:
            print("connected")

    def check_connection(self):
        #check connection
        return self.s.fileno()

    def close_connection(self):
        #close socket connection
        print("closing connection")
        self.s.close()

    def send_message(self, cipher_text):
        #send encrypted message to server in a defined format
        print("sending encrpyted message")
        self.s.send(cipher_text)
        print("message sent")

    def receive_message(self):
        #receive message from server
        return self.s.recv(1024).decode()

def main():
    if len(sys.argv) != 3:
        print('Invalid number of arguments')
        print('python client.py [IP address] [Port] [secret key]')
        sys.exit()

    ser_addr = sys.argv[1]  #might just need port number, ssh tunnel
    port_num = int(sys.argv[2])
    #secret_key = sys.argv[3]
    secret_key = b'0123456789ABCDEF' #dummy secret key, 16 bytes
    #dummy_message = '#1 2 3|shouldershrug|1.80' #must be multiple of 16 bytes

    '''
    #check the input arguments
    print(sys.argv[1])
    print(sys.argv[2])
    print(sys.argv[3])
    print(sys.argv[4])
    '''

    my_client = Client(ser_addr, port_num, secret_key)
    my_client.start() #start the thread

    index = 0   #just for testing

    test = input('->')

    while my_client.check_connection() != -1:
        #send data from ultra96 to evaluation server
        #message = input('->')
        message = ('#' + POSITIONS[index] + '|' + ACTIONS[index] + '|' + str(index))    #change padding, cannot \x10 etc, can only \d \r \t etc
        message = my_client.padding(message)
        cipher_text = my_client.encrypt_message(message)
        my_client.send_message(cipher_text)

        data = my_client.receive_message()
        print(data)

        index += 1

    my_client.close_connection()
if __name__ == '__main__':
    main()
