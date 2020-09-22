#python process
#send data on localhost
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

def main():
    #main program
    start_prompt = input('->')
    host = '127.0.0.2'
    port_num = 8081
    index = 0

    client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)  # instantiate
    client_socket.connect((host, port_num))  # connect to the server
    print('connected\n')
    while index <= len(ACTIONS) - 1:
        data = 'start'
        data = data.encode()
        client_socket.send(data)
        print("start command sent")
        time.sleep(2)
        data = (f"#{POSITIONS[index]}|{ACTIONS[index]}")
        data = data.encode()
        print(f"data sent: {data}")
        client_socket.send(data)
        time.sleep(4)
        index += 1
    client_socket.close()

if __name__ == '__main__':
    main()
