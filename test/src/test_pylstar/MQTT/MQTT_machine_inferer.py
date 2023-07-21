#!/usr/bin/env python

import subprocess
import sys
import os
import time

sys.path.append("../../../../src")
from pylstar.LSTAR import LSTAR
from pylstar.NetworkActiveKnowledgeBase import NetworkActiveKnowledgeBase

class MQTTMachineKnowledgeBase(NetworkActiveKnowledgeBase):

    def __init__(self):
        super(MQTTMachineKnowledgeBase, self).__init__("127.0.0.1", 3000)


def main():

    input_vocabulary = [
        'connect',
        'disconnect',
        'publish',
        'subscribe',
        'unsubscribe'    
    ]
    mqttBase = MQTTMachineKnowledgeBase()
    try:
        lstar = LSTAR(input_vocabulary, mqttBase, max_states = 4)
        mqtt_state_machine = lstar.learn()
    except:
        print("Some Error Occured")
        
    dot_code = mqtt_state_machine.build_dot_code()

    output_file = "mqtt_machine.dot"

    with open(output_file, "w") as fd:
        fd.write(dot_code)

    print("==> MQTT machine Automata dumped in {}".format(output_file))
    print("Knowledge base stats: {}".format(mqttBase.stats))


if __name__ == "__main__":
    main()
