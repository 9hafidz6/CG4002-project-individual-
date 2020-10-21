#get data from laptop
#save data onto tx txt file
import os
import sys
import random
import time
import socket
import threading
from datetime import datetime
import base64
import numpy as np
import pandas as pd
from Crypto.Cipher import AES
from Crypto import Random
import math
import ntplib

num_of_nodes = 0
timex = 0

#listen and receive data from client, parse the data and store in txt file
def threaded_server(port_num, secret_key, ThreadCount, cv, onRecv=None):
    file = open("raw_data.txt", "a+")

    host = '127.0.0.1'
    server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)  # get instance
    try:
        server_socket.bind((host, int(port_num)))  # bind host address and port together
    except socket.error as e:
        print(f"{e}")
    print(f"waiting for connection on server thread: {ThreadCount}")
    # configure server into listen mode
    server_socket.listen(1)

    conn, address = server_socket.accept()  # accept new connection
    print(f"Connected to: {address[0]} : {str(address[1])} on server thread: {ThreadCount}")

    try:
        while server_socket.fileno() != -1:
            global num_of_nodes
            finish = False
            raw = " "
            final_time = 0

            #wait for start of dance, get ntp timing and send back to get rtt and offset
            message = recv_data(conn, secret_key)

            timestamp, raw, ACCELX, ACCELY, ACCELZ, ELBOWX, ELBOWY, ELBOWZ, HANDX, HANDY, HANDZ = str(message).split('|')    #to segregate each data
            print(f"start message received: {message}")
            #ntp_time = request_time()
            num_of_nodes += 1   #increment for every start message
            with cv:    #to acquire the lock associated with condition
                cv.wait()   #releases the lock
            data = (f"{timex}")
            send_data(conn, secret_key, data)
            # print(f"NTP time data sent: {data}\n")

            #after dance start, dance data should come in, write into text file
            while True:
                message = recv_data(conn, secret_key)

                index, dancer_id, final_offset, timestamp, raw, ACCELX, ACCELY, ACCELZ, ELBOWX, ELBOWY, ELBOWZ, HANDX, HANDY, HANDZ = str(message).split('|')    #to segregate each data
                # print(f"received message from laptop:\nindex: {index}\ndancer ID: {dancer_id}\ntimestamp: {timestamp}\nraw: {raw}\nQUAT W: {QUATW}\nQUAT X: {QUATX}\nQUAT Y: {QUATY}\nQUAT Z: {QUATZ}")
                # print(f"ACCEL X: {ACCELX}\nACCEL Y: {ACCELY}\nACCELZ: {ACCELZ}\nGYRO X: {GYROX}\nGYRO Y: {GYROY}\nGYRO Z: {GYROZ}\n\n")
                # print(f"final offset: {final_offset}\n")

                data = ' '
                send_data(conn, secret_key, data)

                if raw == 'Dance Move Stop':
                    print(f"dance finished at: {final_time}")
                    break
                if raw == 'logout':
                    finish = True
                    break
                else:
                    final_time = float(timestamp) + float(final_offset)

                    file.write(f"{index},{dancer_id},{timestamp},{raw},{ACCELX},{ACCELY},{ACCELZ},{ELBOWX},{ELBOWY},{ELBOWZ},{HANDX},{HANDY},{HANDZ},{final_time}\n")

                    if onRecv is not None:
                        processed = {"index": index, "id": dancer_id, "timestamp": timestamp, "raw": raw, "accelx": ACCELX, "accely": ACCELY, "accelz": ACCELZ, "elbowx": ELBOWX, "elbowy": ELBOWY,
                                    "elbowz": ELBOWZ, "handx": HANDX, "handy": HANDY, "handz": HANDZ, "finaltime": final_time}
                        onRecv(processed)

            if finish == True:
                break
            time.sleep(0.001)

    except (ConnectionError, ConnectionRefusedError, KeyboardInterrupt):
        print(f"error, connection lost for thread {ThreadCount}")
        conn.close()
        file.close()
        #sys.exit(1)

    conn.close()
    file.close()
    print(f"connection closed for thread: {ThreadCount}")

def sync_thread(cv):
    #all thread get the same NTP timeing
    while True:
        global timex
        global num_of_nodes
        if num_of_nodes%3 == 0:
            timex = request_time()
            with cv:
                cv.notify_all()
        time.sleep(0.001)
#====================================================================================================================================================================
#padding to make the message in multiples of 16
def padding(data):
    length = 16 - (len(data) % 16)
    data = data.encode()
    data += bytes([length])*length
    #print("\t\tpadding: " + str(data))
    return data

#decrypt the message
def decrypt_message(cipher_text, key):
    #print("decrpyting message")
    decoded_message = base64.b64decode(cipher_text)
    iv = decoded_message[:16]
    cipher = AES.new(key, AES.MODE_CBC, iv)
    decrypted_message = cipher.decrypt(decoded_message[16:])    #removed the strip() function
    #print(f"{decrypted_message}")
    return decrypted_message

#encrypt the message
def encrypt_message(message, secret_key):
    #print("\t\tencrypting data")
    iv = Random.new().read(AES.block_size)
    cipher = AES.new(secret_key, AES.MODE_CBC, iv)
    encoded = base64.b64encode(iv + cipher.encrypt(message))
    #print(f"\t\tdata encrypted: {encoded}")
    return encoded

#pad the data, encrypt and send
def send_data(conn, secret_key, data):
    data = padding(data)
    data = encrypt_message(data,secret_key)
    conn.send(data)

#receive message from ultra96, decrypt, unpad and decode
def recv_data(client_socket, secret_key):
    message = client_socket.recv(1024).decode()  #wait to receive message
    message = decrypt_message(message,secret_key)
    message = message[:-message[-1]]    #remove padding
    message = message.decode('utf8')    #to remove b'1|rocketman|1.8'
    return message

#get the NTP time for synchronization
def request_time():
    c = ntplib.NTPClient()
    response = c.request('pool.ntp.org', version = 3)
    '''
    for attr in dir(response):
        print("remote.%s = %r" % (attr, getattr(response, attr)))
    datetime.fromtimestamp(response.orig_time).strftime("%A, %B %d, %Y %I:%M:%S")
    '''
    return response.orig_time
#====================================================================================================================================================================
def main():
    #hard coded for testing purposes, actual run will ask user to input
    #t1_port = input('enter port for thread1->')
    #t2_port = input('enter port for thread2->')
    #t3_port = input('enter port for thread3->')

    secret_key = b'0123456789ABCDEF'

    #create 3 threads for each of the dancer, each listening on the loopback address but on specific port
    condition = threading.Condition()
    t1 = threading.Thread(target=threaded_server,args=(8090, secret_key, 1, condition,))
    t2 = threading.Thread(target=threaded_server,args=(8091, secret_key, 2, condition,))
    t3 = threading.Thread(target=threaded_server,args=(8092, secret_key, 3, condition,))
    t4 = threading.Thread(target=sync_thread, args=(condition))

    t1.start()
    t2.start()
    t3.start()
    t4.start()

    t1.join()
    t2.join()
    t3.join()
    t4.join()

    print("done!")

if __name__ == '__main__':
    main()
