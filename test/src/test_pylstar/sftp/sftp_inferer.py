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

def SFTPINMapper(alphabet):
    buf = []
    match alphabet:
        case 'user':
            buf.append("USER ")
            buf.append('anonymous\r\n')
        case 'password':
            buf.append("PASS ")
            buf.append("\r\n")
        case 'quit':
            buf.append("QUIT")
            buf.append("\r\n")
        case 'list':
            buf.append("LIST ")
            buf.append("-al")
            buf.append("\r\n")
        case 'download':
            buf.append("RETR ")
            buf.append("ftp_server.c")
            buf.append("\r\n")
        case 'upload':
            buf.append("STOR ")
            buf.append("sftp_inferer.py")
            buf.append("\r\n")
        case 'passive_mode':
            buf.append("PASV")
    return "".join(buf)


def SFTPOUTMapper(data):
    concrete_out = {'':'-',
                    '220 Server ready\r\n221 Goodbye':'quit',
                    '220 Server ready\r\n530 Login failed! username or password is wrong\r\n550 Command not executed (null)': 'Error',
                    '220 Server ready\r\n550 Command not executed received a invalid cmd': 'Error',
                    '220 Server ready\r\n530 Login failed!': 'Error',
                    '220 Server ready\r\n331 Password required for anonymous':'Enter Password',
                    '220 Server ready\r\n530 Login failed! username or password is wrong!\r\n550 Command not executed LIST command wrong!': 'Error',
                    '220 Server ready\r\n530 Login failed! username or password is wrong\r\n550 Command not executed no such file': 'Error',
                    '221 Goodbye':'quit',
                    '230 User anonymous logged in successfully!':'Login successfully',
                    '331 Password required for anonymous':'Enter Password',
                    '530 Login failed!': 'Error2',
                    '530 Login failed! username or password is wrong\r\n550 Command not executed (null)': 'Error2',
                    '530 Login failed! username or password is wrong!\r\n550 Command not executed LIST command wrong!': 'Error2',
                    '530 Login failed! username or password is wrong\r\n550 Command not executed no such file': 'Error2',
                    '550 Command not executed (null)': 'Error3',
                    '550 Command not executed LIST command wrong!': 'Error3',
                    '550 Command not executed received a invalid cmd': 'Error3',
                    '550 Command not executed no such file': 'Error3'}
    return concrete_out[data]



class sftpMachineKnowledgeBase(ActiveKnowledgeBase):

    def __init__(self, target_host, target_port, timeout=5):
        super(sftpMachineKnowledgeBase, self).__init__()
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
            output_letter = Letter(self._send_and_receive(s, SFTPINMapper(to_send)))
        except Exception as e:
            self._logger.error(e)

        return output_letter


    def _send_and_receive(self, s, data):
        # print('input:',data)
        s.sendall(data.encode())
        time.sleep(0.1)
        outdata = s.recv(1024).decode().strip()
        # print('output:',outdata)
        # outputlist.add(outdata)
        return SFTPOUTMapper(outdata)


def main():

    input_vocabulary = [
        'user',
        'password',
        'quit',
        'list',
        'download',
        'upload',
        'passive_mode'  
    ]


    sftpBase = sftpMachineKnowledgeBase("127.0.0.1", 3000)
    try:
        lstar = LSTAR(input_vocabulary, sftpBase, max_states = 2)
        sftp_state_machine = lstar.learn()
    except:
        print("Some Error Occured")
        
    dot_code = sftp_state_machine.build_dot_code()

    output_file = "sftp_machine_mapper.dot"

    with open(output_file, "w") as fd:
        fd.write(dot_code)

    print("==> MQTT machine Automata dumped in {}".format(output_file))
    print("Knowledge base stats: {}".format(sftpBase.stats))


if __name__ == "__main__":
    main()
