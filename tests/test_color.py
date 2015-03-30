import pytest


@pytest.mark.unit
def test_hex_to_xy():
    from bulby.color import get_xy_from_hex
    results = get_xy_from_hex('000082')

    assert results.x == 0.167
    assert results.y == 0.04
