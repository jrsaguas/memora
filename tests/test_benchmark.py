from __future__ import annotations

from experiments.benchmark import measure


def test_benchmark_reports_compact_concept_policy():
    result = measure(20, 4)
    assert result["messages"] == 20
    assert result["nodes"]["message"] == 20
    assert result["nodes"]["concept"] > 0
    assert result["nodes"]["concept"] < result["nodes"]["message"]
    assert result["cross_chat_hits"] >= 2
    assert result["source_utf8_bytes"] > 0
    assert result["database_bytes"] > 0
    assert result["storage_bytes_per_source_byte"] > 0
    assert result["edges_per_message"] > 0
    assert result["duplicate_rate"] == 0
    assert 0 < result["concept_reduction_vs_naive_proxy"] < 1
