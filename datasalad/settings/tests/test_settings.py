import sys

import pytest

from ..defaults import Defaults
from ..setting import Setting
from ..settings import Settings
from ..source import InMemory


def test_settings():
    man = Settings(
        {
            'mem1': InMemory(),
            'mem2': InMemory(),
            'defaults': Defaults(),
        }
    )

    assert list(man.sources.keys()) == ['mem1', 'mem2', 'defaults']
    assert len(man) == 0
    target_key = 'some.key'
    assert target_key not in man
    with pytest.raises(KeyError):
        man[target_key]

    man.sources['defaults'][target_key] = Setting('0', coercer=int)
    assert man[target_key].value == 0

    man.sources['mem2'][target_key] = Setting('1', coercer=float)
    man.sources['mem1'][target_key] = Setting('2')

    coerced_target = 2.0
    item = man[target_key]
    assert item.value == coerced_target
    assert item.coercer == float

    vals = man.getall(target_key)
    assert isinstance(vals, tuple)
    # one per source here
    # TODO: enhance test case to have a multi-value setting in a single source
    nsources = 3
    assert len(vals) == nsources
    assert [v.value for v in vals] == [0, 1.0, '2']

    vals = man.getall('idonotexist')
    assert isinstance(vals, tuple)
    assert vals == (Setting(None),)

    vals = man.getall('idonotexist', Setting(True))
    assert isinstance(vals, tuple)
    assert vals == (Setting(True),)

    assert man.get('idonotexist').value is None
    assert (
        man.get(
            'idonotexist',
            # makes little actual sense, but exercises a lazy
            # default setting
            Setting(
                lambda: sys.executable,
                lazy=True,
            ),
        ).value
        is sys.executable
    )
