#!/usr/bin/env python

import subprocess
import sys
import os
import time

sys.path.append("../../../../src")
from pylstar.LSTAR import LSTAR
from pylstar.NetworkActiveKnowledgeBase import NetworkActiveKnowledgeBase

class CoffeeMachineKnowledgeBase(NetworkActiveKnowledgeBase):

    def __init__(self):
        super(CoffeeMachineKnowledgeBase, self).__init__("127.0.0.1", 3000)


def main():

    input_vocabulary = [
        "REFILL_WATER",
        "REFILL_COFFEE",
        "PRESS_BUTTON_A",
        "PRESS_BUTTON_B",
        "PRESS_BUTTON_C"    
    ]
    coffeeBase = CoffeeMachineKnowledgeBase()
    try:
        lstar = LSTAR(input_vocabulary, coffeeBase, max_states = 4)
        coffee_state_machine = lstar.learn()
    except:
        print("Some Error Occured")
        
    dot_code = coffee_state_machine.build_dot_code()

    output_file = "coffee_machine_{}.dot".format(id_coffee_machine)

    with open(output_file, "w") as fd:
        fd.write(dot_code)

    print("==> Coffee machine {} Automata dumped in {}".format(id_coffee_machine, output_file))
    print("Knowledge base stats: {}".format(coffeeBase.stats))


if __name__ == "__main__":
    main()
