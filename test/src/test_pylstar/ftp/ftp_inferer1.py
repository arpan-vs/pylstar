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

def ftpINMapper(alphabet):
    buf = []
    match alphabet:
        case 'user':
            buf.append("admin")
        case 'password':
            buf.append("password")
        case 'quit':
            buf.append("QUIT")
        case 'list':
            buf.append("LIST")
        case 'pwd':
            buf.append("PWD")
        case 'help':
            buf.append("HELP")
        case 'download':
            buf.append("RETR ")
            buf.append("ftp_server.c")
            buf.append("\r\n")
        case 'upload':
            buf.append("STOR ")
            buf.append("ftp_inferer.py")
            buf.append("\r\n")
        case 'passive_mode':
            buf.append("PASV")
    return "".join(buf)


def ftpOUTMapper(data):
    return
    # return concrete_out[data]



class ftpMachineKnowledgeBase(ActiveKnowledgeBase):

    def __init__(self, target_host, target_port, timeout=5):
        super(ftpMachineKnowledgeBase, self).__init__()
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
            output_letter = Letter(self._send_and_receive(s, ftpINMapper(to_send)))
        except Exception as e:
            self._logger.error(e)

        return output_letter


    def _send_and_receive(self, s, data):
        print('input:',data)
        s.sendall(data.encode())
        time.sleep(0.1)
        outdata = s.recv(1024).decode().strip()
        print('output:',outdata)
        # outputlist.add(outdata)
        return outdata


def main():

    input_vocabulary = [
        'user',
        'password',
        'quit',
        'pwd',
        'help',
        # 'list',
        # 'download',
        # 'upload',
        # 'passive_mode'  
    ]


    ftpBase = ftpMachineKnowledgeBase("127.0.0.1", 21)
    try:
        lstar = LSTAR(input_vocabulary, ftpBase, max_states = 2)
        ftp_state_machine = lstar.learn()
    except:
        print("Some Error Occured")
        exit()
        
    dot_code = ftp_state_machine.build_dot_code()

    output_file = "ftp_machine_mapper.dot"

    with open(output_file, "w") as fd:
        fd.write(dot_code)

    print("==> MQTT machine Automata dumped in {}".format(output_file))
    print("Knowledge base stats: {}".format(ftpBase.stats))


if __name__ == "__main__":
    main()
