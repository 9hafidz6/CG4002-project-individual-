
#import datetime
from datetime import datetime
import os
import sys
import random
import time

import socket

import base64
import numpy as np
import pandas as pd
from Crypto.Cipher import AES
from Crypto import Random
import ntplib
import math
import threading

#print(f"{datetime.datetime.now()}")
data = time.time()
print(f"{data}\n")

#data1 = datetime.fromtimestamp(data).strftime("%A, %B %d, %Y %H:%M:%S")
data1 = datetime.fromtimestamp(data)
print(f"{data1}\n")

'''
import collections
import pymongo
def makehash():
    return collections.defaultdict(makehash)
myhash = makehash()
myhash[1][1] = {'position': 3, 'action': 'test'}
myhash[1][2] = {'position': 2, 'action': 'test1'}
#myhash[index][dancer_id] = {position.....}

print(myhash[1][2]['position'])
print(myhash[1])
print(len(myhash[1]))
myhash[1] = {}
#print(myhash[1])
#print(myhash[1][2])
'''

'''
myfamily = {
  "child1" : {
    "name" : "Emil",
    "year" : 2004
  },
  "child2" : {
    "name" : "Tobias",
    "year" : 2007
  },
  "child3" : {
    "name" : "Linus",
    "year" : 2011
  }
}

for x in myfamily["child1"].values():
	print(x)

#print(myfamily["child1"]["name"])
'''
'''
x = []

x.insert(3,1)
x.insert(2,2)
x.insert(1,3)

print(x)

data = (f"{x[0]} {x[1]} {x[2]}")

print(data)
'''
