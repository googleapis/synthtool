from pathlib import Path


from synthtool.sources import templates


FIXTURES = Path(__file__).parent / 'fixtures'


def test_render():
    t = templates.Templates(FIXTURES)
    result = t.render('example.j2', name='world')

    assert result.name == 'example.j2'
    assert result.read_text() == 'Hello, world!'
