import os

import pytest

from synthtool import transforms


@pytest.fixture()
def expand_path_fixtures(tmpdir):
    files = [
        'a.txt',
        'b.py',
        'c.md',
        'dira/e.txt',
        'dira/f.py',
        'dirb/suba/g.py'
    ]

    for file in files:
        path = tmpdir.join(file)
        path.write_text('content', encoding='utf-8', ensure=True)

    cwd = os.getcwd()
    os.chdir(str(tmpdir))
    yield tmpdir
    os.chdir(cwd)


@pytest.mark.parametrize(['input', 'expected'], [
    ('a.txt', ['a.txt']),
    ('*', [
        'a.txt',
        'b.py',
        'c.md',
        'dira',
        'dirb']),
    ('*.py', [
        'b.py']),
    ('**/*.py', [
        'b.py',
        'dira/f.py',
        'dirb/suba/g.py']),
    ('**/*', [
        'a.txt',
        'b.py',
        'c.md',
        'dira',
        'dira/e.txt',
        'dira/f.py',
        'dirb',
        'dirb/suba',
        'dirb/suba/g.py']),
])
def test__expand_paths(expand_path_fixtures, input, expected):
    paths = sorted([str(x) for x in transforms._expand_paths(input)])
    assert paths == expected


@pytest.mark.parametrize(['input', 'expected'], [
    ('e.txt', ['dira/e.txt']),
    ('*', ['dira/e.txt', 'dira/f.py']),
])
def test__expand_paths_with_root(expand_path_fixtures, input, expected):
    paths = sorted([
        str(x) for x in transforms._expand_paths(input, root='dira')])
    assert paths == expected


def test__filter_files(expand_path_fixtures):
    files = sorted([
        str(x) for x in
        transforms._filter_files(transforms._expand_paths('**/*'))])

    assert files == [
        'a.txt',
        'b.py',
        'c.md',
        'dira/e.txt',
        'dira/f.py',
        'dirb/suba/g.py'
    ]
