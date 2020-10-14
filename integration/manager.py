import threading

from ultra_server import threaded_server
from ultra_client import evaluation_client, dashboard_server
from ml_driver import MLDriver
# from ml_driver import MLDriverStub as MLDriver # Use when driver.py not available

#for debugging purposes
from collections import deque 

import threading
import time
import pandas as pd
import numpy as np

db_q = deque()
eval_q = deque()

# Variables needed for ML
ml_q = deque()
ml_q_has_value = threading.Semaphore(value=0)
mldriver = MLDriver()
internal_mlbuffer = deque()

def onRecvDataServer(data):
  global ml_q, ml_q_has_value
  ml_q.append(data)
  ml_q_has_value.release()
  # print(data)

def onMLReady(forEval=False, forDB=False):
  global eval_q, db_q
  newdata = None
  if forEval:
    while eval_q:
      newdata = eval_q.popleft()
      break
  elif forDB:
    while db_q:
      newdata = db_q.popleft()
      break
  else:
    print("This should not happen!")
  
  return newdata

def mlthread():
  """ Assumes data is collected sequentially in chronological order """
  global ml_q, db_q, eval_q, mldriver, internal_mlbuffer, ml_q_has_value

  # Constants
  WINDOW_SIZE = 1 # Defined in seconds
  OVERLAP_FACTOR = 0.5 # % overlap in windows
  time_to_next_compute = WINDOW_SIZE * OVERLAP_FACTOR

  SAMPLE_SIZE = WINDOW_SIZE * 20

  while True:
    while ml_q_has_value.acquire():
        # print("ML")
        data = ml_q.popleft()
        time_window_start = float(internal_mlbuffer[0]["timestamp"]) if internal_mlbuffer else float(data["timestamp"])
        timediff_s = (float(data["timestamp"]) - time_window_start) # timestamp stored in s

        # Sample size based version (Sliding window)
        while len(internal_mlbuffer) >= SAMPLE_SIZE:
          internal_mlbuffer.popleft() # Remove the oldest

        # # Sliding window buffer implemented with deque
        # while timediff_s > WINDOW_SIZE:
        #   internal_mlbuffer.popleft() # Remove the oldest
        #   time_window_start = float(internal_mlbuffer[0]["timestamp"]) if internal_mlbuffer else float(data["timestamp"])
        #   timediff_s = (float(data["timestamp"]) - time_window_start) # timestamp stored in s

        time_last_entry = float(internal_mlbuffer[-1]["timestamp"]) if internal_mlbuffer else float(data["timestamp"])
        time_to_next_compute -= float(data["timestamp"]) - time_last_entry
        internal_mlbuffer.append(data) # add the latest

        # print(f"LEN: {len(internal_mlbuffer)}")

        if time_to_next_compute < 0:  # ML activates every WINDOW_SIZE * OVERLAP_FACTOR calculated based on timestamp given
          if len(internal_mlbuffer) != SAMPLE_SIZE:
            break
          mlbuffer_list = list(internal_mlbuffer)
          action_start_time = int(float(mlbuffer_list[0]["timestamp"]))  # Round down to s
          print(f"ACTIONSTART: {action_start_time}")

          df = pd.DataFrame(mlbuffer_list)
          # ['index', 'id', 'timestamp', 'raw', 'quatx', 'quaty', 'quatz', 'accelx','accely', 'accelz', 'gyrox', 'gyroy', 'gyroz', 'finaltime']
          
          df.drop(columns=['index', 'id', 'raw', 'finaltime'], inplace=True)
          # ['timestamp', 'quatw', 'quatx', 'quaty', 'quatz', 'accelx','accely', 'accelz', 'gyrox', 'gyroy', 'gyroz']
          # Assume samples are uniformly sampled at a certain frequency TODO: Add interpolation if not giving good results
          df.drop(columns=['timestamp'], inplace=True)
          # print(df.columns)
          toinfer = df.to_numpy()
          toinfer = np.expand_dims(toinfer, axis=0)
          toinfer = np.transpose(toinfer, (2, 0, 1))
          # print(toinfer.shape)

          time_to_next_compute = WINDOW_SIZE * OVERLAP_FACTOR
          result = mldriver.compute(toinfer)
          label = int(result[0, 0])

          def getaction(index):
            """
            elbow  - 0
            hair - 1
            pushback - 2
            rocket - 3
            scarecrow - 4
            shouldershrug - 5
            windows - 6
            zigzag - 7
            """
            actions = ["elbow", "hair", "pushback", "rocket", "scarecrow", "shouldershrug", "windows", "zigzag"]
            return actions[index]

          tosend = {
            1: { 
              "index": label,
              "action": getaction(label),
              "position": 1,
              "time": action_start_time,
            }
          }

          print(f"ML RESULT: {tosend}")

          db_q.append(tosend)
          eval_q.append(tosend)
          break


def main():
  global ml_q, db_q, eval_q
  ser_addr = input('server address->')
  ser_port = input('server port->')

  ThreadCount = 0
  #hard coded for testing purposes, actual run will ask user to input
  secret_key = b'0123456789ABCDEF'

  #create 3 threads for each of the dancer, each listening on the loopback address but on specific port
  server_t1 = threading.Thread(target=threaded_server,args=(8090, secret_key, 1, onRecvDataServer))
  server_t2 = threading.Thread(target=threaded_server,args=(8091, secret_key, 2, onRecvDataServer))
  server_t3 = threading.Thread(target=threaded_server,args=(8092, secret_key, 3, onRecvDataServer))
  #might need to create another thread to communicate with ML
  #t4 = threading.Thread(target=send_to_ML, args=())

  ml_t = threading.Thread(target=mlthread, args=())

  client_t1 = threading.Thread(target=evaluation_client, args=(ser_addr, int(ser_port), secret_key, onMLReady))
  client_t2 = threading.Thread(target=dashboard_server, args=(onMLReady,))

  server_t1.start()
  server_t2.start()
  server_t3.start()
  ml_t.start()
  client_t1.start()
  client_t2.start()
  #t4.start()

  server_t1.join()
  server_t2.join()
  server_t3.join()
  client_t1.join()
  client_t2.join()
  ml_t.join()
  #t4.join()

  print("done!")

if __name__ == '__main__':
    main()
