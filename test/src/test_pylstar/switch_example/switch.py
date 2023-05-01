#!/usr/bin/env python


import socket
import sys
from _thread import * 

class TwoWaySwitch(object):
    """
    This class implements a two way switch.
    """    
    def __init__(self):
        self._switch_a = 0
        self._switch_b = 0
        self._light_on = 0

    def __press_button_a(self):

        if self._switch_a == 0:
            self._switch_a = 1
        elif self._switch_a == 1:
            self._switch_a = 0

        
        self._light_on = (self._switch_a + self._switch_b) % 2 

        if self._light_on:
            return "LIGHT IS ON"
        else:
            return "LIGHT IS OFF"

    def __press_button_b(self):

        if self._switch_b == 0:
            self._switch_b = 1
        elif self._switch_b == 1:
            self._switch_b = 0

        
        self._light_on = (self._switch_a + self._switch_b) % 2 

        if self._light_on:
            return "LIGHT IS ON"
        else:
            return "LIGHT IS OFF"

    def execute_command(self, command):
        try:
            if command is None:
                raise Exception("Command cannot be None")

            command = command.strip()

            if command == "BUTTON_A":
                return self.__press_button_a()
            elif command == "BUTTON_B":
                return self.__press_button_b()
            
        except Exception as e:
            print(e)
            return "ERROR"

        
def clientthread(conn):

    coffee_machine = TwoWaySwitch()
    #Sending message to connected client
    while True:

        order = conn.recv(1024).decode()
        if not order:
            break
        response = coffee_machine.execute_command(order)+"\n"
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

    

    
    
