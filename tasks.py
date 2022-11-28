from invoke import task


@task
def lint(c):
    c.run("flake8 src/redis_file_transfer tests")
    c.run("black src/redis_file_transfer tests --check")


@task
def test(c):
    c.run(
        "pytest --cov=redis_file_transfer  --cov=tests --cov-report=xml --cov-report=html tests"
    )
