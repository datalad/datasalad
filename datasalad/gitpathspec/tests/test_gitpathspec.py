import subprocess
import sys
from pathlib import Path

import pytest

from .. import (
    GitPathSpec,
    GitPathSpecs,
)
from ..pathspec import yield_subdir_match_remainder_pathspecs


def _list_files(path, pathspecs):
    return [
        i
        for i in subprocess.run(
            ['git', 'ls-files', '-z', '--other', '--', *pathspecs],  # noqa: S607
            capture_output=True,
            cwd=path,
            check=False,
        )
        .stdout.decode('utf-8')
        .split('\0')
        if i
    ]


@pytest.fixture(scope='function')  # noqa: PT003
def pathspec_match_testground(tmp_path_factory):
    """Create a Git repo with no commit and many untracked files

    In this playground, `git ls-files --other` can be used to testrun
    pathspecs.

    See the top item in `testcases` for a summary of the content
    """
    p = tmp_path_factory.mktemp('pathspec_match')
    probe = p / 'pr?be'
    # check for case insensitive file systems
    crippled_fs = Path(str(p).upper()).exists()
    try:
        probe.touch()
        probe.unlink()
    except OSError:
        crippled_fs = True

    subprocess.run(['git', 'init'], cwd=p, check=True)  # noqa: S607

    p_sub = p / 'sub'
    p_sub.mkdir()
    for d in (p, p_sub):
        p_a = d / 'aba'
        p_b = d / 'a?a'
        for sp in (p_a,) if crippled_fs else (p_a, p_b):
            sp.mkdir()
            for fname in ('a.txt', 'A.txt', 'a.JPG'):
                (sp / fname).touch()
    # add something that is unique to sub/
    (p_sub / 'b.dat').touch()

    aba_fordir_results = {
        None: {
            'match': [
                'aba/a.JPG',
                'aba/a.txt',
            ]
            if crippled_fs
            else ['aba/A.txt', 'aba/a.JPG', 'aba/a.txt'],
        },
        'aba': {
            'specs': [':'],
            'match': ['a.JPG', 'a.txt'] if crippled_fs else ['A.txt', 'a.JPG', 'a.txt'],
        },
    }

    testcases = [
        # valid
        {
            'ps': ':',
            'fordir': {
                None: {
                    'specs': [':'],
                    'match': [
                        'aba/a.JPG',
                        'aba/a.txt',
                        'sub/aba/a.JPG',
                        'sub/aba/a.txt',
                        'sub/b.dat',
                    ]
                    if crippled_fs
                    else [
                        'a?a/A.txt',
                        'a?a/a.JPG',
                        'a?a/a.txt',
                        'aba/A.txt',
                        'aba/a.JPG',
                        'aba/a.txt',
                        'sub/a?a/A.txt',
                        'sub/a?a/a.JPG',
                        'sub/a?a/a.txt',
                        'sub/aba/A.txt',
                        'sub/aba/a.JPG',
                        'sub/aba/a.txt',
                        'sub/b.dat',
                    ],
                },
                'sub': {
                    'specs': [':'],
                    'match': ['aba/a.JPG', 'aba/a.txt', 'b.dat']
                    if crippled_fs
                    else [
                        'a?a/A.txt',
                        'a?a/a.JPG',
                        'a?a/a.txt',
                        'aba/A.txt',
                        'aba/a.JPG',
                        'aba/a.txt',
                        'b.dat',
                    ],
                },
            },
        },
        {
            'ps': 'aba',
            'fordir': aba_fordir_results,
        },
        # same as above, but with a trailing slash
        {
            'ps': 'aba/',
            'fordir': aba_fordir_results,
        },
        # and one more of this kind, as a pointless literal
        {
            'ps': ':(literal)aba',
            'fordir': aba_fordir_results,
        },
        {
            'ps': ':(glob)aba/*.txt',
            'fordir': {
                None: {
                    'match': [
                        'aba/a.txt',
                    ]
                    if crippled_fs
                    else ['aba/A.txt', 'aba/a.txt']
                },
                'sub': {'specs': []},
            },
        },
        {
            'ps': ':/aba/*.txt',
            'norm': ':(top)aba/*.txt',
            'fordir': {
                None: {
                    'match': [
                        'aba/a.txt',
                    ]
                    if crippled_fs
                    else ['aba/A.txt', 'aba/a.txt']
                },
                # for a subdir a keeps matching the exact same items
                # not only be name, but by location
                'sub': {
                    'specs': [':(top)aba/*.txt'],
                    'match': ['../aba/a.txt']
                    if crippled_fs
                    else ['../aba/A.txt', '../aba/a.txt'],
                },
            },
        },
        {
            'ps': 'aba/*.txt',
            'fordir': {
                None: {
                    'match': ['aba/a.txt']
                    if crippled_fs
                    else ['aba/A.txt', 'aba/a.txt'],
                },
                # not applicable
                'sub': {'specs': []},
                # but this is
                'aba': {'specs': ['*.txt']},
            },
        },
        {
            'ps': 'sub/aba/*.txt',
            'fordir': {
                None: {
                    'match': ['sub/aba/a.txt']
                    if crippled_fs
                    else ['sub/aba/A.txt', 'sub/aba/a.txt']
                },
                'sub': {
                    'specs': ['aba/*.txt'],
                    'match': ['aba/a.txt']
                    if crippled_fs
                    else ['aba/A.txt', 'aba/a.txt'],
                },
            },
        },
        {
            'ps': '*.JPG',
            'fordir': {
                None: {
                    'match': ['aba/a.JPG', 'sub/aba/a.JPG']
                    if crippled_fs
                    else ['a?a/a.JPG', 'aba/a.JPG', 'sub/a?a/a.JPG', 'sub/aba/a.JPG']
                },
                # unchanged
                'sub': {'specs': ['*.JPG']},
            },
        },
        {
            'ps': '*ba*.JPG',
            'fordir': {
                None: {'match': ['aba/a.JPG', 'sub/aba/a.JPG']},
                'aba': {'specs': ['*ba*.JPG', '*.JPG'], 'match': ['a.JPG']},
            },
        },
        # invalid
        #
        # conceptual conflict and thereby unsupported by Git
        # makes sense and is easy to catch that
        {'ps': ':(glob,literal)broken', 'raises': ValueError},
    ]
    if not crippled_fs:
        testcases.extend(
            [
                # literal magic is only needed for non-crippled FS
                {
                    'ps': ':(literal)a?a/a.JPG',
                    'fordir': {
                        None: {
                            'match': ['a?a/a.JPG'],
                        },
                        'a?a': {
                            'specs': [':(literal)a.JPG'],
                            'match': ['a.JPG'],
                        },
                    },
                },
                {
                    'ps': ':(literal,icase)SuB/A?A/a.jpg',
                    'fordir': {
                        None: {'match': ['sub/a?a/a.JPG']},
                        'sub/a?a': {
                            'specs': [':(literal,icase)a.jpg'],
                            # given the spec transformation matches
                            # MIH would really expect to following,
                            # but it is not coming from Git :(
                            #'match': ['a.JPG'],
                            'match': [],
                        },
                    },
                },
                {
                    'ps': ':(icase)A?A/a.jpg',
                    'fordir': {
                        None: {'match': ['a?a/a.JPG', 'aba/a.JPG']},
                        'aba': {
                            'specs': [':(icase)a.jpg'],
                            'match': ['a.JPG'],
                        },
                    },
                },
                {
                    'ps': ':(literal,icase)A?A/a.jpg',
                    'fordir': {
                        None: {'match': ['a?a/a.JPG']},
                        'a?a': {
                            'specs': [':(literal,icase)a.jpg'],
                            'match': ['a.JPG'],
                        },
                        # the target subdir does not match the pathspec
                        'aba': {'specs': set()},
                    },
                },
            ]
        )

    return p, testcases


