from src.draft_math import snake_pick_numbers


def test_karns_pick_four():
    assert snake_pick_numbers(12, 4, 6) == [4, 21, 28, 45, 52, 69]
