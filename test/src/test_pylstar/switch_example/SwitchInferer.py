#!/usr/bin/env python

import subprocess
import sys
import os
import time

sys.path.append("../../../../src")
from pylstar.LSTAR import LSTAR
from pylstar.NetworkActiveKnowledgeBase import NetworkActiveKnowledgeBase

class TwoWaySwitchKnowledgeBase(NetworkActiveKnowledgeBase):

    def __init__(self, executable):
        super(TwoWaySwitchKnowledgeBase, self).__init__("127.0.0.1", 3000)
        self.__sp = None
        self.__executable = executable

    def start(self):
        print("Starting switch machine target")
        coffee_path = self.__executable
        self.__sp = subprocess.Popen("/usr/bin/python3 {}".format(coffee_path), shell=True)
        time.sleep(5)
        
    def stop(self):
        print("Stoping switch machine")
        if self.__sp is not None:
            print("Coffee machine process is forced to stop")
            self.__sp.terminate()            
            self.__sp.kill()


def main():

    
    input_vocabulary = [
        "BUTTON_A",
        "BUTTON_B"   
    ]
    switchBase = TwoWaySwitchKnowledgeBase("switch.py")
    try:
        switchBase.start()
        lstar = LSTAR(input_vocabulary, switchBase, max_states = 7)
        switch_state_machine = lstar.learn()
    finally:
        switchBase.stop()
        
    dot_code = switch_state_machine.build_dot_code()

    output_file = "switch_machine.dot"

    with open(output_file, "w") as fd:
        fd.write(dot_code)

    print("==> Two Way Switch Automata dumped in {}".format(output_file))
    print("Knowledge base stats: {}".format(switchBase.stats))


if __name__ == "__main__":
    main()
