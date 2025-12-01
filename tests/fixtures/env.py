import pytest


@pytest.fixture
def mock_env_vars():
    """Fixture for environment variables"""
    return {
        "AZURE_OPENAI_ENDPOINT": "https://test.openai.azure.com/",
        "AZURE_OPENAI_DEPLOYMENT_NAME": "gpt-4",
        "AZURE_OPENAI_API_VERSION": "2024-02-01",
    }