def test_pathspecs(pathspec_match_testground):
    tg, testcases = pathspec_match_testground

    for testcase in testcases:
        if testcase.get('raises'):
            # test case states how `GitPathSpec` will blow up
            # on this case. Verify and skip any further testing
            # on this case
            with pytest.raises(testcase['raises']):
                GitPathSpec.from_pathspec_str(testcase['ps'])
            continue
        # create the instance
        ps = GitPathSpec.from_pathspec_str(testcase['ps'])
        # if no deviating normalized representation is given
        # it must match the original one
        assert str(ps) == testcase.get('norm', testcase['ps'])
        # test translations onto subdirs now
        # `None` is a special subdir that means "self", i.e.
        # not translation other than normalization, we can use it
        # to test matching behavior of the full pathspec
        for subdir, target in testcase.get('fordir', {}).items():
            # translate -- a single input pathspec can turn into
            # multiple translated ones. This is due to
            subdir_specs = [str(s) for s in ps.for_subdir(subdir)]
            if 'specs' in target:
                assert set(subdir_specs) == set(
                    target['specs']
                ), f'Mismatch for {testcase["ps"]!r} -> subdir {subdir!r} {target}'
            if subdir and not target.get('specs') and 'match' in target:
                msg = (
                    'invalid test specification: no subdir specs expected, '
                    f'but match declared: {testcase!r}'
                )
                raise ValueError(msg)
            if subdir_specs and 'match' in target:
                tg_subdir = tg / subdir if subdir else tg
                assert _list_files(tg_subdir, subdir_specs) == target['match']


