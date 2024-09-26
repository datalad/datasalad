import pytest

from ..setting import Setting


def test_setting():
    with pytest.raises(ValueError, match='callable required'):
        Setting(5, lazy=True)

    test_val = 5
    item = Setting(lambda: test_val, lazy=True)
    assert item.is_lazy is True
    assert item.value == test_val

    assert 'lambda' in str(item)

    test_val = 4
    item.update(Setting(str(test_val), coercer=int))
    assert item.is_lazy is False
    assert item.value == test_val

    item.update(Setting(coercer=float))
    assert item.value == float(test_val)


def test_setting_derived_copy():
    class MySetting(Setting):
        def __init__(self, allnew: str):
            self.allnew = allnew

    target = 'dummy'
    ms = MySetting(target)
    ms_c = ms.copy()
    assert ms_c.allnew == target

    # __eq__ considers the derived type and rejects
    assert ms != Setting(target)
