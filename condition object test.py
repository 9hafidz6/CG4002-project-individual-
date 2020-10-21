#test out the condition object for multithreaded applications with
import threading
import time
import ntplib
import sys

timex = 0
num_of_nodes = 0

def thread1(cv, num):
    global num_of_nodes
    while True:
        num_of_nodes += 1
        with cv:
            cv.wait()
            print(f"thread {num} received at time {timex}")
        time.sleep(1)

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

def main():
    condition = threading.Condition()
    try:
        t1 = threading.Thread(target=thread1, args=(condition, 1))
        t2 = threading.Thread(target=thread1, args=(condition, 2))
        t3 = threading.Thread(target=thread1, args=(condition, 3))
        t1.start()
        t2.start()
        t3.start()

        while True:
            if num_of_nodes%3 == 0:
                with condition:
                    condition.notify_all()
                    global timex
                    timex = request_time()
                    time.sleep(2)
            time.sleep(0.001)
            if num_of_nodes == 30:
                break
        t1.join()
        t2.join()
        t3.join()
    except:
        a = 0
        a += 1000
        print(a)
        print("caught keyboard exception")
    else:
        print("done!")
    finally:
        print("done!!")

if __name__ == '__main__':
    main()
