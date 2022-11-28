from invoke import task


@task
def lint(c):
    c.run("flake8 src/file_transfer tests")
    c.run("black src/file_transfer tests --check")


@task
def test(c):
    c.run(
        "pytest --cov=file_transfer  --cov=tests --cov-report=xml --cov-report=html tests"
    )
