from __future__ import annotations

import pytest

from ..exception import CommandError


def test_CommandError_minial():
    with pytest.raises(TypeError):
        # we need a command
        CommandError()


def test_CommandError_str_repr() -> None:
    unicode_out = "ΔЙקم๗あösdohabcdefdf0j23d2däüß§!אؠॵΔЙקم๗あöäüß§!אؠॵℱ⏰︻𐂃𐃍"
    cp1252_out = b'\xe4\xd6\xc4\xdf\xa7'
    testcases = [
        (CommandError('mycmd'),
         "CommandError: 'mycmd'",
         "CommandError('mycmd')"),
        (CommandError(['mycmd', 'arg0']),
         "CommandError: ['mycmd', 'arg0']",
         "CommandError(['mycmd', 'arg0'])"),
        (CommandError(cmd="<cmd>", msg="<msg>", returncode=1,
                      stdout="<stdout>", stderr="<stderr>", cwd="<cwd>"),
         "CommandError: '<cmd>' failed with exitcode 1 at CWD <cwd> [<msg>]",
         "CommandError('<cmd>', msg='<msg>', returncode=1, stdout='<stdout>', "
         "stderr='<stderr>', cwd='<cwd>')"),
        (CommandError('mycmd', stdout=unicode_out),
         "CommandError: 'mycmd'",
         f"CommandError('mycmd', stdout='{unicode_out[:20]}<... +14 chars>{unicode_out[-20:]}')"),
        (CommandError('mycmd', stdout=cp1252_out),
         "CommandError: 'mycmd'",
         "CommandError('mycmd', stdout=b'<5 bytes>')"),
        (CommandError('mycmd', stderr=cp1252_out),
         "CommandError: 'mycmd'",
         "CommandError('mycmd', stderr=b'<5 bytes>')"),
    ]
    for ce, _str, _repr in testcases:
        assert ce.to_str() == str(ce) == _str
        assert repr(ce) == _repr
