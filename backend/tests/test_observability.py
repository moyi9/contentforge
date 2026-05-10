import pytest
import asyncio
from app.observability.traces import ContentForgeTracer


@pytest.mark.asyncio
async def test_tracer_creates_spans():
    tracer = ContentForgeTracer(service_name="contentforge-test")

    with tracer.span("test_operation") as span:
        span.set_attribute("task_id", "task-1")
        span.set_attribute("agent", "planner")

    spans = tracer.get_spans()
    assert len(spans) > 0
    assert any(s.name == "test_operation" for s in spans)


@pytest.mark.asyncio
async def test_span_attributes():
    tracer = ContentForgeTracer("test-attrs")

    with tracer.span("operation_a") as span:
        span.set_attribute("duration_ms", "150")
        span.set_attribute("model", "gpt-4o")

    span = tracer.get_spans()[-1]
    assert span.attributes.get("duration_ms") == "150"
    assert span.attributes.get("model") == "gpt-4o"


@pytest.mark.asyncio
async def test_nested_spans():
    tracer = ContentForgeTracer("test-nested")

    with tracer.span("parent") as parent:
        parent.set_attribute("type", "pipeline")
        with tracer.span("child") as child:
            child.set_attribute("type", "agent_call")

    spans = tracer.get_spans()
    assert len(spans) >= 2


@pytest.mark.asyncio
async def test_trace_decorator():
    tracer = ContentForgeTracer("test-decorator")

    @tracer.trace_agent("planner")
    async def my_agent(state):
        return {"result": "ok", "duration_ms": 100}

    result = await my_agent({"input": "test"})
    assert result["result"] == "ok"

    spans = tracer.get_spans()
    assert any(s.name == "planner" for s in spans)
