# Adding observability using Azure Monitor OpenTelemetry Exporter
import dotenv
import os
import asyncio
from functools import wraps

from azure.monitor.opentelemetry.exporter import AzureMonitorTraceExporter
from opentelemetry import trace
from opentelemetry.sdk.trace import TracerProvider
from opentelemetry.sdk.trace.export import BatchSpanProcessor
from opentelemetry.trace import SpanKind

dotenv.load_dotenv()

def setup_telemetry():
    # create the exporter with just the connection string
    exporter = AzureMonitorTraceExporter(
        connection_string = os.environ["APPLICATIONINSIGHTS_CONNECTION_STRING"]
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
