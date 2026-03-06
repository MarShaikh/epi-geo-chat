"""Tests for Pydantic models across the codebase — schemas, agent models, and API contracts."""

import pytest
from pydantic import ValidationError

from src.agents.query_parser import ParsedQuery
from src.agents.geocoding_temporal import GeocodingResult
from src.agents.stac_coordinator import STACSearchResult, STACItem
from src.api.schemas import ChatRequest, StreamEvent


# ---------------------------------------------------------------------------
# ParsedQuery
# ---------------------------------------------------------------------------


class TestParsedQuery:

    def test_valid_data_search(self):
        pq = ParsedQuery(
            intent="data_search",
            data_type_keywords=["rainfall"],
            location="Lagos",
            datetime="February 2024",
        )
        assert pq.intent == "data_search"
        assert pq.metadata_sub_intent is None
        assert pq.location == "Lagos"

    def test_valid_metadata_query(self):
        pq = ParsedQuery(
            intent="metadata_query",
            metadata_sub_intent="list_collections",
            data_type_keywords=[],
        )
        assert pq.metadata_sub_intent == "list_collections"

    def test_missing_required_intent(self):
        with pytest.raises(ValidationError):
            ParsedQuery(data_type_keywords=["rainfall"])

    def test_missing_required_keywords(self):
        with pytest.raises(ValidationError):
            ParsedQuery(intent="chat")

    def test_optional_fields_default_none(self):
        pq = ParsedQuery(intent="chat", data_type_keywords=[])
        assert pq.location is None
        assert pq.datetime is None
        assert pq.additional_params is None
        assert pq.metadata_sub_intent is None

    def test_serialization_round_trip(self):
        pq = ParsedQuery(
            intent="analysis",
            data_type_keywords=["NDVI", "vegetation"],
            location="Kano",
            datetime="2023",
        )
        data = pq.model_dump()
        restored = ParsedQuery(**data)
        assert restored == pq


# ---------------------------------------------------------------------------
# GeocodingResult
# ---------------------------------------------------------------------------


class TestGeocodingResult:

    def test_valid_result(self):
        gr = GeocodingResult(
            bbox=[3.0, 6.0, 4.0, 7.0],
            datetime="2024-02-01T00:00:00Z/2024-02-28T23:59:59Z",
            location_source="azure_maps",
        )
        assert gr.bbox == [3.0, 6.0, 4.0, 7.0]
        assert gr.location_source == "azure_maps"

    def test_all_none(self):
        gr = GeocodingResult()
        assert gr.bbox is None
        assert gr.datetime is None
        assert gr.location_source is None

    def test_serialization_round_trip(self):
        gr = GeocodingResult(
            bbox=[2.5, 5.5, 3.5, 6.5],
            datetime="2024-01-01T00:00:00Z",
            location_source="local",
        )
        data = gr.model_dump()
        restored = GeocodingResult(**data)
        assert restored == gr


# ---------------------------------------------------------------------------
# STACItem / STACSearchResult
# ---------------------------------------------------------------------------


class TestSTACItem:

    def test_valid_item(self):
        item = STACItem(
            id="item-001",
            datetime="2024-02-15T00:00:00Z",
            assets=["COG", "metadata"],
        )
        assert item.id == "item-001"
        assert len(item.assets) == 2

    def test_missing_required_field(self):
        with pytest.raises(ValidationError):
            STACItem(id="item-001", datetime="2024-02-15T00:00:00Z")  # missing assets


class TestSTACSearchResult:

    def test_minimal_result(self):
        result = STACSearchResult(
            count=0,
            collections=["coll-1"],
            date_range="Unspecified",
        )
        assert result.count == 0
        assert result.items is None
        assert result.bbox_searched is None

    def test_full_result(self):
        item = STACItem(
            id="item-001",
            datetime="2024-02-15T00:00:00Z",
            assets=["COG"],
        )
        result = STACSearchResult(
            count=1,
            description="Rainfall data",
            keywords=["precipitation"],
            license="CC-BY-4.0",
            collections=["chirps-rainfall"],
            date_range="2024-02-01 to 2024-02-28",
            items=[item],
            bbox_searched=[3.0, 6.0, 4.0, 7.0],
        )
        assert len(result.items) == 1
        assert result.items[0].id == "item-001"

    def test_serialization_round_trip(self):
        result = STACSearchResult(
            count=5,
            collections=["coll-a", "coll-b"],
            date_range="2024-01-01 to 2024-06-30",
            items=[
                STACItem(id="i1", datetime="2024-01-01T00:00:00Z", assets=["COG"]),
            ],
        )
        data = result.model_dump()
        restored = STACSearchResult(**data)
        assert restored == result


# ---------------------------------------------------------------------------
# ChatRequest
# ---------------------------------------------------------------------------


class TestChatRequest:

    def test_valid_request(self):
        req = ChatRequest(query="Show me rainfall data for Lagos")
        assert req.query == "Show me rainfall data for Lagos"
        assert req.session_id is None

    def test_with_session_id(self):
        req = ChatRequest(query="hello", session_id="sess-123")
        assert req.session_id == "sess-123"

    def test_empty_query_rejected(self):
        with pytest.raises(ValidationError):
            ChatRequest(query="")

    def test_query_too_long_rejected(self):
        with pytest.raises(ValidationError):
            ChatRequest(query="x" * 1001)

    def test_missing_query_rejected(self):
        with pytest.raises(ValidationError):
            ChatRequest()


# ---------------------------------------------------------------------------
# StreamEvent
# ---------------------------------------------------------------------------


class TestStreamEvent:

    def test_minimal_event(self):
        event = StreamEvent(event="done")
        assert event.event == "done"
        assert event.agent is None
        assert event.data is None

    def test_full_event(self):
        event = StreamEvent(
            event="agent_completed",
            agent="QueryParser",
            step=1,
            data={"intent": "data_search"},
            message="Parsed query",
        )
        assert event.step == 1
        assert event.data["intent"] == "data_search"
