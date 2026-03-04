# Adding observability using Azure Monitor OpenTelemetry Exporter
import asyncio
import json
import os
from functools import wraps
from typing import List

import dotenv
from azure.monitor.opentelemetry.exporter import AzureMonitorTraceExporter
from opentelemetry import trace
from opentelemetry.sdk.trace import TracerProvider
from opentelemetry.sdk.trace.export import BatchSpanProcessor
from opentelemetry.trace import SpanKind

dotenv.load_dotenv()


def setup_telemetry():
    # create the exporter with just the connection string
    exporter = AzureMonitorTraceExporter(
        connection_string=os.environ["APPLICATIONINSIGHTS_CONNECTION_STRING"]
    )

    # create and configure the tracer provider
    provider = TracerProvider()
    provider.add_span_processor(BatchSpanProcessor(exporter))

    # set as global default
    trace.set_tracer_provider(provider)


def traced(span_name: str, kind: SpanKind = SpanKind.INTERNAL):
    def decorator(func):
        @wraps(func)
        async def async_wrapper(*args, **kwargs):
            tracer = trace.get_tracer(__name__)
            with tracer.start_as_current_span(span_name, kind=kind):
                return await func(*args, **kwargs)

        @wraps(func)
        def sync_wrapper(*args, **kwargs):
            tracer = trace.get_tracer(__name__)
            with tracer.start_as_current_span(span_name, kind=kind):
                return func(*args, **kwargs)

        return async_wrapper if asyncio.iscoroutinefunction(func) else sync_wrapper

    return decorator


def traced_agent(
    span_name: str,
    capture_args: List[str] | None = None,
    capture_output: str | None = None,
):
    def decorator(func):
        @wraps(func)
        async def async_wrapper(*args, **kwargs):
            tracer = trace.get_tracer(__name__)
            with tracer.start_as_current_span(
                span_name, kind=SpanKind.INTERNAL
            ) as span:
                # capture specified args
                if capture_args:
                    for arg_name in capture_args:
                        if arg_name in kwargs:
                            value = kwargs[arg_name]
                            span.set_attribute(
                                f"agent.arg.{arg_name}", _serialize_args(value)
                            )

                result = await func(*args, **kwargs)

                if capture_output:
                    span.set_attribute(
                        f"agent.output.{capture_output}", _serialize_args(result)
                    )

                return result

        @wraps(func)
        def sync_wrapper(*args, **kwargs):
            tracer = trace.get_tracer(__name__)
            with tracer.start_as_current_span(
                span_name, kind=SpanKind.INTERNAL
            ) as span:
                if capture_args:
                    for arg_name in capture_args:
                        if arg_name in kwargs:
                            value = kwargs[arg_name]
                            span.set_attribute(
                                f"agent.arg.{arg_name}", _serialize_args(value)
                            )

                result = func(*args, **kwargs)

                if capture_output and result is not None:
                    span.set_attribute(
                        f"agent.output.{capture_output}", _serialize_args(result)
                    )

                return result

        return async_wrapper if asyncio.iscoroutinefunction(func) else sync_wrapper

    return decorator


def _serialize_args(value, max_length: int = 1000) -> str:
    """Serialize argument values for tracing."""
    if hasattr(value, "model_dump"):
        serialized = json.dumps(value.model_dump(), default=str)
    elif hasattr(value, "__dict__"):
        serialized = json.dumps(value.__dict__, default=str)
    else:
        serialized = str(value)

    return serialized[:max_length] if len(serialized) > max_length else serialized
