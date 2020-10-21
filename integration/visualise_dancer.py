from bluepy.btle import DefaultDelegate, Peripheral, Scanner, BTLEInternalError, BTLEDisconnectError
import sys
import time
import struct
from functools import reduce
import numpy as np
import matplotlib.pyplot as plt
import threading

#python process
#send data on localhost
import sys
import random
import socket
import csv

#deque
import base64
import pandas as pd
from Crypto.Cipher import AES
from Crypto import Random
import ntplib
import math

from collections import deque
q = deque()


BLUNO_NAME		= "Bluno"
ADTYPE_NAME		= 9
SERIAL_HANDLE	= 0x25
COMMAND_HANDLE	= 0x28
ADDRESSES = ['c8:df:84:fe:4f:1f', '2c:ab:33:cc:6c:cd', ]

class BlunoDelegate(DefaultDelegate):
	def __init__(self, line3d1, line3d2):
		self.line3d1 = line3d1
		self.line3d2 = line3d2
		DefaultDelegate.__init__(self)

	def handleNotification(self, cHandle, data):
		packet = decodePacket(data)
		if packet is None:
			return
		self.line3d1.set_data_3d([6000, 6000 + packet[0][0]], [6000, 6000 + packet[0][1]], [0, packet[0][2]])
		self.line3d2.set_data_3d([0, packet[1][0], packet[2][0]], [0, packet[1][1], packet[2][1]], [0, packet[1][2], packet[2][2]])
		print(packet)
		sensor_data = {
			"ACCELX": packet[0][0],
			"ACCELY": packet[0][1],
			"ACCELZ": packet[0][2],
			"ELBOWX": packet[1][0],
			"ELBOWY": packet[1][1],
			"ELBOWZ": packet[1][2],
			"HANDX": packet[2][0],
			"HANDY": packet[2][1],
			"HANDZ": packet[2][2]
		}
		q.append(sensor_data)

# https://stackoverflow.com/a/54658860
# https://anthonychiu.xyz/2016/04/05/communication-between-raspberry-pi-and-multiple-arduinos-via-bluetooth-low-power-ble/
class BlunoThread(threading.Thread):
	def __init__(self, device):
		threading.Thread.__init__(self)
		self.device = device

	def run(self):
		global SERIAL_HANDLE
		try:
			time.sleep(1.0)
			self.device.writeCharacteristic(SERIAL_HANDLE, b'0')
			while True:
				self.device.waitForNotifications(5)
		except BTLEDisconnectError:
			print("Disconnected.")
		except BTLEInternalError:
			print("Internal Error.")

def initPeripheral(address, iface, line3d1, line3d2):
	device = None
	while device == None:
		try:
			device = Peripheral(address, iface=iface).withDelegate(BlunoDelegate(line3d1, line3d2))
		except (BTLEInternalError, BTLEDisconnectError):
			print("Failed to connect. Retrying %s" % address)
	return device


def decodePacket(packet):
	try:
		data = struct.unpack("<hhhhhhhhhBx", packet)
		if data[9] != 0xAB:
			raise ValueError("Magic number was wrong!")

		return (data[0:3], data[3:6], data[6:9], data[9])
	except (struct.error, ValueError):
		return None


def getDevices(scanner):
	devices = list(filter(lambda x:
			x.getValueText(ADTYPE_NAME)!= None
			and BLUNO_NAME in x.getValueText(ADTYPE_NAME)
			and x.connectable,
			scanner.scan(5.0)))

	if len(devices) < 2:
		return None
	elif len(devices) == 2:
		return (devices[0].addr, devices[1].addr)
	else:
		selDevices = []

		index = -1
		for i in range(len(devices)):
			print(i, devices[i].addr)
		while index < 0 or index >= len(devices):
			try:
				index = int(input("Select a device's index from the list above: "))
			except ValueError:
				index = -1
		selDevices.append(devices.pop(index))

		index = -1 # copy pasted the above because lazy tbh
		for i in range(len(devices)):
			print(i, devices[i].addr)
		while index < 0 or index >= len(devices):
			try:
				index = int(input("Select a device's index from the list above: "))
			except ValueError:
				index = -1
		selDevices.append(devices.pop(index))
		return selDevices

def dancer_thread():
	host = '127.0.0.1'
	port_num = 8081

	client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)  # TCP socket
    client_socket.connect((host, port))  # connect to the server
	try:
		while client_socket.fileno() != -1:
			while q:
				queue_data = q.popleft()

				data = (f"{time.time()}|{"Dance Move Start"}|{queue_data['ACCELX']}|{queue_data['ACCELY']}|{queue_data['ACCELZ']}|{queue_data['ELBOWX']}|{queue_data['ELBOWY']}|{queue_data['ELBOWZ']}|{queue_data['HANDX']}|{queue_data['HANDY']}|{queue_data['HANDZ']}")
				data = data.encode()
				client_socket.send(data)
				print(f"data sent: {data}")
				message = client_socket.recv(1024).decode()
			time.sleep(0.001)
	except Exception as e:
		print(f"{e}")
		client_socket.close()
		sys.exit(1)
	else:
		print("dancer thread closed")
		client_socket.close()

def main():
	#main program

	#print("Scanning for devices...")
	#devices = getDevices(s)
	#if devices is None:
	#	print("One or no devices found.")
	#	sys.exit()

	fig = plt.figure()
	ax = fig.gca(projection='3d')
	ax.axes.set_xlim3d(left=-32768, right=32768)
	ax.axes.set_ylim3d(bottom=-32768, top=32768)
	ax.axes.set_zlim3d(bottom=-32768, top=32768)
	ax.xaxis.set_ticks([])
	ax.yaxis.set_ticks([])
	ax.zaxis.set_ticks([])
	ax.set_xlabel('x')
	ax.set_ylabel('y')
	ax.set_zlabel('z')
	ax.plot([12000, 0, 1000, 11000, 12000], [0, 0, 0, 0, 0], [0, 0, -18000, -18000, 0]) # body
	ax.plot([9000, 3000, 3000, 9000, 9000], [0, 0, 0, 0, 0], [0, 0, 8000, 8000, 0]) # head
	ax.plot([14000, 11000, 1000, -2000], [0, 0, 0, 0], [-32000, -18000, -18000, -32000]) # legs
	plt.ion()
	line3d1, = ax.plot([], [], [])
	line3d2, = ax.plot([], [], [])
	t1 = BlunoThread(initPeripheral(ADDRESSES[1], 0, line3d1, line3d2))
	#t2 = BlunoThread(initPeripheral(ADDRESSES[1], 1, line3d2))
	t2 = threading.Thread(target=dancer_thread, args=())

	t1.start()
	t2.start()
	plt.draw()

	while True:
		time.sleep(0.01)
		plt.pause(0.0001)

if __name__ == "__main__":
	main()
