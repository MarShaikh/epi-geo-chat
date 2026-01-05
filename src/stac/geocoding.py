import os
import json
import logging
from src.utils.logging_config import setup_logging
from dotenv import load_dotenv
from typing import Optional, Dict, List

from azure.core.credentials import AzureKeyCredential
from azure.maps.search import MapsSearchClient
from src.agents.agent_config import create_agent_client

load_dotenv()
setup_logging()
logger = logging.getLogger(__name__)

# Local region definitions
REGION = {
    "Nigeria": {
        "bbox": [2.31, 3.84, 15.13, 14.15],
        "aliases": {"nigeria", "ng", "naija", "federal republic of nigeria"},
    }
}

# Load state-level bounding boxes from JSON file
region_file_path = os.path.join(
    os.path.dirname(__file__), "../../docs/nigeria_state_bboxes.json"
)
with open(region_file_path, "r") as f:
    region_file = json.load(f)

# Add each state to the REGION dict
for state, data in region_file.items():
    REGION[state] = {
        "bbox": data["bbox"],
        "pcode": data["pcode"],
        "aliases": set(data["aliases"]),
    }


class GeoCodingService:
    """Multi-strategy geocoding service inspired by Earth Copilot's geocoding approach."""

    def __init__(self):
        maps_key = os.environ.get("AZURE_MAPS_SUBSCRIPTION_KEY")
        self.maps_client = (
            MapsSearchClient(credential=AzureKeyCredential(maps_key))
            if maps_key
            else None
        )
        self.agent_client = create_agent_client()

    async def geocode(self, location: str) -> Optional[Dict]:
        """
        Geocode a location using multiple strategies using fallback chain:
        1. Local region lookup
        2. Azure Maps geocoding
        3. OpenAI fallback

        Returns:
            {
                "name": str,
                "bbox": [min_lon, min_lat, max_lon, max_lat],
                "source": str # e.g., "local", "azure_maps", "llm"
            }
        """
        # strategy 1: Local region lookup
        result = self._local_lookup(location)
        if result:
            logger.info(f"Geocoded '{location}' using local lookup.")
            result["source"] = "local"
            return result

        # strategy 2: Azure Maps geocoding
        if self.maps_client:
            result = await self._azure_maps_geocode(location)
            if result:
                logger.info(f"Geocoded '{location}' using Azure Maps.")
                result["source"] = "azure_maps"
                return result

        # strategy 3: OpenAI fallback
        if self.agent_client:
            result = await self._llm_geocode(location)
            if result:
                logger.info(f"Geocoded '{location}' using LLM fallback.")
                result["source"] = "llm"
                return result

        logger.warning(f"Failed to geocode location: '{location}'")
        return None

    def _local_lookup(self, location: str) -> Optional[Dict]:
        """Check if the location matches any local region aliases."""
        loc_lower = location.lower()
        for region_name, data in REGION.items():
            if loc_lower == region_name.lower():
                return {"name": region_name, "bbox": data["bbox"]}
            if loc_lower in data.get("aliases", set()):
                return {"name": region_name, "bbox": data["bbox"]}

        logger.info(f"Local lookup found no match for '{location}'")
        return None

    async def _azure_maps_geocode(self, location: str) -> Optional[Dict]:
        """Use Azure Maps to geocode the location."""
        try:
            search_query = location
            result = (
                self.maps_client.get_geocoding(query=search_query)
                if self.maps_client
                else None
            )

            if result and result.get("features", False):
                features = result["features"]
                nigeria_bbox = REGION["Nigeria"]["bbox"]

                def bbox_inside_nigeria(bbox):
                    if not bbox or len(bbox) != 4:
                        return False
                    min_lon, min_lat, max_lon, max_lat = bbox
                    ng_min_lon, ng_min_lat, ng_max_lon, ng_max_lat = nigeria_bbox

                    # check if bbox is inside Nigeria bbox
                    return (
                        min_lon >= ng_min_lon
                        and min_lat >= ng_min_lat
                        and max_lon <= ng_max_lon
                        and max_lat <= ng_max_lat
                    )

                def is_nigeria_feature(feature):
                    props = feature.get("properties", {})
                    address = props.get("address", {})
                    country_code = (
                        address.get("countryRegion", {}).get("name", "").lower()
                    )
                    return country_code in {"nga", "ng", "nigeria"}

                nigeria_features = [f for f in features if is_nigeria_feature(f)]
                if not nigeria_features:
                    nigeria_features = [
                        f for f in features if bbox_inside_nigeria(f.get("bbox"))
                    ]

                if nigeria_features and nigeria_features[0].get("bbox", None):
                    bbox = nigeria_features[0]["bbox"]
                    min_lon, min_lat, max_lon, max_lat = bbox
                    return {
                        "name": nigeria_features[0]
                        .get("properties", {})
                        .get("address", {})
                        .get("formattedAddress", location),
                        "bbox": [min_lon, min_lat, max_lon, max_lat],
                    }

        except Exception as e:
            logger.error(f"Azure Maps geocoding error for '{location}': {e}")

        logger.info(f"Azure Maps returned no results for '{location}'")
        return None

    async def _llm_geocode(self, location: str) -> Optional[Dict]:
        """Use LLM to geocode the location as a last resort."""
        if not self.agent_client:
            return None

        prompt = f"""
        Extract the bounding box for this location: '{location}'. If the location is in Nigeria, provide the bounding box. 
        If it is ambiguous, don't assume anything and respond with None. 
        Return ONLY a JSON object in the following format: 
        {{
            "name": "<location_name>",
            "bbox": [min_lon, min_lat, max_lon, max_lat]
        }}

        Rules: 
        - Bounding box should be reasonable and ONLY located in Nigeria(not too large, not too small)
        - Use [min_lon, min_lat, max_lon, max_lat] format
        - For cities, bbox should be ~0.1-0.3 degrees 
        - For states/regions, bbox should be ~1-3 degrees
        """
        try:
            geocoding_agent = self.agent_client.create_agent(
                name="GeoCodingLLM", instructions=prompt
            )

            result = await geocoding_agent.run()
            result_str = str(result).strip()

            # remove markdown code block if present
            if result_str.startswith("```") and result_str.endswith("```"):
                # remove ```json or ``` at start and ``` at end
                result_str = result_str.split("```")[1]
                if result_str.startswith("json"):
                    result_str = result_str[4:].strip()

            result_str = result_str.replace(": None", ": null")
            parsed = json.loads(result_str)
            if "error" not in parsed and "bbox" in parsed:
                return parsed

        except Exception as e:
            logger.error(f"LLM geocoding error for '{location}': {e}")

        return None

    def get_all_regions(self) -> List[str]:
        """Return a list of all locally defined region names."""
        return list(REGION.keys())
