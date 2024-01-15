import pika
import os
import solverK8Job
import threading
import json
import time
import messageQueue
import minizinc
import sys
import re


def start_solver_selection(body):
    features = extract_features(body)

def extract_features(minizinc_content):
    model = minizinc.Model("test.mzn")
    print(model.flat())
    return
    

    


if __name__ == "__main__":
    with open(sys.argv[1], 'r') as file:
        minizinc_content = file.read()

        custom_features = extract_features(minizinc_content)
        print(custom_features)

