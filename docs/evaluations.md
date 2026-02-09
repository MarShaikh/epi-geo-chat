# Evaluations

A custom evaluation framework validates the agent pipeline against a **golden dataset** of annotated queries.

## Golden Dataset

**File:** `tests/fixtures/sample_queries.json`

Contains 8 test queries covering varying difficulty levels (easy, medium, hard). Each query includes:
- Expected intent and sub-intent
- Expected collections
- Expected location, bounding box, and datetime

### Query Schema

```json
{
  "id": "q001",
  "query": "Show me rainfall in Lagos for February 2024",
  "intent": "data_search",
  "metadata-sub-intent": null,
  "expected_params": {
    "location": "Lagos",
    "collections": ["Nigeria-CHIRPS"],
    "bbox": [3.0, 6.4, 3.7, 6.7],
    "datetime": "2024-02-01/2024-02-29"
  },
  "difficulty": "easy"
}
```

### Coverage

The dataset covers scenarios including:
- Simple spatial + temporal queries (rainfall in Lagos)
- Metadata queries with collections
- Multi-intent queries (compare coverage)
- Landmark-based locations (Murtala Muhammed Airport)
- Data quality metadata queries
- Time series analysis (Port Harcourt rainfall)
- Ambiguous temporal references (Lagos last summer)
- Metadata list queries (all datasets for Nigeria)

## Evaluator

**File:** `tests/evaluation/evaluate.py`

The `QueryEvaluator` class:
1. Loads sample queries from the golden dataset JSON
2. Iterates through queries with 10-second delays to avoid rate limiting
3. Executes the full agent workflow for each query
4. Compares outputs against expected values

## Metrics

### Accuracy (Exact Match)

Calculated per field:
- Intent Accuracy
- Metadata Sub-Intent Accuracy
- Collections Accuracy
- Location Accuracy
- Datetime Accuracy

### Bounding Box IoU

Uses Intersection over Union to compare expected vs. parsed bounding boxes:
- `bbox_area()` — Calculates area of a bounding box
- `bbox_intersection()` — Computes intersection area of two bounding boxes
- `iou()` — Computes IoU score (0.0 to 1.0)

### Precision

Calculated per field: `TP / (TP + FP)`

### Recall

Calculated per field: `TP / (TP + FN)`

## Results

Results are stored in `tests/evaluation/results.json`. Each entry includes:

```json
{
  "query_id": "q001",
  "query": "...",
  "expected_intent": "data_search",
  "parsed_intent": "data_search",
  "expected_collections": ["Nigeria-CHIRPS"],
  "parsed_collections": ["Nigeria-CHIRPS"],
  "expected_bbox": [3.0, 6.4, 3.7, 6.7],
  "parsed_bbox": [2.70, 6.37, 4.35, 6.70],
  "expected_datetime": "2024-02-01/2024-02-29",
  "parsed_datetime": "2024-02-01/2024-02-29"
}
```

## Running Evaluations

```bash
python tests/evaluation/evaluate.py
```

Output includes accuracy, precision, recall per field, and average bounding box IoU.
