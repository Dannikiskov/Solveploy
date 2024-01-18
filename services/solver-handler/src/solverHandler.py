import json
import subprocess
import numpy as np
import kb
import messageQueue

def solver_handler(info):
    print("Solver Handler:::", info, flush=True)
    json_info = json.dumps(info)
    messageQueue.pub_to_queue(json_info, f'api-queue-{info["identifier"]}')
    #kb.handle_instance(info.file_data)