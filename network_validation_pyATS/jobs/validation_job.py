import os

from pyats.easypy import run

TESTS_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "tests")
ORDER = ["connectivity", "interfaces", "ospf", "routing", "reachability"]


def main(runtime):
    selected = os.environ.get("VALIDATION_TESTS")
    names = [n.strip() for n in selected.split(",")] if selected else ORDER

    for name in names:
        if name not in ORDER:
            raise ValueError(f"Unknown test '{name}'. Choose from: {', '.join(ORDER)}")
        run(testscript=os.path.join(TESTS_DIR, f"test_{name}.py"), taskid=name)
