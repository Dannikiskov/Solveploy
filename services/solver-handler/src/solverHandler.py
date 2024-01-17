import subprocess
import numpy as np
import kb

def solver_handler(info):
    kb.handle_instance(info.file_data)