def test_yield_subdir_match_remainder_pathspecs():
    testcases = [
        # FORMAT: target path, pathspec, subdir pathspecs
        ('abc', ':', [':']),
        # top-magic is returned as-is
        ('murks', ':(top)crazy*^#', [':(top)crazy*^#']),
        # no match
        ('abc', 'not', []),
        ('abc', 'ABC', [':'] if sys.platform.startswith('win') else []),
        # direct hits, resolve to "no pathspecs"
        ('abc', 'a?c', [':']),
        ('abc', 'abc', [':']),
        ('abc', 'abc/', [':']),
        # icase-magic
        ('abc', ':(icase)ABC', [':']),
        ('ABC', ':(icase)abc', [':']),
        # some fairly common fnmatch-style pathspec
        ('abc', 'abc/*.jpg', ['*.jpg']),
        ('abc', '*.jpg', ['*.jpg']),
        ('abc', '*/*.jpg', ['*/*.jpg', '*.jpg']),
        ('abc', '*/*.jpg', ['*/*.jpg', '*.jpg']),
        ('abc', '*bc*.jpg', ['*bc*.jpg', '*.jpg']),
        # adding an glob-unrelated magic does not impact the result
        ('abc', ':(exclude)*/*.jpg', [':(exclude)*/*.jpg', ':(exclude)*.jpg']),
        (
            'abc',
            ':(attr:export-subst)*/*.jpg',
            [':(attr:export-subst)*/*.jpg', ':(attr:export-subst)*.jpg'],
        ),
        (
            'abc',
            ':(icase,exclude)*/*.jpg',
            [':(icase,exclude)*/*.jpg', ':(icase,exclude)*.jpg'],
        ),
        # glob-magic
        ('abc', ':(glob)*bc*.jpg', []),
        ('abc', ':(glob)*bc**.jpg', [':(glob)**.jpg']),
        # 2nd-level subdir
        ('abc/123', 'some.jpg', []),
        ('abc/123', '*.jpg', ['*.jpg']),
        ('abc/123', 'abc/*', [':']),
        ('abc/123', 'abc', [':']),
        ('abc/123', ':(glob)abc', [':']),
        ('abc/123', '*123', ['*123', ':']),
        ('abc/123', '*/123', ['*/123', ':']),
        ('abc/123', ':(glob)*/123', [':']),
        # literal-magic
        ('abc', ':(literal)a?c', []),
        ('a?c', ':(literal)a?c', [':']),
        ('a?c', ':(literal)a?c/*?ab*', [':(literal)*?ab*']),
        ('a?c/123', ':(literal)a?c', [':']),
        # more complex cases
        ('abc/123/ABC', 'a*/1?3/*.jpg', ['*/1?3/*.jpg', '*.jpg', '1?3/*.jpg']),
        # exclude-magic
        ('abc', ':(exclude)abc', [':']),
        ('abc/123', ':(exclude)abc', [':']),
        ('a?c', ':(exclude,literal)a?c', [':']),
        # stuff that was problematic at some point
        # initial, non-wildcard part already points inside the
        # target directory
        ('sub', 'sub/aba/*.txt', ['aba/*.txt']),
        # no directory-greedy wildcard whatsoever
        ('abc', ':(icase)A?C/a.jpg', [':(icase)a.jpg']),
        # no directory-greedy wildcard in later chunk
        ('nope/abc', 'no*/a?c/a.jpg', ['*/a?c/a.jpg', 'a.jpg']),
    ]
    for ts in testcases:
        # always test against the given subdir, and also against the subdir
        # given with a trailing slash
        for target_path in (ts[0], f'{ts[0]}/'):
            tsps = GitPathSpec.from_pathspec_str(ts[1])
            remainders = list(
                yield_subdir_match_remainder_pathspecs(
                    target_path,
                    tsps,
                )
            )
            assert [str(ps) for ps in remainders] == ts[2], f'Mismatch for {ts}'
            # arglist processing of the GitPathSpecs container comes to the
            # same result
            if remainders:
                assert GitPathSpecs(remainders).arglist() == ts[2]
            # now we produce the same result with the GitPathSpecs handler
            try:
                assert GitPathSpecs([ts[1]]).for_subdir(target_path).arglist() == [
                    str(ps) for ps in remainders
                ]
            except ValueError:
                # translation must raise when there would not be a remainder
                assert not remainders
            # if we are supposed to get any remainder out, the test for a
            # subdir match also gives an analog result
            if ts[2]:
                assert GitPathSpecs([tsps]).any_match_subdir(target_path)
            else:
                assert not GitPathSpecs([tsps]).any_match_subdir(target_path)


def test_GitPathSpecs():
    spec_input = ['mike/*', '*.jpg']
    ps = GitPathSpecs(spec_input)
    # we can create a GitPathSpecs object from another
    assert GitPathSpecs(ps).arglist() == ps.arglist()

    # going over the properties
    assert repr(ps) == "GitPathSpecs(['mike/*', '*.jpg'])"
    assert len(ps) == len(spec_input)

    # we can have "no pathspecs". `None` and a single ':' are equivalent
    # ways to communicate this
    for ps in (None, ':'):
        nops = GitPathSpecs(ps)
        assert GitPathSpecs(ps).for_subdir('doesntmatter') == nops
        assert GitPathSpecs(ps).any_match_subdir('doesntmatter') is True

    # how about the semantic distinction between None and []?
    # [] is not valid
    with pytest.raises(ValueError, match='did not contain any pathspecs'):
        GitPathSpecs([])
