"""
Test script for the structured output workflow.
"""

import os

os.environ["TOKENIZERS_PARALLELISM"] = "false"

import asyncio
from src.agents.workflow import process_query
from dotenv import load_dotenv

load_dotenv()


async def main():
    # Test queries
    test_queries = [
        # "Show me rainfall data for Lagos in February 2024",
        "How much data is available for Kano from 21st March 2023 to 25th March 2023?", # this doesn't work 
        # "What was the vegetation like in Ondo State in 2021?",
        "How many rainfall items do we have for January 2023?"
    ]
    for query in test_queries:
        print(f"\n{'=' * 80}")
        print(f"TESTING QUERY: {query}")
        print(f"{'=' * 80}")
        try:
            result = await process_query(query)
            print(f"\n📊 WORKFLOW SUMMARY:")
            print(f"  - Intent: {result.parsed_query.intent}")
            print(f"  - Collections: {result.stac_search_result.collections}")
            print(f"  - BBox: {result.geocoding_result.bbox}")
            print(f"  - Datetime: {result.geocoding_result.datetime}")
            print(f"  - Items Found: {result.stac_search_result.count}")

            # wait before next query for readability
            await asyncio.sleep(5)
        except Exception as e:
            print(f"❌ Error: {e}")
            import traceback

            traceback.print_exc()


if __name__ == "__main__":
    asyncio.run(main())
