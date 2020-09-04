'''from time import ctime
import time
import ntplib

ntpc = ntplib.NTPClient()
resp = ntpc.request('pool.ntp.org')
print ('Global Time: ',ctime(resp.tx_time))
print('Local Time: ',ctime())

time.sleep(5)

print ('Global Time: ',ctime(resp.tx_time))

'''

'''
import time

print(time.perf_counter())
time.sleep(5)   #sleep for 5 seconds
print(time.perf_counter())
'''

import time

print(time.clock_gettime(time.CLOCK_REALTIME))
time.sleep(5)
print(time.clock_gettime(time.CLOCK_REALTIME))
