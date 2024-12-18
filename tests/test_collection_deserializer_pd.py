import json
from dartfx.postmanapi import postman_collection_pd as pc
import os

def get_data_dir():
    script_dir = os.path.dirname(os.path.realpath(__file__))
    return os.path.join(script_dir, "data")

def get_output_dir():
    script_dir = os.path.dirname(os.path.realpath(__file__))
    return os.path.join(script_dir, "output")

def test_hello_world():
    filename = "Hello World.postman_collection.json"
    # deserialize
    filepath = os.path.join(get_data_dir(), filename)
    with open(filepath, 'r') as file:
        data = json.load(file)
    collection = pc.Collection.model_validate(data)
    print(collection)
    # check
    assert collection.info.name == "Hello World"
    assert collection.item[0].name == "Hello World"
    # serialize
    filepath = os.path.join(get_output_dir(), filename)
    collection.save(filepath)
