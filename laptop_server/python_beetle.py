#python process
#send data on localhost
import os
import sys
import random
import time
import socket
import csv

#==============================================================================================================================================
def main():
    #main program
    start_prompt = input('->')
    host = '127.0.0.1'
    port_num = 8081
    index = 0

    client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)  # TCP socket
    client_socket.connect((host, port_num))  # connect to the laptop client
    print('connected\n')

    #open the csv file
    with open('xavier_elbowlock.csv', mode = 'r') as file:
        csvFile = csv.DictReader(file)

        timer1 = time.time()    #to check how long it takes to transmit the data

        for lines in csvFile:
            #data = (f"{lines['Timestamp (ns)']}|{lines['raw']}|{lines['QUAT W']}|{lines['QUAT X']}|{lines['QUAT Y']}|{lines['QUAT Z']}|{lines['ACCEL X']}|{lines['ACCEL Y']}|{lines['ACCEL Z']}|{lines['GYRO X']}|{lines['GYRO Y']}|{lines['GYRO Z']}")
            data = (f"{time.time()}|{lines['raw']}|{lines['QUAT W']}|{lines['QUAT X']}|{lines['QUAT Y']}|{lines['QUAT Z']}|{lines['ACCEL X']}|{lines['ACCEL Y']}|{lines['ACCEL Z']}|{lines['GYRO X']}|{lines['GYRO Y']}|{lines['GYRO Z']}")

            data = data.encode()
            client_socket.send(data)
            print(f"data sent: {data}")

            message = client_socket.recv(1024).decode()

            if lines['raw'] == 'bye-bye':
                break

        timer2 = time.time()
        end_time = timer2 - timer1

    client_socket.close()
    print(f"python process ended in {end_time} seconds")

if __name__ == '__main__':
    main()
