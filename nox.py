import nox


@nox.session
def test(session):
    session.interpreter = 'python3.6'
    session.install('pytest', 'flit')
    session.run('flit', 'install')
    session.run('pytest', 'tests', *session.posargs)


@nox.session
def lint(session):
    session.interpreter = 'python3.6'
    session.install('flit', 'mypy', 'flake8')
    session.run('flit', 'install')
    session.run('flake8', 'synthtool', 'synthtool_gcp', 'tests')
    session.run('mypy', '--ignore-missing-imports', 'synthtool')
