import pytest

from ..setting import Setting
from ..source import (
    CachingSource,
    InMemory,
    Source,
    WritableSource,
)


class DummyCachingSource(CachingSource):
    def _load(self):
        pass


def test_inmemorysrc():
    mem = InMemory()
    assert str(mem) == 'InMemory'

    target_key = 'dummy'
    mem[target_key] = Setting('dummy')
    assert mem.getall('dummy') == (Setting('dummy'),)
    assert str(InMemory()) == 'InMemory'


def test_cachingsource():
    ds = DummyCachingSource()
    ds['mike'] = Setting('one')
    assert ds['mike'] == Setting('one')
    assert ds.get('mike') == Setting('one')
    assert str(ds) == "DummyCachingSource(mike='one')"
    assert repr(ds) == (
        'DummyCachingSource(' "{'mike': Setting('one', coercer=None, lazy=False)})"
    )

    ds.add('mike', Setting('two'))
    assert ds['mike'].value == 'two'
    assert ds.get('mike').value == 'two'
    assert ds.getall('mike') == (Setting('one'), Setting('two'))

    assert ds.getall('nothere') == (Setting(None),)
    assert ds.getall('nothere', Setting(True)) == (Setting(True),)

    ds.add('notherebefore', Setting('butnow'))
    assert ds['notherebefore'].value == 'butnow'


def test_settings_base_default_methods():
    class DummySource(Source):
        def _load(self):  # pragma: no cover
            pass

        def _reinit(self):  # pragma: no cover
            pass

        def _get_item(self, key):  # pragma: no cover
            return Setting(f'key_{key}')

        def _get_keys(self):
            return {'mykey', 'plain', 'tuple'}

    src = DummySource()
    assert 'mykey' in src
    # smoke test for __iter__
    assert set(src) == src.keys()

    assert not src.is_writable

    assert src.get('plain').value == 'key_plain'
    assert src.getall('plain') == (Setting('key_plain'),)


def test_settings_writable_not_writable():
    class DummySource(WritableSource):
        @property
        def is_writable(self):
            return False

        def _load(self):  # pragma: no cover
            pass

        def _reinit(self):  # pragma: no cover
            pass

        def _get_item(self, key):  # pragma: no cover
            raise NotImplementedError

        def _get_keys(self):
            raise NotImplementedError

        def _set_item(self):
            raise NotImplementedError

        def _del_item(self):
            raise NotImplementedError

    src = DummySource()
    with pytest.raises(RuntimeError):
        src['dummy'] = Setting('irrelevant')
