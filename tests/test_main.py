from src.retail.main import STAGES


def test_all_stages_listed():
    assert len(STAGES) == 10
