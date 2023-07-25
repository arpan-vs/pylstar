import socket
import threading
import sys

class Client:
  soc = socket.socket(socket.AF_INET, socket.SOCK_STREAM) # make TCP connection on IPv4
  port = 3000
  buffSize = 1024
  
  def __init__(self, ip):
    self.ip = ip
    self.soc.connect((self.ip, self.port))
    sendTh = threading.Thread(target=self.sendMessage)
    sendTh.daemon = True
    sendTh.start()

    while True:
      data = self.soc.recv(self.buffSize)
      if not data:
        break
      print(data)

  def sendMessage(self):
    while True:
      self.soc.send(bytes(input(""), 'utf-8'))

if(len(sys.argv) > 1):
  client = Client(sys.argv[1])
else:
  print("Please provide the IP of server!")