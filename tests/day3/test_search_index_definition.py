from aegisap.day3.retrieval.azure_ai_search_adapter import (
    DAY3_SEMANTIC_CONFIGURATION_NAME,
    build_day3_search_index,
)


def test_build_day3_search_index_includes_semantic_configuration() -> None:
    index = build_day3_search_index("day3-evidence")

    assert index.semantic_search is not None
    assert index.semantic_search.default_configuration_name == DAY3_SEMANTIC_CONFIGURATION_NAME
    assert len(index.semantic_search.configurations) == 1

    config = index.semantic_search.configurations[0]
    assert config.name == DAY3_SEMANTIC_CONFIGURATION_NAME
    assert config.prioritized_fields.title_field.field_name == "title"
    assert [field.field_name for field in config.prioritized_fields.content_fields] == ["content"]
