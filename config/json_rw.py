import json

with open(r'.\config\files\config.json', 'r') as json_file:
    config_dict = json.load(json_file)