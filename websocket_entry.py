"""Runs the server or client depending on the command line arguments."""

import sys
#from homeassistant_websocket.server.__main__ import main as server_main
from homeassistant_websocket.client.__main__ import main as client_main
import json

# The user should configure in the options file whether the script should run as a server or client
'''def load_config():
    # Path to the configuration file
    config_path = '/data/options.json'
    with open(config_path, 'r') as config_file:
        config = json.load(config_file)
    return config

config = load_config()
run_type = config["run_type"]
'''
run_type = "client"

def run():
    if run_type == "server":
        return server_main()
    elif run_type == "client":
        return client_main()

if __name__ == "__main__":
    try:
        sys.exit(run())
    except KeyboardInterrupt:
        sys.exit(0)