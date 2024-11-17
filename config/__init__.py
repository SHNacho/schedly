import yaml
import os

def load_config():
    with open(os.path.join(os.path.dirname(__file__), "config.yaml"), "r") as file:
        config = yaml.safe_load(file)
    return config

