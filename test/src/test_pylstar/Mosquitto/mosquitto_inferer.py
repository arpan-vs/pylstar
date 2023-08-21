#!/usr/bin/env python

import subprocess
import sys
import os
import time
import socket
import json
import random


sys.path.append("../../../../src")
from pylstar.tools.Decorators import PylstarLogger
from pylstar.LSTAR import LSTAR
from pylstar.ActiveKnowledgeBase import ActiveKnowledgeBase
from pylstar.Letter import Letter, EmptyLetter
from pylstar.Word import Word

def MQTTMapper(client, alphabet):
    
    import util

    match alphabet:
        case 'connect':
            x = client.connect(util.mqtt_host["hostname"], util.mqtt_host["port"], 60)
            return "connect_ack" if x == 0 else "connect_fail"
        case 'disconnect':
            x = client.disconnect()
            return "disconnect_ack" if x == 0 else "disconnect_fail"
        # case 'publish':
        #     map1['num'] = 300
        case 'subscribe':
            x = client.subscribe(util.topic_name + str(random.random()))[0]
            return "subscribe_ack" if x == 0 else "subscribe_fail"
        case 'unsubscribe':
            x = client.unsubscribe(util.topic_name + str(random.random()))[0]
            return "unsubscribe_ack" if x == 0 else "unsubscribe_fail"
        case default:
            pass

    # return json.dumps(map1)
            

class MQTTMachineKnowledgeBase(ActiveKnowledgeBase):

    def __init__(self, client, timeout=5):
        super(MQTTMachineKnowledgeBase, self).__init__()
        self.client = client
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
            output_letters = [self._submit_letter(0, letter) for letter in word.letters]
        except:
            pass
        # finally:
        #     break
            # s.close()

        return Word(letters=output_letters)

    def _submit_letter(self, s, letter):
        output_letter = EmptyLetter()
        try:
            to_send = ''.join([symbol for symbol in letter.symbols])
            answer = MQTTMapper(self.client, to_send)
            time.sleep(0.5)
            print(to_send,':',answer)
            output_letter = Letter(answer)
        except Exception as e:
            self._logger.error(e)

        return output_letter


    # def _send_and_receive(self, s, data):
    #     print(data)
    #     s.sendall(data.encode())
    #     time.sleep(0.1)
    #     return s.recv(1024).strip()


def main():

    input_vocabulary1 = [
        # 'connect',
        'disconnect',
        # 'publish',
        'subscribe',
        'unsubscribe'    
    ]

    import util
    import paho.mqtt.client as mqtt
    client = mqtt.Client()
    client.on_connect = util.on_connect
    client.on_message = util.on_message
    client.on_subscribe = util.on_subscribe
    client.on_disconnect = util.on_disconnect
    mqttBase = MQTTMachineKnowledgeBase(client)
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
