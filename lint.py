"""This file run linters for the project."""
import subprocess


class Linter:
    linters: list[tuple[str]]

    def __init__(self, **kwargs):
        self.linters = [cmds for cmds in kwargs.values()]

    def run(self):
        err = False
        for cmds in self.linters:
            try:
                subprocess.run(cmds, check=True)
            except subprocess.CalledProcessError:
                err = True
        if err:
            exit(1)


linter = Linter(flake8=("flake8", "--exclude",
                        "spezspellz/migrations,__init__.py",
                        "--max-line-length", "256", "spezspellz"),
                mypy=("mypy", "spezspellz"),
                ruff=(("ruff", "check", "spezspellz")))
linter.run()
