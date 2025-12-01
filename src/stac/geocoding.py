import os

from typing import Optional, Dict, List

from azure.core.credentials import AzureKeyCredential
from azure.maps.search import MapsSearchClient
from agent_framework.azure import AzureAIAgentClient
from agent_framework.azure import AzureOpenAIResponsesClient
