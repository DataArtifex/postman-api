from dotenv import load_dotenv
from pathlib import Path
import pytest

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
    api = postman.PostmanApi(api_key=postman_api_key)
    return api