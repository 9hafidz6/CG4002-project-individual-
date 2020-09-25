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
    client_socket.connect((host, port_num))  # connect to the server
    print('connected\n')

    index = 0
    #open the csv file
    with open('xavier_elbowlock.csv', mode = 'r') as file:
        csvFile = csv.DictReader(file)

        for lines in csvFile:
            data = (f"{lines['Timestamp (ns)']}|{lines['raw']}|{lines['QUAT W']}|{lines['QUAT X']}|{lines['QUAT Y']}|{lines['QUAT Z']}|{lines['ACCEL X']}|{lines['ACCEL Y']}|{lines['ACCEL Z']}|{lines['GYRO X']}|{lines['GYRO Y']}|{lines['GYRO Z']}")
            data = data.encode()
            print(f"data sent: {data}")
            client_socket.send(data)

            if lines['raw'] == 'bye-bye':
                break

            time.sleep(0.005)
            #index += 1
    client_socket.close()
    print("python process ended")

if __name__ == '__main__':
    main()
