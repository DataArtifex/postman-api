import os
from pathlib import Path

import pytest
from dotenv import load_dotenv

from dartfx.postmanapi import postman


@pytest.fixture(scope="session", autouse=True)
def load_env():
    dotenv_path = Path(__file__).parent / "../.env"  # Construct path from current test file dir
    load_dotenv(dotenv_path=dotenv_path)

@pytest.fixture(scope="session")
def postman_api_key():
    key = os.environ.get('DARTFX_POSTMAN_API_KEY')
    if not key: # fallback to POSTMAN_API_KEY
        key = os.environ.get('POSTMAN_API_KEY')
    return key

@pytest.fixture(scope="module")
def postman_api(postman_api_key):
    if not postman_api_key:
        pytest.skip("Postman integration tests require POSTMAN_API_KEY or DARTFX_POSTMAN_API_KEY")

    api = postman.PostmanApi(api_key=postman_api_key)
    try:
        api.get_user_profile()
    except postman.PostmanApiError as exc:
        pytest.skip(f"Postman integration tests skipped due to invalid API key: {exc}")

    return api
