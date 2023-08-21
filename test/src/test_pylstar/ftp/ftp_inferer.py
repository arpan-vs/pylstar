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

import ftplib

def FTPINMapper(ftp, alphabet):
    # from ftplib import FTP
    # ftp = FTP('ftp.us.debian.org')
    # ftp.login()

    response = ''
    match alphabet:
        case 'login':
            try:
                response = ftp.login()
            except ftplib.error_perm as err:
                # return
                response = "error"
        # case 'cd':
        #     try:
        #         response = ftp.cwd('debian')
        #     except:
        #         response = "error"
        # case 'write':
        #     try:
        #         with open('README', 'wb') as fp:
        #             response = ftp.retrbinary('RETR README', fp.write)
        #     except ftplib.error_perm as err:
        #         response = err
        case 'quit':
            try:
                response = ftp.quit()
            except:
                response = 'quit failed'
    # ftp.quit()
    return response            




class ftpMachineKnowledgeBase(ActiveKnowledgeBase):

    def __init__(self, ftp, timeout=5):
        super(ftpMachineKnowledgeBase, self).__init__()

        # from ftplib import FTP
        self.target_host = ftp
        self.target_host
        self.timeout = timeout

    def start_target(self):
        pass

    def stop_target(self):
        pass

    def submit_word(self, word):

        self._logger.debug("Submiting word '{}' to the network target".format(word))

        output_letters = []

        # s = socket.socket()
        # # Reuse the connection
        # s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        # s.settimeout(self.timeout)
        # s.connect((self.target_host, self.target_port))
        try:
            # self.target_host.login()
            output_letters = [self._submit_letter(letter) for letter in word.letters]
        except:
            pass
        finally:
            print("Session CLosed")          # s.close()
            # self.target_host.quit()  

        return Word(letters=output_letters)

    def _submit_letter(self, letter):
        output_letter = EmptyLetter()
        try:
            to_send = ''.join([symbol for symbol in letter.symbols])
            output_letter = Letter(FTPINMapper(self.target_host, to_send))
            time.sleep(0.1)
            print(to_send,output_letter)
        except Exception as e:
            self._logger.error(e)

        return output_letter


    # def _send_and_receive(self, s, data):
    #     # print('input:',data)
    #     s.sendall(data.encode())
    #     time.sleep(0.1)
    #     outdata = s.recv(1024).decode().strip()
    #     # print('output:',outdata)
    #     # outputlist.add(outdata)
    #     return ftpOUTMapper(outdata)


def main():

    input_vocabulary = [
        'login',
        # 'cd',
        # 'write',
        'quit', 
    ]

    from ftplib import FTP
    ftp = FTP('ftp.us.debian.org')
    # ftp.login()
    ftpBase = ftpMachineKnowledgeBase(ftp)
    try:
        lstar = LSTAR(input_vocabulary, ftpBase, max_states = 0)
        ftp_state_machine = lstar.learn()
    except:
        print("Some Error Occured")
    # final:
    # ftp.quit()
        
    dot_code = ftp_state_machine.build_dot_code()

    output_file = "ftp_machine_mapper.dot"

    with open(output_file, "w") as fd:
        fd.write(dot_code)

    print("==> MQTT machine Automata dumped in {}".format(output_file))
    print("Knowledge base stats: {}".format(ftpBase.stats))


if __name__ == "__main__":
    main()
