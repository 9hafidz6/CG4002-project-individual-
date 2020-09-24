#python process
#send data on localhost
import os
import sys
import random
import time
import socket
import csv

ACTIONS = ['zigzag', 'rocket', 'hair', 'shouldershrug', 'zigzag', 'bye-bye, close']
POSITIONS = ['1', '2', '3', '1', '2', '1']

'''
#reading from csv file, actual data
with open('xavier_elbowlock.csv', mode = 'r') as file:
    csvFile = csv.DictReader(file)
    index = 0
    for lines in csvFile:
        print(lines['Timestamp (ns)'])
        index += 1
        if index == 5:
            break
'''
#==============================================================================================================================================
'''
def main():
    #main program
    start_prompt = input('->')
    host = '127.0.0.1'
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
        time.sleep(1)
        data = (f"#{POSITIONS[index]}|{ACTIONS[index]}")
        data = data.encode()
        print(f"data sent: {data}")
        client_socket.send(data)
        time.sleep(3)
        index += 1
    client_socket.close()

if __name__ == '__main__':
    main()
'''
#==============================================================================================================================================
def main():
    #main program
    start_prompt = input('->')
    host = '127.0.0.1'
    port_num = 8081
    index = 0

    client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)  # instantiate
    client_socket.connect((host, port_num))  # connect to the server
    print('connected\n')

    index = 0
    with open('xavier_elbowlock.csv', mode = 'r') as file:
        csvFile = csv.DictReader(file)
        for lines in csvFile:
            data = "#" #might only be for the first line
            data = data.encode()
            client_socket.send(data)
            print("start flag sent")
            time.sleep(1)

            if index == 5:
                data = ("bye-bye, close")
                print(data)
                data = data.encode()
                client_socket.send(data)
                break

            data = (f"{lines['Timestamp (ns)']}|{lines['raw']}|{lines['QUAT W']}|{lines['QUAT X']}|{lines['QUAT Y']}|{lines['QUAT Z']}|{lines['ACCEL X']}|{lines['ACCEL Y']}|{lines['ACCEL Z']}|{lines['GYRO X']}|{lines['GYRO Y']}|{lines['GYRO Z']}")
            data = data.encode()
            print(f"data sent: {data}")
            client_socket.send(data)
            time.sleep(3)
            index += 1
    client_socket.close()

if __name__ == '__main__':
    main()
