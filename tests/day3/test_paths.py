from aegisap.common.paths import repo_root
from aegisap.day3.retrieval.interfaces import day3_data_path


def test_repo_root_and_day3_data_path_resolve_inside_checkout():
    root = repo_root(__file__)
    vendor_master = day3_data_path("structured", "vendor_master.json")

    assert (root / "pyproject.toml").exists()
    assert vendor_master.is_file()
    assert root == vendor_master.parents[3]
