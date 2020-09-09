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

start_time = time.clock_gettime(time.CLOCK_REALTIME)
print(start_time)
#time.sleep(2)
end_time = time.clock_gettime(time.CLOCK_REALTIME)
print(end_time)
print('time difference:' + str(end_time -start_time))

'''
# Python program to explain time.clock_settime() method

# importing time module
import time

# clk_id for System-wide real-time clock
clk_id = time.CLOCK_REALTIME


# Get the current value of
# system-wide real-time clock (in seconds)
# using time.clock_gettime() method
t = time.clock_gettime(clk_id)

print("Current value of system-wide real-time clock: % d seconds" % t)

# Set the new value of
# time (in seconds) for
# System-wide real-time clock
# using time.clock_settime() method
seconds = 10000000
time.clock_settime(clk_id,seconds)

print("\nTime modified")


# Get the modified value of
# system-wide real-time clock (in seconds)
# using time.clock_gettime() method
t = time.clock_gettime(clk_id)
print("\nCurrent value of system-wide real-time clock: % d seconds" % t)
'''
'''
import time
import ntplib

def request_time():
    c= ntplib.NTPClient()
    response = c.request('pool.ntp.org', version = 3)
    #for attr in dir(response):
        #print("remote.%s = %r" % (attr, getattr(response, attr)))
    return response.orig_time

if __name__ == '__main__':
    start_time = request_time()
    print(start_time)
    #time.sleep(1)
    end_time = request_time()
    print(end_time)
    print('time difference:' + str(end_time -start_time))
'''
