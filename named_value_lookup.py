import os, json

name_lookup = {}
value_lookup = {}
path = "static_db/gg_revelator/named_values/"
for filename in os.listdir(path):
    command_name = filename.replace(".json", "")
    data = json.loads(open(path + filename).read())
    name_lookup[command_name] = data
    value_lookup[command_name] = {v: k for k, v in data.iteritems()}

def name_for_value(command, value):
    return name_lookup.get(str(command), {}).get(str(value))

def value_for_name(command, name):
    return value_lookup.get(str(command), {}).get(str(name))
