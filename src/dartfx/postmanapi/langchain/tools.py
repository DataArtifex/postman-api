"""
Package to provide LangChain/LangGraph with tools to interact with the Postman API.

References:
- https://python.langchain.com/docs/concepts/tools
- https://python.langchain.com/docs/how_to/custom_tools/

"""
from dataclasses import Field
from typing import Annotated
from langchain_core.tools import BaseTool, InjectedToolArg, ToolException
from langchain_core.tools.base import BaseToolkit
from langchain_core.tools import tool

from ..postman import PostmanApi

class PostmanApiToolkit(BaseToolkit):
    """Toolkit for interacting with the Postman API."""
    
    def __init__(self, api_key: str):
        super().__init__()
        self.api_key = api_key
    
    def get_tools(self) -> list[BaseTool]:
        """Get the tools in the toolkit."""
        return [
            get_user_profile(), 
            get_workspaces(), 
            import_collection(),
        ]

@tool
def get_user_profile(
        api_key: Annotated[str, "The Postman API key", InjectedToolArg]
    ) -> dict:
    """Retrieves user profile associated with an API key from the Postman API.
    
    The information returned includes:
    - the user id
    - the user name
    - the user full name
    - the user email
    - link to the user avatar image
    - a flag indicating it the profile is public
    - the user team id
    - the user team name
    - the user team domain
    - the user roles 

    Example:
    {'id': 12345678, 'username': 'jdoe', 'email': 'john.doe@postman.com', 'fullName': 'John Doe', 'avatar': 'https://res.cloudinary.com/postman/image/upload/t_user_profile_300/v1657152605/user/echw9kzoxbzkj8tlbkoo.jpg', 'isPublic': True, 'teamId': 6029, 'teamName': 'Postman', 'teamDomain': 'postman', 'roles': ['user', 'flow-editor']}
    
    """
    api = PostmanApi(api_key)
    data = api.get_user_profile()
    return data



@tool
def get_workspaces(
    api_key: Annotated[str, "The Postman API key", InjectedToolArg],
    type: Annotated[str,"The workspace type: personal, private, public, team, partner"] = None, 
    created_by: Annotated[str,"The id of the user who created the workspace"] = None    
) -> list[dict]:
    """Searches for team workspaces in the Postman API.
    """
    api = PostmanApi(api_key)
    data = api.get_workspaces(type, created_by)
    return data

@tool
def import_collection(
        collection: Annotated[dict, "The collection definition as a valid JSON Postman collection"], 
        api_key: Annotated[str, "The Postman API key", InjectedToolArg], 
        workspace_id: Annotated[str, "The ID of the workspace where the collection will be imported and created", InjectedToolArg] = None, 
        collection_id: Annotated[str, "The ID of the existing collection to update", InjectedToolArg] = None,

    ) -> dict:
    """Imports, creates, updates, or replaces a valid Collection in Postman.
    """
    # The following rules apply:  
    # - A valid Postman API key must be provided.
    # - Either a workspace ID or a collection ID must be provided.
    # - If a workspace_id is provided, the collection is imported into the workspace.
    # - If collection_id is provided, the collection is assumed to exist and will be updated.
    # - The collection specification must be valid based on the latest Postman API schema.
    
    if workspace_id:
        data = create_collection(collection, api_key, workspace_id)
    elif collection_id:
        data = replace_collection(collection, api_key, collection_id)  
    else:
        raise ToolException("Either a workspace_id (create) or collection_id (update) must be provided")
    return data


@tool
def create_collection(
        collection: Annotated[str, "The Postman collection JSON document"], 
        api_key: Annotated[str, InjectedToolArg, "The Postman API key"], 
        workspace_id: Annotated[str, InjectedToolArg, "The ID of the workspace where the collection will be imported and created"]
    ) -> dict:
    """Creates a new Postman Collection.
    """
    if workspace_id == "mock":
        data = {
            "collection": {
                "id": "12ece9e1-2abf-4edc-8e34-de66e74114d2",
                "name": "Test Collection",
                "uid": "12345678-12ece9e1-2abf-4edc-8e34-de66e74114d2"
            }
        }
    else:
        api = PostmanApi(api_key)
        data = api.import_collection(workspace_id, collection)
    return data

@tool
def replace_collection(
        collection: Annotated[dict, "The collection definition as a valid Postman collection JSON document"], 
        api_key: Annotated[str, "The Postman API key", InjectedToolArg], 
        collection_id: Annotated[str, "The ID of the existing collection to update", InjectedToolArg] = None,
    ) -> dict:
    """Replaces/updates an existing Postman Collection.
    """
    if collection_id == "mock":
        data = {
            "collection": {
                "id": "12ece9e1-2abf-4edc-8e34-de66e74114d2",
                "name": "Test Collection",
                "uid": "12345678-12ece9e1-2abf-4edc-8e34-de66e74114d2"
            }
        }
    else:
        api = PostmanApi(api_key)
        data = api.replace_collection(collection_id, collection)
    return data
