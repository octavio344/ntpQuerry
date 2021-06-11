#!/usr/bin/env python3
import ntplib
from time import ctime
import time
import threading
import sys
import csv
import os

results = [1]
retries = 0
delay = "15"
host = ""
alternative = ""
fileCsv = "./data.csv"

def QuerryToServer(self):
    try:
        client = ntplib.NTPClient()
        response = client.request(host)

        if not response:
            raise ntplib.NtpException('No response from NTP server.')
        print("Querry result:")
        print(ctime(response.tx_time))
        self.data[0] = response.tx_time
        logIntoCsv(ctime(response.tx_time))
        #time.sleep(args.delay)
    except (ntplib.NTPException) as e:
        if alternative =="":
            print("No response from Ntp Server retry in "+delay+" sec...")
            time.sleep(int(delay))
            QuerryToServer()
            #print("No response from Ntp main server, the alternate server was not configured...\nExiting...")
            #sys.exit(1)
        try:
            client = ntplib.NTPClient()
            response = client.request(host)

            if not response:
                raise ntplib.NtpException('No response from NTP server.')
            print("Querry result:")
            print(ctime(response.tx_time))
            self.data[0] = response.tx_time
        except (ntplib.NTPException) as e:
            print("No response from alternate Ntp server\nExiting...")
            sys.exit(1)


class ntpThread (threading.Thread):
   def __init__(self, threadID, name, counter,data):
      threading.Thread.__init__(self)
      self.threadID = threadID
      self.name = name
      self.counter = counter
      self.data = data
   def run(self):
       QuerryToServer(self)
       return

class ntpSupportThread (threading.Thread):
   def __init__(self, threadID, name, counter,data):
      threading.Thread.__init__(self)
      self.threadID = threadID
      self.name = name
      self.counter = counter
      self.data = data 
   def run(self):
       AuxiliaryCounter(self)

def AuxiliaryCounter(self):
    counter = 0
    while(counter < int(args.delay)):
        time.sleep(1)
        results[0] = results[0]+1
        timeAux = ctime(results[0])
        logIntoCsv(timeAux)
        print(timeAux)
        counter = counter + 1
    
def NtpRequest():
    
    #while 1:
        threadntp = ntpThread(1, "Thread-NTP", 1,results)
        threadntp.start()
        threadntp.join()
        threadaux = ntpSupportThread(1, "Thread-NTP-Support", 1,results)
        threadaux.start()
        threadaux.join()
        NtpRequest()


#   Esta función recibe los datos del monitoreo y los escribe en el csv (append)
def logIntoCsv(currentTime):
    ts = time.time()
    row = [currentTime,results[0],ts, results[0]-ts]
    # Abro el archivo
    with open(fileCsv, 'a', encoding='UTF8') as f:
        # crea el escritor del archivo csv
        writer = csv.writer(f)
        # escribo la row
        writer.writerow(row)

#   Esta funcion se llama al incio de la ejecucion del programa para limpiar el csv
#  anterior y establecer las cabeceras
def initCsv():

    # Checkeo si existe el archivo y si no existe entonces lo creo
    if not os.path.exists(fileCsv):
        open(fileCsv, 'a').close()
    
    row = ['Time','NtpTimeStamp','LocalTimeStamp','Delta']
    #  Una vez creado o si existe, limpio el archivo y establezco la cabezera
    with  open(fileCsv, 'w') as f:
        # crea el escritor del archivo csv
        writer = csv.writer(f)
        # escribo la cabecera
        writer.writerow(row)


if __name__ == '__main__':
    import argparse
    try: 
        parser = argparse.ArgumentParser()
        parser.add_argument("-ho","--host", help=f"IP from ntp server to query")
        parser.add_argument("-a","--alternative",help=f"IP from ntp an auxiliary server to query")
        parser.add_argument("-v","--version", help=f"Version from ntp server to query",default=3)
        parser.add_argument("-d","--delay", help=f"Delay to query in seconds",default=15)
        args = parser.parse_args()
        if not args.host:
            raise Exception('Please use -ho or -host to set the host to query!')
        host = args.host
        if args.alternative:
            alternative= args.alternative
        if int(args.delay) < 15:
            raise ntplib.NTPException('Ntp protocol does not allow queries in a period of less than 15 seconds!')
        delay= args.delay
        initCsv()    
        NtpRequest()
    except (ntplib.NTPException) as e:
        print('NTP client request error: %s', str(e))
    except KeyboardInterrupt as e:
        print('\nFor exit press one more time Ctrl^C..')
    except Exception as e:
        print(e)



