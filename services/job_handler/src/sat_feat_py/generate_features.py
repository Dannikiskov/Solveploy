import sys
from .sat_instance.sat_instance import SATInstance

def generate_features(cnf_path):

    satinstance = SATInstance(cnf_path, preprocess=False)

    satinstance.gen_basic_features()
    return satinstance.features_dict

