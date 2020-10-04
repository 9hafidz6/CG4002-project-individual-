#TCP client
import os
import sys
import random
import time

import socket
import threading
import datetime
import pymongo
import csv
from datetime import datetime
import collections

import base64
import numpy as np
import pandas as pd
from Crypto.Cipher import AES
from Crypto import Random
import math

from collections import deque
db_q = deque()
eval_q = deque()

dict_data = {}

'''
ACTIONS = ['zigzag', 'rocket', 'hair', 'shouldershrug', 'elbowlock']
POSITIONS = ['3 2 1', '1 2 3', '2 3 1', '3 1 2', '1 3 2']
DELAY = ['1.89','2.43','1.5','0.54','2']
dancer_id = ['1','2','3','1','2']
'''
#====================================================================================================================================================================

def threaded_client(ser_addr, ser_port, secret_key):
    #connect to eval server
    client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)  # TCP socket
    client_socket.connect((ser_addr, ser_port))  # connect to the server

    try:
        #index = 0
        user_prompt = input('->')
        exit_flag = False
        while client_socket.fileno() != -1:
            while eval_q:
                index = eval_q.popleft()
                #index, dancer_id, action, position, time = str(data).split('|')
                action = dict_data[index]['action']
                position = dict_data[index]['position']
                time = dict_data[index]['time']

                data = (f"#{position}|{action}|{time}")
                send_data(client_socket,secret_key,data)

                message = client_socket.recv(1024).decode()
                print(f"{message}")
                if action == 'logout':
                    exit_flag = True

            if exit_flag:
                break
            user_prompt = input('->')

            '''
            data = (f"#{POSITIONS[index]}|{ACTIONS[index]}|{DELAY[index]}")
            send_data(client_socket, secret_key, data)

            message = client_socket.recv(1024).decode()
            print(f"{message}")
            index += 1

            if index == len(POSITIONS) - 1:
                index = 0
                user_prompt = input('->')
            '''

    except (ConnectionError, ConnectionRefusedError):
        print("error, connection lost")
        client_socket.close()
    print("closing connection")
    client_socket.close()

#connect and send data to mongoDb atlas server for dashboard
def dashboard_client():
    #connect to dashboard MongoDB atlas
    print("connect to MongoDB atlas")
    connection = connect_to_mongodb()

    while connection:
        flag = 1
        #if there is data in queue, send to mongodb
        while db_q:
            flag = data_to_send()
        if not flag:
            break
    print("connection to MongoDB closed")

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

def makehash():
    return collections.defaultdict(makehash)

#====================================================================================================================================================================

def connect_to_mongodb():
    global db
    global db_predictions
    try:
        client = pymongo.MongoClient("mongodb+srv://huyidi:<password>@cluster0.7p6mm.gcp.mongodb.net/test?retryWrites=true&w=majority")
    except:
        return -1
    else:
        db = client['dashboard-db']
        db_predictions = db.predictions
        return 1

def data_to_send():
    try:
        #send data from queue or csv file for now
        index = db_q.popleft()
        #index, dancer_id, action, position, time = str(data).split('|')
        dancer_id = dict_data[index]['dancer_id']
        action = dict_data[index]['action']
        position = dict_data[index]['position']
        time = dict_data[index]['time']

        data_to_send = {
            "dancerId": dancer_id,
            "move": action,
            "position": position,
            "eventDate": datetime.fromtimestamp(time).strftime("%A, %B %d, %Y %H:%M:%S")
        }
        db_predictions.insert_one(data_to_send)
    except:
        return -1
    else:
        if action == 'logout':
            return -1
        else:
            return 1

#====================================================================================================================================================================
def main():
    ser_addr = input('server address->')
    ser_port = input('server port->')
    secret_key = b'0123456789ABCDEF' #dummy secret key, 16 bytes

    #read data from csv file, temporary
    with open('final_data.csv', mode = 'r') as file:
        csvFile = csv.DictReader(file)
        database = makehash()

        for lines in csvFile:
            index = int(lines['index'])
            dancer_id = int(lines['dancer_id'])
            #dict_data[index] = {'dancer_id':lines['dancer_id'], 'action':lines['action'], 'position':lines['position'], 'time':lines['time']}
            #dict_data[index] = {int(lines['dancer_id']):[lines['action'], lines['position'], lines['time']]}

            database[index][dancer_id] = {'action':lines['action'], 'position':lines['position'], 'time':lines['time']}

            if len(database[index]) == 3:
                db_q.append(index)
                eval_q.append(index)

    #2 threads to send to evaluation and dashboard server_address
    #1 thread to listen/get data from ML side
    t1 = threading.Thread(target=threaded_client, args=(ser_addr, int(ser_port), secret_key))
    t2 = threading.Thread(target=dashboard_client, args=())
    #t3 = threading.Thread()

    t1.start()
    t2.start()
    #t3.start()

    t1.join()
    t2.join()
    #t3.join()

    print("done!")

if __name__ == '__main__':
    main()
