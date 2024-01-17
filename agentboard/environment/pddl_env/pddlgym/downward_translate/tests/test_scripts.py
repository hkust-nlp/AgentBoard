import os.path
import subprocess
import sys

DIR = os.path.dirname(os.path.abspath(__file__))
TRANSLATE_DIR = os.path.dirname(DIR)
REPO = os.path.abspath(os.path.join(DIR, "..", "..", ".."))
BENCHMARKS = os.path.join(REPO, "misc", "tests", "benchmarks")
DOMAIN = os.path.join(BENCHMARKS, "gripper", "domain.pddl")
PROBLEM = os.path.join(BENCHMARKS, "gripper", "prob01.pddl")
SCRIPTS = [
    "build_model.py",
    "graph.py",
    "instantiate.py",
    "invariant_finder.py",
    "normalize.py",
    "pddl_to_prolog.py",
    "translate.py",
]

def test_scripts():
    for script in SCRIPTS:
        script = os.path.join(TRANSLATE_DIR, script)
        folder, filename = os.path.split(script)
        assert subprocess.check_call([sys.executable, filename, DOMAIN, PROBLEM], cwd=folder) == 0
