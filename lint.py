"""This file run linters for the project."""
import subprocess

subprocess.run(("flake8", "--exclude", "spezspellz/migrations,__init__.py",
                "--max-line-length", "100", "spezspellz"),
               check=False)
subprocess.run(("mypy", "spezspellz"), check=False)
subprocess.run(("ruff", "check", "spezspellz"), check=False)
