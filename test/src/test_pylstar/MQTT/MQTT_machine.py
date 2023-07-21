#!/usr/bin/env python


import socket
import sys
from _thread import *

from Mqtt import MockMqttExample
    

class MQTTMachine(object):    
    def __init__(self):
        self.mqtt = MockMqttExample()

    def pre(self):
        self.mqtt.state = 'CONCLOSED'

    def post(self):
        self.mqtt.topics.clear()

    def execute_command(self, command):
        if command == 'connect':
                return self.mqtt.connect()
        elif command == 'disconnect':
            return self.mqtt.disconnect()
        elif command == 'publish':
            return self.mqtt.publish(topic='test')
        elif command == 'subscribe':
            return self.mqtt.subscribe(topic='test')
        else:
            return self.mqtt.unsubscribe(topic='test')


        
def clientthread(conn):

    mqtt_machine = MQTTMachine()
    #Sending message to connected client
    while True:

        order = conn.recv(1024).decode()
        if not order:
            break
        response = mqtt_machine.execute_command(order)+"\n"
        conn.sendall(response.encode())
        
def main():

    host = "127.0.0.1"
    port = 3000
    
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)    
    try:
        s.bind((host, port))
    except socket.error as msg:
        print('Bind failed. Error Code : {}'.format(msg))
        sys.exit()

    s.listen(10)
    print("Server is started and listenning")

    #now keep talking with the client
    while 1:
        #wait to accept a connection - blocking call
        conn, addr = s.accept()
        print("Connected with {}:{}".format(addr[0], addr[1]))
     
        #start new thread takes 1st argument as a function name to be run, second is the tuple of arguments to the function.
        start_new_thread(clientthread ,(conn,))
 
    s.close()    
    

if __name__ == "__main__":
    main()

    

    
    
