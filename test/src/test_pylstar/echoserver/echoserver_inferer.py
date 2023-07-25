#!/usr/bin/env python

import subprocess
import sys
import os
import time
import socket
import json


sys.path.append("../../../../src")
from pylstar.tools.Decorators import PylstarLogger
from pylstar.LSTAR import LSTAR
from pylstar.ActiveKnowledgeBase import ActiveKnowledgeBase
from pylstar.Letter import Letter, EmptyLetter
from pylstar.Word import Word

def MQTTMapper(alphabet):
    
    # def __init__(self, ):
    #     self.num = 0
    #     self.str = alphabet
    map1 = {'str':alphabet}

    match alphabet:
        case 'connect':
            map1['num'] = 100
        case 'disconnect':
            map1['num'] = 200
        case 'publish':
            map1['num'] = 300
        case 'subscribe':
            map1['num'] = 400
        case 'unsubscribe':
            map1['num'] = 500
        case default:
            pass

    return json.dumps(map1)
            

class EchoServerKnowledgeBase(ActiveKnowledgeBase):

    def __init__(self, target_host, target_port, timeout=5):
        super(EchoServerKnowledgeBase, self).__init__()
        self.target_host = target_host
        self.target_port = target_port
        self.timeout = timeout

    def start_target(self):
        pass

    def stop_target(self):
        pass

    def submit_word(self, word):

        self._logger.debug("Submiting word '{}' to the network target".format(word))

        output_letters = []

        s = socket.socket()
        # Reuse the connection
        s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        s.settimeout(self.timeout)
        s.connect((self.target_host, self.target_port))
        try:
            output_letters = [self._submit_letter(s, letter) for letter in word.letters]
        finally:
            s.close()

        return Word(letters=output_letters)

    def _submit_letter(self, s, letter):
        output_letter = EmptyLetter()
        try:
            to_send = ''.join([symbol for symbol in letter.symbols])
            output_letter = Letter(self._send_and_receive(s, to_send))
            print(output_letter)
        except Exception as e:
            self._logger.error(e)

        return output_letter


    def _send_and_receive(self, s, data):
        # print(data)
        s.sendall(data.encode())
        time.sleep(0.1)
        return s.recv(1024).strip()


def main():

    input_vocabulary = [
        'connect',
        'disconnect',
        'publish',
        'subscribe',
        'unsubscribe'    
    ]


    EchoServerBase = EchoServerKnowledgeBase("127.0.0.1", 3000)
    try:
        lstar = LSTAR(input_vocabulary, EchoServerBase, max_states = 2)
        EchoServerBase_state_machine = lstar.learn()
    except:
        print("Some Error Occured")
        
    dot_code = EchoServerBase_state_machine.build_dot_code()

    output_file = "echoserver.dot"

    with open(output_file, "w") as fd:
        fd.write(dot_code)

    print("==> MQTT machine Automata dumped in {}".format(output_file))
    print("Knowledge base stats: {}".format(EchoServerBase.stats))


if __name__ == "__main__":
    main()
