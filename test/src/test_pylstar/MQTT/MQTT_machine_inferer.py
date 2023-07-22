#!/usr/bin/env python

import subprocess
import sys
import os
import time

from Mqtt import MockMqttExample

sys.path.append("../../../../src")
from pylstar.LSTAR import LSTAR
from pylstar.NetworkActiveKnowledgeBase import NetworkActiveKnowledgeBase

from Mapper import FunctionDecorator
class MQTTMachineKnowledgeBase(NetworkActiveKnowledgeBase):

    def __init__(self):
        super(MQTTMachineKnowledgeBase, self).__init__("127.0.0.1", 3000)


def main():

    input_vocabulary1 = [
        "REFILL_WATER",
        "REFILL_COFFEE",
        "PRESS_BUTTON_A",
        "PRESS_BUTTON_B",
        "PRESS_BUTTON_C"     
    ]
    # input_vocabulary1 = [
    #     'connect',
    #     'disconnect',
    #     'publish',
    #     'subscribe',
    #     'unsubscribe'    
    # ]

    mqtt = MockMqttExample
    input_vocabulary2 = [
        str(FunctionDecorator(mqtt.connect)),
        str(FunctionDecorator(mqtt.disconnect)),
        str(FunctionDecorator(mqtt.subscribe, 'topic')),
        str(FunctionDecorator(mqtt.unsubscribe, 'topic')),
        str(FunctionDecorator(mqtt.publish, 'topic'))
    ]


    mqttBase = MQTTMachineKnowledgeBase()
    try:
        lstar = LSTAR(input_vocabulary1, mqttBase, max_states = 2)
        mqtt_state_machine = lstar.learn()
    except:
        print("Some Error Occured")
        
    dot_code = mqtt_state_machine.build_dot_code()

    output_file = "mqtt_machine_2.dot"

    with open(output_file, "w") as fd:
        fd.write(dot_code)

    print("==> MQTT machine Automata dumped in {}".format(output_file))
    print("Knowledge base stats: {}".format(mqttBase.stats))


if __name__ == "__main__":
    main()
