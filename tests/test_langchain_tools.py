import os
from dartfx.postmanapi.langchain import tools
from dotenv import load_dotenv

load_dotenv()

api_key = os.getenv("POSTMAN_API_KEY")

def test_import_collection_annotations():
    #print(tools.import_collection.name)
    #print(tools.import_collection.description)
    #for k,v in tools.import_collection.args.items():
    #    print(f'{k}: {v}')
    assert tools.import_collection.name == "import_collection"
    assert tools.import_collection.description
    assert len(tools.import_collection.args) == 4

def test_get_user_profile():
    data = tools.get_user_profile.invoke({'api_key': api_key})
    print(data)
    assert data.get('id')
    assert data.get('username')
    
    
def test_get_personal_workspaces():
    data = tools.get_workspaces.invoke({'api_key': api_key, 'type': 'personal'})
    #print(data)
    assert len(data) > 0
