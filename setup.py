#!/usr/bin/env python

import os

THIS_DIR = os.path.dirname(os.path.realpath(__file__))
BIN_DIR = os.path.expanduser("~/bin")

def symlink_to_bin():
    ln_src = os.path.join(THIS_DIR, "webnull.py")
    ln_dest = os.path.join(BIN_DIR, "webnull")
    if os.path.isfile(ln_dest):
        os.remove(ln_dest)
    os.symlink(ln_src, ln_dest)

if __name__ == "__main__":
    symlink_to_bin()
