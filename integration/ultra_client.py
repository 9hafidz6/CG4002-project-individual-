#listen for data from ML side
#to send data evaluation server and dashboard
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

#====================================================================================================================================================================
def threaded_client(ser_addr, ser_port, secret_key, onMlReady=None):
    #connect to eval server
    client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)  # TCP socket
    client_socket.connect((ser_addr, ser_port))  # connect to the server

    try:
        #index = 0
        #user_prompt = input('->')
        exit_flag = False
        dancer_position = np.array([1, 2, 3])
        while client_socket.fileno() != -1:

            if onMlReady is not None:
                newdata = onMlReady(forEval=True)
                while newdata is not None:
                    dancer_id1 = 1
                    action1 = newdata[dancer_id1]['action']
                    position1 = newdata[dancer_id1]['position']
                    time1 = newdata[dancer_id1]['time']

                    dancer_id2 = 2
                    action2 = action1
                    position2 = position1 + 1
                    time2 = time1

                    dancer_id3 = 3
                    action3 = action2
                    position3 = position2 + 1
                    time3 = time2

                    # index = eval_q.popleft()

                    # dancer_id1 = 1
                    # action1 = database[index][dancer_id1]['action']
                    # position1 = database[index][dancer_id1]['position']
                    # time1 = database[index][dancer_id1]['time']

                    # dancer_id2 = 2
                    # action2 = database[index][dancer_id2]['action']
                    # position2 = database[index][dancer_id2]['position']
                    # time2 = database[index][dancer_id2]['time']

                    # dancer_id3 = 3
                    # action3 = database[index][dancer_id3]['action']
                    # position3 = database[index][dancer_id3]['position']
                    # time3 = database[index][dancer_id3]['time']

                    #check if actions are all same
                    if not action1 == action2 == action3:
                        print("actions are not the same")
                        continue
                    #check if positions are all different
                    #print(f"{position1} {position2} {position3}")
                    if position1 == position2 == position3:
                        print("some have same positions")
                        continue

                    dancer_position[int(position1)-1] = dancer_id1
                    dancer_position[int(position2)-1] = dancer_id2
                    dancer_position[int(position3)-1] = dancer_id3

                    final_position = (f"{dancer_position[0]} {dancer_position[1]} {dancer_position[2]}")

                    data = (f"#{final_position}|{action1}|{time1}")
                    send_data(client_socket,secret_key,data)
                    print(data)

                    message = client_socket.recv(1024).decode()
                    print(f"Recved {message}")

                    if action1 == 'logout':
                        print("exiting")
                        exit_flag = True

                    newdata = onMlReady(forEval=True)

            if exit_flag:
                break
            time.sleep(0.001)
            #user_prompt = input('->')

    except (ConnectionError, ConnectionRefusedError):
        print("error, connection lost")
        client_socket.close()
    print("closing connection")
    client_socket.close()

#connect and send data to mongoDb atlas server for dashboard
def dashboard_client(onMlReady=None):
    #connect to dashboard MongoDB atlas
    print("connecting to MongoDB atlas")
    connection = connect_to_mongodb()

    while connection:
        flag = 1
        #if there is data in queue, send to mongodb
        if onMlReady is not None:
            newdata = onMlReady(forDB=True)
            while newdata is not None:
                flag = data_to_send(newdata)
                newdata = onMlReady(forDB=True)

        if not flag:
            break
        time.sleep(0.001)
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

#for storing the data from csv file or ML
def makehash():
    return collections.defaultdict(makehash)

#====================================================================================================================================================================

def connect_to_mongodb():
    global db
    global db_predictions
    try:
        client = pymongo.MongoClient("mongodb+srv://hafidz:hafidz@cluster0.7p6mm.gcp.mongodb.net/test1?retryWrites=true&w=majority")
    except:
        print("error connecting to mongodb")
        return -1
    else:
        print("successfully connected to Mongo")
        db = client['test1']
        db_predictions = db.predictions
        return 1

def data_to_send(data):
    try:
        #send data from queue or csv file for now
        # index = db_q.popleft()

        dancer_id1 = 1
        index = data[dancer_id1]['index']
        action1 = data[dancer_id1]['action']
        position1 = data[dancer_id1]['position']
        time1 = data[dancer_id1]['time']

        dancer_id2 = 2
        action2 = action1
        position2 = position1 + 1
        time2 = time1

        dancer_id3 = 3
        action3 = action2
        position3 = position2 + 1
        time3 = time2

        # dancer_id1 = 1
        # action1 = database[index][dancer_id1]['action']
        # position1 = database[index][dancer_id1]['position']
        # time1 = database[index][dancer_id1]['time']

        # dancer_id2 = 2
        # action2 = database[index][dancer_id2]['action']
        # position2 = database[index][dancer_id2]['position']
        # time2 = database[index][dancer_id2]['time']

        # dancer_id3 = 3
        # action3 = database[index][dancer_id3]['action']
        # position3 = database[index][dancer_id3]['position']
        # time3 = database[index][dancer_id3]['time']

        data_list = [
            {"index": index, "dancerId": dancer_id1, "move": action1, "position": position1, "eventDate": datetime.fromtimestamp(int(time1)).strftime("%A, %B %d, %Y %H:%M:%S")},
            {"index": index, "dancerId": dancer_id2, "move": action2, "position": position2, "eventDate": datetime.fromtimestamp(int(time2)).strftime("%A, %B %d, %Y %H:%M:%S")},
            {"index": index, "dancerId": dancer_id3, "move": action3, "position": position3, "eventDate": datetime.fromtimestamp(int(time3)).strftime("%A, %B %d, %Y %H:%M:%S")}
        ]

        db_predictions.insert_many(data_list)
    except Exception as e:
        print(f"Error: {e}")
        print("error sending to MongoDB")
        return -1
    else:
        if action1 == 'logout':
            return -1
        else:
            print("successfully sent to MongoDB")
            return 1

#====================================================================================================================================================================
def main():
    ser_addr = input('server address->')
    ser_port = input('server port->')

    secret_key = b'0123456789ABCDEF' #dummy secret key, 16 bytes

    #read data from csv file, temporary, by right, data will stream from ML side, get via another thread
    with open('final_data.csv', mode = 'r') as file:
        csvFile = csv.DictReader(file)
        global database
        database = makehash()

        for lines in csvFile:
            index = int(lines['index'])
            dancer_id = int(lines['dancer'])

            database[index][dancer_id] = {'action':lines['action'], 'position':lines['position'], 'time':lines['time']}

            if len(database[index]) == 3:
                db_q.append(index)
                eval_q.append(index)
        #print(database)

    #2 threads to send to evaluation and dashboard server_address
    t1 = threading.Thread(target=threaded_client, args=(ser_addr, int(ser_port), secret_key, database))
    t2 = threading.Thread(target=dashboard_client, args=(database,))
    #1 thread to listen/get data from ML side
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
