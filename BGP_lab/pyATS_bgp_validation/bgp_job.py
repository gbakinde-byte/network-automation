import os

from pyats.easypy import run


def main(runtime):
    run(testscript=os.path.join(os.path.dirname(__file__), "test_bgp.py"), runtime=runtime)
