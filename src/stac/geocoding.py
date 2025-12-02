import os
import json
import logging
from typing import Optional, Dict, List

from azure.core.credentials import AzureKeyCredential
from azure.maps.search import MapsSearchClient
from agent_framework.azure import AzureAIAgentClient
from agent_framework.azure import AzureOpenAIResponsesClient


logger = logging.getLogger(__name__)

# Local region definitions
REGION = {
    "Nigeria": {
        "bbox": [2.31, 3.84, 15.13, 14.15],
        "aliases": {"nigeria", "ng", "naija", "federal republic of nigeria"}
    }
}

# Load state-level bounding boxes from JSON file
region_file_path = os.path.join(os.path.dirname(__file__), '../../docs/nigeria_state_bboxes.json')
with open(region_file_path, 'r') as f:
    region_file = json.load(f)

# Add each state to the REGION dict
for state, data in region_file.items():
    REGION[state] = {
        "bbox": data["bbox"],
        "pcode": data["pcode"],
        "aliases": set(data["aliases"])
    }
