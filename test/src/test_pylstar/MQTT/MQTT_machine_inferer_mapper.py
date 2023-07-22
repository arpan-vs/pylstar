#!/usr/bin/env python

import subprocess
import sys
import os
import time
import socket
import json

from Mqtt import MockMqttExample

sys.path.append("../../../../src")
from pylstar.tools.Decorators import PylstarLogger
from pylstar.LSTAR import LSTAR
from pylstar.ActiveKnowledgeBase import ActiveKnowledgeBase
from pylstar.Letter import Letter, EmptyLetter
from pylstar.Word import Word
from Mapper import FunctionDecorator

class MQTTMapper:
    def __init__(self, alphabet):
        self.num = 0
        self.str = alphabet

        match alphabet:
            case 'connect':
                self.num = 100
            case 'disconnect':
                self.num = 200
            case 'publish':
                self.num = 300
            case 'subscribe':
                self.num = 400
            case 'unsubscribe':
                self.num = 500
            case default:
                pass
    def __str__(self):
        return str(self.num)
            

class MQTTMachineKnowledgeBase(ActiveKnowledgeBase):

    def __init__(self, target_host, target_port, timeout=5):
        super(MQTTMachineKnowledgeBase, self).__init__()
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
            output_letter = Letter(self._send_and_receive(s, MQTTMapper(to_send)))
        except Exception as e:
            self._logger.error(e)

        return output_letter


    def _send_and_receive(self, s, data):
        # print(str(data))
        s.sendall(str(data).encode())
        time.sleep(0.1)
        return s.recv(1024).strip()


def main():

    input_vocabulary1 = [
        'connect',
        'disconnect',
        'publish',
        'subscribe',
        'unsubscribe'    
    ]

    mqtt = MockMqttExample
    input_vocabulary2 = [
        str(FunctionDecorator(mqtt.connect)),
        str(FunctionDecorator(mqtt.disconnect)),
        str(FunctionDecorator(mqtt.subscribe, 'topic')),
        str(FunctionDecorator(mqtt.unsubscribe, 'topic')),
        str(FunctionDecorator(mqtt.publish, 'topic'))
    ]


    mqttBase = MQTTMachineKnowledgeBase("127.0.0.1", 3000)
    try:
        lstar = LSTAR(input_vocabulary1, mqttBase, max_states = 2)
        mqtt_state_machine = lstar.learn()
    except:
        print("Some Error Occured")
        
    dot_code = mqtt_state_machine.build_dot_code()

    output_file = "mqtt_machine_mapper.dot"

    with open(output_file, "w") as fd:
        fd.write(dot_code)

    print("==> MQTT machine Automata dumped in {}".format(output_file))
    print("Knowledge base stats: {}".format(mqttBase.stats))


if __name__ == "__main__":
    main()
