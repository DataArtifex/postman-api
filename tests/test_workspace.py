from datetime import datetime

import pytest

from dartfx.postmanapi import postman

WORKSPACE_ID = "194dd33d-438d-47e1-ae69-e2ab5b414beb"


def get_workspace(api: postman.PostmanApi, workspace_id: str = WORKSPACE_ID) -> postman.WorkspaceManager:
    ws = postman.WorkspaceManager(api, workspace_id)
    return ws


def get_collection(api: postman.PostmanApi, index: int = 0) -> postman.CollectionManager:
    ws = get_workspace(api)
    collection_stub = ws.collections[index]
    collection = postman.CollectionManager(api, collection_stub["id"])
    return collection


def test_workspace_properties(postman_api):
    ws = get_workspace(postman_api)
    assert ws.id is not None
    assert ws.name is not None
    assert ws.type is not None
    assert ws.visibility is not None
    assert ws.created_by is not None
    assert ws.updated_by is not None
    assert ws.created_at is not None
    assert isinstance(ws.created_at, datetime)
    assert ws.updated_at is not None


def test_workspace_tags(postman_api):
    ws = get_workspace(postman_api)
    assert isinstance(ws.tags, list)


def test_workspace_global_variables(postman_api):
    ws = get_workspace(postman_api)
    assert isinstance(ws.global_variables, list)


def test_collection_properties(postman_api):
    collection = get_collection(postman_api)
    assert collection.info is not None
    assert collection.id == collection.info.get("_postman_id")


@pytest.mark.skip(reason="reactivate as needed")
def test_create_delete_workspace(postman_api):
    api = postman_api
    id = api.create_workspace("test_workspace", "personal")
    api.delete_workspace(id)
