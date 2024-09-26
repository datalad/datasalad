import logging
import sys
from os.path import dirname

from ..defaults import Defaults
from ..setting import Setting


def test_defaultsrc(caplog):
    d = Defaults()
    assert str(d) == 'Defaults'

    # smoke test NO-OP method
    d.load()

    target_key = 'some.key'
    orig_value = 'mike'
    updated_value = 'allnew'

    assert target_key not in d
    assert d.get(target_key, 'default').value == 'default'
    assert d.get(target_key, Setting('default2')).value == 'default2'
    d[target_key] = Setting(orig_value)
    assert d[target_key].value == orig_value
    assert 'Resetting' not in caplog.text
    with caplog.at_level(logging.DEBUG):
        # we get a debug message when a default is reset
        d[target_key] = Setting(updated_value)
    assert 'Resetting' in caplog.text
    assert d[target_key].value == updated_value
    del d[target_key]
    assert target_key not in d

    d[target_key] = Setting(orig_value)
    assert len(d) == 1
    d.reinit()
    assert target_key not in d
    assert len(d) == 0


def test_defaultsrc_dynamic():
    d = Defaults()
    target_key = 'some.key'
    dynset = Setting(
        lambda: sys.executable,
        coercer=dirname,
        lazy=True,
    )
    assert dynset.value == dirname(sys.executable)

    d[target_key] = dynset
    item = d[target_key]
    assert item.value == dirname(sys.executable)
