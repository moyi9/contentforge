"""OpenTelemetry integration for ContentForge agent tracing.
Implements a lightweight tracer that can optionally bridge to OpenTelemetry SDK."""

import time
from functools import wraps
from typing import Any, Optional


class TraceSpan:
    """A recorded span with name, attributes, and timing."""

    def __init__(self, name: str, parent: Optional["TraceSpan"] = None):
        self.name = name
        self.attributes: dict = {}
        self.start_time = time.time()
        self.end_time: Optional[float] = None
        self.children: list["TraceSpan"] = []
        self.parent = parent

    def set_attribute(self, key: str, value: Any):
        self.attributes[key] = str(value)

    def close(self):
        self.end_time = time.time()

    @property
    def duration_ms(self) -> float:
        if self.end_time and self.start_time:
            return (self.end_time - self.start_time) * 1000
        return 0.0

    def to_dict(self) -> dict:
        return {
            "name": self.name,
            "attributes": dict(self.attributes),
            "duration_ms": round(self.duration_ms, 2),
            "start_time": round(self.start_time, 3),
            "children": [c.to_dict() for c in self.children],
        }


class ContentForgeTracer:
    """Lightweight tracer for agent operations.
    Stores spans in-memory for the task trace visualization.
    Can be upgraded to use OpenTelemetry SDK exporters."""

    def __init__(self, service_name: str = "contentforge"):
        self.service_name = service_name
        self.spans: list[TraceSpan] = []
        self._current_stack: list[TraceSpan] = []

    def span(self, name: str):
        """Context manager for creating a span."""
        return _SpanContextManager(self, name)

    def get_spans(self) -> list[TraceSpan]:
        return self.spans

    def get_span_data(self) -> list[dict]:
        """Get serializable span data for API responses."""
        return [s.to_dict() for s in self.spans]

    def trace_agent(self, agent_name: str):
        """Decorator for agent functions to automatically create spans."""

        def decorator(func):
            @wraps(func)
            async def wrapper(*args, **kwargs):
                with self.span(agent_name) as span:
                    span.set_attribute("agent", agent_name)
                    span.set_attribute("args", str(args))
                    span.set_attribute("kwargs", str(kwargs))
                    try:
                        result = await func(*args, **kwargs)
                        span.set_attribute("status", "success")
                        if isinstance(result, dict):
                            span.set_attribute(
                                "result_keys", str(list(result.keys()))
                            )
                        return result
                    except Exception as e:
                        span.set_attribute("status", "error")
                        span.set_attribute("error", str(e))
                        raise

            return wrapper

        return decorator


class _SpanContextManager:
    def __init__(self, tracer: ContentForgeTracer, name: str):
        self.tracer = tracer
        self.name = name
        self.span: Optional[TraceSpan] = None

    def __enter__(self):
        parent = (
            self.tracer._current_stack[-1] if self.tracer._current_stack else None
        )
        self.span = TraceSpan(self.name, parent)
        self.tracer.spans.append(self.span)
        if parent:
            parent.children.append(self.span)
        self.tracer._current_stack.append(self.span)
        return self.span

    def __exit__(self, exc_type, exc_val, exc_tb):
        if self.span:
            self.span.close()
        if self.tracer._current_stack:
            self.tracer._current_stack.pop()
        if exc_type:
            if self.span:
                self.span.set_attribute("error", str(exc_val))
            return False
        return True


# Module-level default tracer
tracer = ContentForgeTracer(service_name="contentforge")
