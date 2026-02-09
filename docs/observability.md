# Observability

The system uses **Azure Monitor with OpenTelemetry** for end-to-end tracing across the agent pipeline.

## Core Components

Located in `src/utils/observability.py`:

### `setup_telemetry()`

Initializes the OpenTelemetry tracing pipeline:
- Creates an `AzureMonitorTraceExporter` using the `APPLICATIONINSIGHTS_CONNECTION_STRING` environment variable
- Wraps it in a `BatchSpanProcessor` for efficient batch exporting
- Sets a global `TracerProvider`

Called at module import in `src/agents/agent_runners.py` to ensure telemetry is ready before any agent execution.

### `@traced` Decorator

A generic decorator that creates spans for any sync or async function.

```python
@traced("AgentWorkflow.run", kind=SpanKind.CLIENT)
async def run(self, query: str):
    ...
```

- Configurable `SpanKind` (defaults to `INTERNAL`, can be set to `CLIENT`)
- Handles both async and synchronous functions seamlessly

### `@traced_agent` Decorator

An advanced decorator with selective argument and output capture for agent functions.

```python
@traced_agent("agent_1_query_parser", capture_args=["user_query"], capture_output="parsed_query")
async def run_query_parser(user_query: str, ...):
    ...
```

**Parameters:**
- `span_name` — Name of the span for telemetry
- `capture_args` — List of keyword argument names to serialize and attach to the span
- `capture_output` — Specific output field name to capture

**Features:**
- Automatically serializes Pydantic models using `model_dump()`
- Handles objects with `__dict__` attribute
- Truncates serialized values to 1000 characters to prevent excessive data
- Sets span attributes using keys like `agent.arg.{name}` and `agent.output.{name}`

## Agent-Level Tracing

Each agent in `src/agents/agent_runners.py` is decorated with `@traced_agent` to capture its inputs and outputs as span attributes:

| Agent | Span Name | Captured Args | Captured Output |
|-------|-----------|---------------|-----------------|
| Query Parser | `agent_1_query_parser` | `user_query` | `parsed_query` |
| Geocoder | `agent_2_geocoding` | `location`, `datetime` | `geocoding_result` |
| STAC Coordinator | `agent_3_stac_coordinator` | `user_query`, `intent`, `collections`, `bbox`, `datetime` | `stac_result` |
| Synthesizer | `agent_4_response_synthesizer` | `user_query`, `intent`, `metadata_sub_intent`, `item_count`, `date_range`, `collections` | `final_response` |

## Workflow-Level Tracing

In `src/agents/workflow.py`:
- Uses `@traced("AgentWorkflow.run", kind=SpanKind.CLIENT)` for top-level spans
- Logs trace IDs via `format_trace_id()` for end-to-end correlation in Application Insights

## Configuration

**Required environment variable:**
```
APPLICATIONINSIGHTS_CONNECTION_STRING=<your-connection-string>
```

**Dependency:**
```
azure-monitor-opentelemetry  # in requirements/base.txt
```
