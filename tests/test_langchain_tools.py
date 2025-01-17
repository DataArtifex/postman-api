from copy import deepcopy
from dartfx.postmanapi import postman_collection
from dartfx.postmanapi.langchain import tools
from dartfx.postmanapi.langchain.tools import create_collection
import json
from langchain_core.runnables import chain
from langchain_core.tools import InjectedToolArg,tool
from langchain.globals import set_debug, set_verbose
from langchain_openai import ChatOpenAI
from langchain_groq import ChatGroq

import os
import pytest
from typing import Annotated, Generator, List

api_key = os.getenv("POSTMAN_API_KEY")

#set_debug(True)
#et_verbose(True)

@chain
def inject_postman_api_key(ai_msg):
    tool_calls = []
    for tool_call in ai_msg.tool_calls:
        tool_call_copy = deepcopy(tool_call)
        tool_call_copy["args"]["api_key"] = os.getenv("POSTMAN_API_KEY")
        tool_calls.append(tool_call_copy)
    return tool_calls    

def test_annotation_import_collection():
    #print(tools.import_collection.name)
    #print(tools.import_collection.description)
    #for k,v in tools.import_collection.args.items():
    #    print(f'{k}: {v}')
    assert tools.import_collection.name == "import_collection"
    assert tools.import_collection.description
    assert len(tools.import_collection.args) == 4

def test_invoke_get_user_profile():
    data = tools.get_user_profile.invoke({'api_key': api_key})
    print(data)
    assert data.get('id')
    assert data.get('username')
   
    
def test_invoke_get_personal_workspaces():
    data = tools.get_workspaces.invoke({'api_key': api_key, 'type': 'personal'})
    print(data)
    assert len(data) > 0

def test_tool_create_collection():
    llm_tools = [
        create_collection
    ]
    print("---\n",create_collection.get_input_schema().model_json_schema())
    print("---\n",create_collection.tool_call_schema.model_json_schema())

    llm = ChatOpenAI(model="gpt-4o", temperature=0.2)
    #llm = ChatGroq(model="mixtral-8x7b-32768")
    llm_with_tools = llm.bind_tools(llm_tools)

    response = llm_with_tools.invoke("Create a Postman collection for a 'Hello World' API.")
    #print(json.dumps(response.model_dump(),indent=4))
    with open('tests/output/test_tool_create_collection.json', 'w') as file:
        json.dump(response.model_dump(), file, indent=4)
    assert response
    
