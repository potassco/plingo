import sys
from clingo.application import clingo_main

from .plingo_app import PlingoApp


def main():
    sys.exit(int(clingo_main(PlingoApp(), sys.argv[1:])))
