#ultra96 server
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

#start_count = 0

#def threaded_server(port_num, conn, secret_key, server_socket, ThreadCount):
def threaded_server(port_num, secret_key, ThreadCount):
    file = open("raw_data.txt", "a+")

    host = '127.0.0.1'
    server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)  # get instance
    try:
        server_socket.bind((host, int(port_num)))  # bind host address and port together
    except socket.error as e:
        print(str(e))
    print(f"waiting for connection on thread: {ThreadCount}")
    # configure server into listen mode
    server_socket.listen(1)

    conn, address = server_socket.accept()  # accept new connection
    #print('Connected to: ' + address[0] + ':' + str(address[1]))
    print(f"Connected to: {address[0]} : {str(address[1])} on thread: {ThreadCount}")

    try:
        while server_socket.fileno() != -1:
            finish = False
            raw = " "
            final_time = 0
            #wait for start of dance, get ntp timing and send back to get rtt and offset
            message = recv_data(conn, secret_key)
            #start_count += 1
            timestamp, raw, QUATW, QUATX, QUATY, QUATZ, ACCELX, ACCELY, ACCELZ, GYROX, GYROY, GYROZ, dancer_id = str(message).split('|')    #to segregate each data
            print(f"start message received: {message}")
            ntp_time = request_time()
            data = (f"{ntp_time}")
            send_data(conn, secret_key, data)
            print(f"NTP time data sent: {data}\n")

            #after dance start, dance data should come in, write into text file
            while True:
                message = recv_data(conn, secret_key)

                timestamp, raw, QUATW, QUATX, QUATY, QUATZ, ACCELX, ACCELY, ACCELZ, GYROX, GYROY, GYROZ, dancer_id, final_offset, index = str(message).split('|')    #to segregate each data
                print(f"received message from laptop:\nindex: {index}\ndancer ID: {dancer_id}\ntimestamp: {timestamp}\nraw: {raw}\nQUAT W: {QUATW}\nQUAT X: {QUATX}\nQUAT Y: {QUATY}\nQUAT Z: {QUATZ}")
                print(f"ACCEL X: {ACCELX}\nACCEL Y: {ACCELY}\nACCELZ: {ACCELZ}\nGYRO X: {GYROX}\nGYRO Y: {GYROY}\nGYRO Z: {GYROZ}\n\n")
                print(f"final offset: {final_offset}\n")

                final_time = float(timestamp) + float(final_offset)

                file.write(index + ',' + dancer_id + ','+ timestamp + ',' + raw + ',' + QUATW + ',' + QUATX + ',' + QUATY + ',' + QUATZ + ',' + ACCELX + ',' + ACCELY + ',' + ACCELZ + ',' + GYROX + ',' + GYROY + ',' + GYROZ + ',' + str(final_time) + '\n')

                data = ' '
                send_data(conn, secret_key, data)

                if raw == 'bye-bye':
                    #finish = True
                    print(f"dance finished at: {final_time}")
                    break

            if finish == True:
                break

    except (ConnectionError, ConnectionRefusedError):
        print("error, connection lost")
        conn.close()
        file.close()
        sys.exit(1)

    conn.close()  # close the connection
    file.close()
    print(f"connection closed for thread: {ThreadCount}")

#====================================================================================================================================================================
def padding(data):
    #padding to make the message in multiples of 16
    length = 16 - (len(data) % 16)
    data = data.encode()
    data += bytes([length])*length
    #print("\t\tpadding: " + str(data))
    return data

def decrypt_message(cipher_text, key):
    #print("decrpyting message")
    decoded_message = base64.b64decode(cipher_text)
    iv = decoded_message[:16]
    cipher = AES.new(key, AES.MODE_CBC, iv)
    decrypted_message = cipher.decrypt(decoded_message[16:])    #removed the strip() function
    #print(f"{decrypted_message}")
    return decrypted_message

def encrypt_message(message, secret_key):
    #encrypt messages
    #print("\t\tencrypting data")
    iv = Random.new().read(AES.block_size)
    cipher = AES.new(secret_key, AES.MODE_CBC, iv)
    encoded = base64.b64encode(iv + cipher.encrypt(message))
    #print(f"\t\tdata encrypted: {encoded}")
    return encoded

def send_data(conn, secret_key, data):
    data = padding(data)
    data = encrypt_message(data,secret_key)
    conn.send(data)

def recv_data(client_socket, secret_key):
    message = client_socket.recv(1024).decode()  #wait to receive message
    message = decrypt_message(message,secret_key)
    message = message[:-message[-1]]    #remove padding
    message = message.decode('utf8')    #to remove b'1|rocketman|
    return message

def request_time():
    c = ntplib.NTPClient()
    response = c.request('pool.ntp.org', version = 3)
    #for attr in dir(response):
        #print("remote.%s = %r" % (attr, getattr(response, attr)))
    #datetime.fromtimestamp(response.orig_time).strftime("%A, %B %d, %Y %I:%M:%S")
    return response.orig_time
#====================================================================================================================================================================
def main():
    ThreadCount = 0
    #hard coded for testing purposes, actual run will ask user to input
    secret_key = b'0123456789ABCDEF'

    #create 3 threads for each of the dancer, each listening on the loopback address but on specific port
    t1 = threading.Thread(target=threaded_server,args=(8090, secret_key, 1))
    t2 = threading.Thread(target=threaded_server,args=(8091, secret_key, 2))
    t3 = threading.Thread(target=threaded_server,args=(8092, secret_key, 3))
    #might need to create another thread to communicate with ML

    t1.start()
    t2.start()
    t3.start()

    t1.join()
    t2.join()
    t3.join()

    print("done!")

if __name__ == '__main__':
    main()
