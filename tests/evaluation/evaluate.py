import json
import asyncio
from pathlib import Path
from src.agents.workflow import AgentWorkflow

def bbox_area(b):
    if not b or len(b) != 4:
        return 0.0
    minx, miny, maxx, maxy = b
    w = max(0.0, maxx - minx)
    h = max(0.0, maxy - miny)
    return w * h


def bbox_intersection(a, b):
    if not a or not b or len(a) != 4 or len(b) != 4:
        return None
    ixmin = max(a[0], b[0])
    iymin = max(a[1], b[1])
    ixmax = min(a[2], b[2])
    iymax = min(a[3], b[3])
    if ixmax <= ixmin or iymax <= iymin:
        return None
    return [ixmin, iymin, ixmax, iymax]


def iou(a, b):
    inter = bbox_intersection(a, b)
    if inter is None:
        return 0.0
    inter_area = bbox_area(inter)
    a_area = bbox_area(a)
    b_area = bbox_area(b)
    denom = a_area + b_area - inter_area
    return inter_area / denom if denom > 0 else 0.0


class QueryEvaluator: 
    def __init__(self, sample_queries_path: str):
        with open(sample_queries_path, 'r') as f:
            self.sample_queries = json.load(f)
        
        self.workflow = AgentWorkflow()
    
    async def evaluate_queries(self):
        """Evaluate all the sample queries"""
        results = []

        for query_data in self.sample_queries:
            print(f"Evaluating query: {query_data['id']}")
            print(f"Query: {query_data['query']}")
            
            result = await self.workflow.run(query_data['query'])

            # compare with the expected
            evaluation = {
                "query_id": query_data['id'],
                "query": query_data['query'],
                "expected_intent": query_data.get("intent"),
                "parsed_intent": result.parsed_query.intent,
                "expected_metadata_sub_intent": query_data.get("metadata-sub-intent"),
                "parsed_metadata_sub_intent": result.parsed_query.metadata_sub_intent,
                "expected_collections": query_data.get("expected_params", {}).get("collections"),
                "parsed_collections": result.stac_search_result.collections,
                "parsed_location": result.parsed_query.location,
                "expected_location": query_data.get("expected_params", {}).get("location"),
                "expected_bbox": query_data.get("expected_params", {}).get("bbox"),
                "parsed_bbox": result.geocoding_result.bbox,
                "expected_datetime": query_data.get("expected_params", {}).get("datetime"),
                "parsed_datetime": result.geocoding_result.datetime,
            }

            results.append(evaluation)

            # timeout for 10s between queries to avoid rate limits
            await asyncio.sleep(10)
        
        # calculate metrics:
        def accuracy_metric(key: str) -> float:
            return sum(1 for r in results if r[f"expected_{key}"] == r[f"parsed_{key}"] and r[f"expected_{key}"] is not None) / len(results)
        
        intent_accuracy = accuracy_metric("intent")
        metadata_sub_intent_accuracy = accuracy_metric("metadata_sub_intent")
        collections_accuracy = accuracy_metric("collections")
        location_accuracy = accuracy_metric("location")

        # calculating Intersection over union (IoU) for bbox accuracy
        bbox_ious = [iou(r["expected_bbox"], r["parsed_bbox"]) for r in results if r["expected_bbox"] is not None and r["parsed_bbox"] is not None]
        
        datetime_accuracy = accuracy_metric("datetime")

        print(f"\nEvaluation Results:")
        print(f"\nTotal Queries Evaluated: {len(results)}")

        # accuracy metrics
        print(f"Intent Accuracy: {intent_accuracy*100:.2f}%")
        print(f"Metadata Sub-Intent Accuracy: {metadata_sub_intent_accuracy*100:.2f}%")
        print(f"Collections Accuracy: {collections_accuracy*100:.2f}%")
        print(f"BBox IoU Average: {bbox_ious and sum(bbox_ious)/len(bbox_ious) or 0.0:.2f}")
        print(f"Location Accuracy: {location_accuracy*100:.2f}%")
        print(f"Datetime Accuracy: {datetime_accuracy*100:.2f}%")

        # recall metrics
        """
        True Positive (TP): The model correctly identifies a relevant item.
        False Positive (FP): The model incorrectly identifies a non-relevant item as relevant.
        False Negative (FN): The model fails to identify a relevant item.
        True Negative (TN): The model correctly identifies a non-relevant item as non-relevant.
        """
        def recall(key: str) -> float:
            true_positive = sum(1 for r in results if r[f"expected_{key}"] == r[f"parsed_{key}"] and r[f"expected_{key}"] is not None)
            false_negative = sum(1 for r in results if r[f"expected_{key}"] != r[f"parsed_{key}"] and r[f"expected_{key}"] is not None)
            return true_positive / (true_positive + false_negative) if (true_positive + false_negative) > 0 else 0.0
        
        recall_intent = recall("intent")
        recall_metadata_sub_intent = recall("metadata_sub_intent")
        recall_collections = recall("collections")
        recall_location = recall("location")
        recall_datetime = recall("datetime")

        print(f"\nRecall Metrics:")
        print(f"\nIntent Recall: {recall_intent*100:.2f}%")
        print(f"Metadata Sub-Intent Recall: {recall_metadata_sub_intent*100:.2f}%")
        print(f"Collections Recall: {recall_collections*100:.2f}%")
        print(f"Location Recall: {recall_location*100:.2f}%")
        print(f"Datetime Recall: {recall_datetime*100:.2f}%")

        # precision metrics
        def precision(key: str) -> float:
            true_positive = sum(1 for r in results if r[f"expected_{key}"] == r[f"parsed_{key}"] and r[f"parsed_{key}"] is not None)
            false_positive = sum(1 for r in results if r[f"expected_{key}"] != r[f"parsed_{key}"] and r[f"parsed_{key}"] is not None)
            return true_positive / (true_positive + false_positive) if (true_positive + false_positive) > 0 else 0.0
        
        precision_intent = precision("intent")
        precision_metadata_sub_intent = precision("metadata_sub_intent")
        precision_collections = precision("collections")
        precision_location = precision("location")
        precision_datetime = precision("datetime")

        print(f"\nPrecision Metrics:")
        print(f"\nIntent Precision: {precision_intent*100:.2f}%")
        print(f"Metadata Sub-Intent Precision: {precision_metadata_sub_intent*100:.2f}%")
        print(f"Collections Precision: {precision_collections*100:.2f}%")
        print(f"Location Precision: {precision_location*100:.2f}%")
        print(f"Datetime Precision: {precision_datetime*100:.2f}%")

        # save results
        results_path = Path("tests/evaluation/results.json")
        with open(results_path, 'w') as f:
            json.dump(results, f, indent=4)
        
        return results
    
async def main():
    evaluator = QueryEvaluator(sample_queries_path="tests/fixtures/sample_queries.json")
    await evaluator.evaluate_queries()

if __name__ == "__main__":
    asyncio.run(main())