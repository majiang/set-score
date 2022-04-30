import gb

def test_tp():
    assert gb.get_tp12([3, 2, 1, 0]) == [tp * 12 for tp in [4, 2, 1, 0]]
    assert gb.get_tp12([2, 2, 1, 0]) == [tp * 12 for tp in [3, 3, 1, 0]]
    assert gb.get_tp12([2, 1, 1, 0]) == [48, 18, 18, 0]
    assert gb.get_tp12([2, 1, 0, 0]) == [48, 24, 6, 6]
    assert gb.get_tp12([1, 1, 0, 0]) == [36, 36, 6, 6]
    assert gb.get_tp12([1, 1, 1, 0]) == [28, 28, 28, 0]
    assert gb.get_tp12([1, 0, 0, 0]) == [tp * 12 for tp in [4, 1, 1, 1]]
    assert gb.get_tp12([0, 0, 0, 0]) == [21, 21, 21, 21]
