from __future__ import annotations

import sys

import pytest

from ..exception import CommandError


def test_CommandError_minial():
    with pytest.raises(TypeError):
        # we need a command
        CommandError()


def test_CommandError_str_repr() -> None:
    unicode_out = 'ΔЙקم๗あösdohabcdefdf0j23d2däüß§!אؠॵΔЙקم๗あöäüß§!אؠॵℱ⏰︻𐂃𐃍'
    cp1252_out = b'\xe4\xd6\xc4\xdf\xa7'
    testcases = [
        (
            CommandError('mycmd'),
            "Command 'mycmd' errored with unknown exit status",
            "CommandError('mycmd')",
        ),
        (
            CommandError(['mycmd', 'arg0']),
            "Command ['mycmd', 'arg0'] errored with unknown exit status",
            "CommandError(['mycmd', 'arg0'])",
        ),
        (
            CommandError(
                cmd='<cmd>',
                msg='<msg>',
                returncode=1,
                stdout='<stdout>',
                stderr='<stderr>',
                cwd='<cwd>',
            ),
            "Command '<cmd>' returned non-zero exit status 1 at CWD <cwd> [<msg>] [stderr: <stderr>]",
            "CommandError('<cmd>', msg='<msg>', returncode=1, stdout='<stdout>', "
            "stderr='<stderr>', cwd='<cwd>')",
        ),
        (
            CommandError('mycmd', stdout=unicode_out),
            "Command 'mycmd' errored with unknown exit status",
            f"CommandError('mycmd', stdout='{unicode_out[:20]}<... +14 chars>{unicode_out[-20:]}')",
        ),
        (
            CommandError('mycmd', stdout=cp1252_out),
            "Command 'mycmd' errored with unknown exit status",
            "CommandError('mycmd', stdout=b'<5 bytes>')",
        ),
        (
            CommandError('mycmd', returncode=6),
            "Command 'mycmd' returned non-zero exit status 6",
            "CommandError('mycmd', returncode=6)",
        ),
        (
            CommandError('mycmd', returncode=-234),
            "Command 'mycmd' died with unknown signal 234",
            "CommandError('mycmd', returncode=-234)",
        ),
        (
            CommandError('mycmd', stderr=unicode_out),
            f"Command 'mycmd' errored with unknown exit status [stderr: {unicode_out}]",
            f"CommandError('mycmd', stderr='{unicode_out[:20]}<... +14 chars>{unicode_out[-20:]}')",
        ),
    ]
    if not sys.platform.startswith('win'):
        testcases.extend(
            (
                # decode signal name, like `subprocess.CalledProcessError` does
                (
                    CommandError('mycmd', returncode=-6),
                    "Command 'mycmd' died with SIGABRT",
                    "CommandError('mycmd', returncode=-6)",
                ),
                # this is done on non-windows, because it uses a CP1252
                # encoded string to provoke a decoding error
                (
                    CommandError('mycmd', stderr=cp1252_out),
                    "Command 'mycmd' errored with unknown exit status "
                    '[stderr: <undecodable 5 bytes>]',
                    "CommandError('mycmd', stderr=b'<5 bytes>')",
                ),
            )
        )
    for ce, _str, _repr in testcases:
        assert str(ce) == _str
        assert repr(ce) == _repr


def check_reraise_CommandError_with_msg():
    try:
        # some call raises an original exception
        raise CommandError('mycmd')  # noqa: TRY301, EM101
    except CommandError as e:
        # a wrapping try/except can be used to add context info
        # or a hint on a probably cause to the exception
        e.msg = 'context info or hint'
        raise


def test_CommandError_context_msg():
    with pytest.raises(CommandError) as cmderr:
        check_reraise_CommandError_with_msg()
    assert cmderr.value.cmd == 'mycmd'
    assert cmderr.value.msg == 'context info or hint'
    assert (
        str(cmderr.value) == "Command 'mycmd' errored with unknown exit status "
        '[context info or hint]'
    )
