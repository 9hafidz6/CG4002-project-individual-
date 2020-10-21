#dashboard server to get data from ultra_client
import socket
import time
import pymongo
import threading
from datetime import datetime
import base64
from Crypto.Cipher import AES
from Crypto import Random
import math

from collections import deque
q = deque()

#=====================================================================================================================================

def threaded_client(secret_key):
    #create a listening socket to ultra96 client
    host = '127.0.0.1'
    port = 8079

    client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)  # TCP socket
    client_socket.connect((host, int(port)))  # connect to the server

    try:
        while client_socket.fileno() != -1:
            message = recv_data(client_socket, secret_key)
            #dancer_id1, index1, action1, position1, time1 = str(data).split('|')
            print(f"received: {message}")
            q.append(message)
            #if action1 == 'logout':
                #break
            data = ' '
            send_data(client_socket, secret_key, data)

    except (ConnectionError, ConnectionRefusedError):
        print("error, connection lost")
        client_socket.close()
    client_socket.close()  # close the connection
    file.close()
    print(f"connection closed for ultra96 thread")

#=====================================================================================================================================

#connect and send data to mongoDb atlas server for dashboard
def dashboard_client():
    #connect to dashboard MongoDB atlas
    print("connecting to MongoDB atlas")
    connection = connect_to_mongodb()

    while connection:
        flag = 1
        #if there is data in queue, send to mongodb
        while q:
            flag = data_to_send()
        if not flag:
            break
        time.sleep(0.001)
    print("connection to MongoDB closed")

#=====================================================================================================================================

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
        #get the data from the queue
        data = q.popleft()

        #dancer_id1, index1, action1, position1, time1, dancer_id2, index2, action2, position2, time2, dancer_id3, index3, action3, position3, time3 = str(data).split('|')
        dancer_id1, index1, action1, position1, time1 = str(data).split('|')

        #data = {"index": index1, "dancerId": dancer_id1, "move": action1, "position": position1, "eventDate": datetime.fromtimestamp(int(time1)).strftime("%A, %B %d, %Y %H:%M:%S")}
        data = {"index": index1, "dancerId": dancer_id1, "move": action1, "position": int(position1), "eventDate": datetime.fromtimestamp(int(time1))}
        db_predictions.insert_one(data)

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

#=====================================================================================================================================

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
    message = message.decode('utf8')    #to remove b'1|rocketman|
    return message

#=====================================================================================================================================

def main():
    secret_key = b'0123456789ABCDEF'

    #create 2 threads to listen to ultra96 and send to mongo_db
    t1 = threading.Thread(target=threaded_client, args=(secret_key,))
    t2 = threading.Thread(target=dashboard_client, args=())

    t1.start()
    t2.start()

    t1.join()
    t2.join()

    print("done!")

if __name__ == '__main__':
    main()
