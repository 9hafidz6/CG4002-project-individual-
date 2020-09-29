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
POSITIONS = ['3 2 1', '1 2 3', '2 3 1', '3 1 2', '1 3 2', '2 1 3']
DELAY = ['1.89','2.43','1.5','0.54','2','4.5']

class Client(threading.Thread):
    def __init__(self,ser_addr, port_num, secret_key):
        super(Client, self).__init__()
        self.key = secret_key

        # setup moves
        self.actions = ACTIONS
        self.position = POSITIONS

        #creating socket
        self.s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        #connecting
        self.setup_connection(ser_addr, port_num)

    def run(self):
        index = 0   #just for testing

        while self.check_connection() != -1 and index < len(POSITIONS) - 1:
            data = (f"#{POSITIONS[index]}|{ACTIONS[index]}|{DELAY[index]}")
            data = self.padding(data)
            data = self.encrypt_message(data)
            #user_prompt = input('->')
            self.send_message(data)

            message = self.receive_message()
            print(message)

            index += 1

        print('closing connection')
        self.close_connection()

    def padding(self,data):
        #pad the data to size of 16
        length = 16 - (len(data) % 16)
        data = data.encode()
        data += bytes('\n', 'utf8')*length   #if padding of \0x10 for example, the evaluation server will not unpad properly
        print("padded data: " + str(data))
        return data

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
    ser_addr = input('server address->')
    ser_port = input('server port->')

    #dash_addr = input('dashboard address->')
    #dash_port = input('dashboard port->')

    secret_key = b'0123456789ABCDEF' #dummy secret key, 16 bytes

    evaluation_thread = Client(ser_addr, int(ser_port), secret_key)
    evaluation_thread.start() #start the thread

    #start another thread to pass data to dashboard
    #dashboard_thread = Client(dash_addr, int(dash_port), secret_key)
    #dashboard_thread.start()

if __name__ == '__main__':
    main()
