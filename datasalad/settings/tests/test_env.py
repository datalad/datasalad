from collections.abc import Hashable
from os import (
    environ,
)
from os import (
    name as os_name,
)
from unittest.mock import patch

import pytest

from ..env import Environment
from ..setting import Setting


def test_envsrc():
    assert str(Environment()) == 'Environment'
    assert str(Environment(var_prefix='DATALAD_')) == 'Environment[DATALAD_]'
    assert repr(Environment()) == 'Environment()'

    # smoke test NO-OP methods
    env = Environment()
    env.reinit().load()


def test_envsrc_illegal_keys():
    env = Environment()
    # prevent any accidental modification
    with patch.dict(environ, {}):
        with pytest.raises(ValueError, match='illegal'):
            env['mustnothave=char'] = 'some'
        with pytest.raises(ValueError, match='illegal'):
            env['mustnothave\0char'] = 'some'


# traditional datalad name transformation approach
class DataladLikeEnvironment(Environment):
    def get_key_from_varname(self, name: str) -> Hashable:
        return name.replace('__', '-').replace('_', '.').casefold()

    def get_varname_from_key(self, key: Hashable) -> str:
        # note that this is not actually a real inverse transform
        return str(key).replace('.', '_').replace('-', '__').upper()


def test_envsrc_get(monkeypatch):
    target_key = 'datalad.chunky-monkey.feedback'
    target_value = 'ohmnomnom'
    absurd_must_be_absent_key = 'nobody.would.use.such.a.key'
    with monkeypatch.context() as m:
        m.setenv('DATALAD_CHUNKY__MONKEY_FEEDBACK', 'ohmnomnom')
        env = DataladLikeEnvironment(var_prefix='DATALAD_')
        assert target_key in env.keys()  # noqa: SIM118
        assert target_key in env
        assert env.get(target_key).value == target_value
        # default is wrapped into Setting if needed
        assert env.get(absurd_must_be_absent_key, target_value).value is target_value
        assert (
            env.get(absurd_must_be_absent_key, Setting(value=target_value)).value
            is target_value
        )
        # assert env.getvalue(target_key) == target_value
        # assert env.getvalue(absurd_must_be_absent_key) is None
        assert len(env)


def test_envsrc_ambiguous_keys(monkeypatch, caplog):
    target_key = 'datalad.chunky-monkey.feedback'
    target_value = 'ohmnomnom'
    with monkeypatch.context() as m:
        # define two different setting that map on the same key
        # with datalad's mapping rules
        m.setenv('DATALAD_CHUNKY__monkey_FEEDBACK', 'würg')
        m.setenv('DATALAD_CHUNKY__MONKEY_FEEDBACK', 'ohmnomnom')
        env = DataladLikeEnvironment(var_prefix='DATALAD_')
        # we still get the key's value
        assert env[target_key].value == target_value
        # negative test to make the next one count
        assert 'map on identical' not in caplog.text
        assert env.keys() == {target_key}
        # we saw a log message complaining about the ambiguous
        # key
        if os_name not in ('os2', 'nt'):
            # not testing on platforms where Python handles vars
            # in case insensitive manner
            assert (
                'Ambiguous ENV variables map on identical keys: '
                "{'datalad.chunky-monkey.feedback': "
                "['DATALAD_CHUNKY__MONKEY_FEEDBACK', "
                "'DATALAD_CHUNKY__monkey_FEEDBACK']}"
            ) in caplog.text


def test_envsrc_set():
    env = Environment()

    with patch.dict(environ, {}):
        env['some.key'] = Setting(value='mike')
        assert 'some.key' in env

    # the instance is stateless, restoring the original
    # env removes any knowledge of the key
    assert 'some.key' not in env


def test_envsrc_del():
    env = Environment()

    with patch.dict(environ, {}):
        env['some.key'] = Setting(value='mike')
        assert 'some.key' in env
        del env['some.key']
        assert 'some.key' not in env

    # the instance is stateless, restoring the original
    # env removes any knowledge of the key
    assert 'some.key' not in env


def test_envsrc_set_matching_transformed():
    env = DataladLikeEnvironment(var_prefix='DATALAD_')
    env_name = 'DATALAD_SOME_KEY'
    orig_value = 'mike'
    updated_value = 'allnew'

    with patch.dict(environ, {env_name: orig_value}):
        assert 'datalad.some.key' in env
        assert env['datalad.some.key'].value == orig_value
        env['datalad.some.key'] = Setting(updated_value)
        # the new value is set for the inverse-transformed
        # variable name
        assert environ.get(env_name) == updated_value


def test_envsrc_lowercase_keys():
    with patch.dict(environ, {}):
        env = Environment(var_prefix='myapp_')
        env['myapp_conf'] = Setting(123, coercer=str)
        assert (
            env.keys() == {'MYAPP_CONF'} if os_name in ('os2', 'nt') else {'myapp_conf'}
        )
        assert env['myapp_conf'].value == '123'
