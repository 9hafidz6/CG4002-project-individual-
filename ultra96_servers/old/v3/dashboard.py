#ultra96 to dashboard
#server program to listen to ultra96 client
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

def main():
    #main program
    secret_key = '0123456789ABCDEF'
    host = '127.0.0.1'
    port = 8093

    server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)  # get instance
    try:
        server_socket.bind((host, port)  #bind host address and port together
    except socket.error as e:
        print(str(e))
    print(f"waiting for connection on thread: {ThreadCount}")
    #configure server into listen mode
    server_socket.listen(1)
        conn, address = server_socket.accept()  # accept new connection

    while True:
        message = recv_data(conn, secret_key)
        timestamp, raw, QUATW, QUATX, QUATY, QUATZ, ACCELX, ACCELY, ACCELZ, GYROX, GYROY, GYROZ, dancer_id, final_offset = str(message).split('|')    #to segregate each data
        print(f"received message from laptop:\ndancer ID: {dancer_id}\ntimestamp: {timestamp}\nraw: {raw}\nQUAT W: {QUATW}\nQUAT X: {QUATX}\nQUAT Y: {QUATY}\nQUAT Z: {QUATZ}")
        print(f"ACCEL X: {ACCELX}\nACCEL Y: {ACCELY}\nACCELZ: {ACCELZ}\nGYRO X: {GYROX}\nGYRO Y: {GYROY}\nGYRO Z: {GYROZ}\n\n")

if __name__ == '__main__':
    main()
