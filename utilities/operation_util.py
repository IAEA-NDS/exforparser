import os
import shutil
import time
import json
import sys

sys.path.append("../")
from config import OUT_PATH, EXFOR_MASTER_REPO_PATH


def del_outputs(name):

    path = os.path.join(OUT_PATH, name)

    if os.path.exists(path):
        shutil.rmtree(path)

    os.mkdir(path)


def rescue(processed):
    lines = []
    if os.path.exists("processed.dat"):
        with open("processed.dat") as f:
            lines = f.readlines()
        if processed in "".join(lines):
            return True

        else:
            with open(r"processed_id.dat", "a") as fp:
                fp.write(processed + "\n")
            return False

    else:
        with open(r"processed_id.dat", "a") as fp:
            fp.write(processed + "\n")
            return False


def process_time(func):
    """
    for debugging purpose, delete @decorator
    """

    def inner(*args):
        start_time = time.time()
        func(*args)
        print(str(func), "--- %s seconds ---" % (time.time() - start_time))

    return inner


def print_time(start_time=None):
    if start_time:
        str = "--- %s seconds ---" % (time.time() - start_time)
        return str

    else:
        return time.time()


def get_entry_update_date():
    d = {}
    file = os.path.join(EXFOR_MASTER_REPO_PATH, "entry_updatedate.dat")
    with open(file) as f:
        for line in f:
            x = line.split(" ")
            d.update({x[0]: {"last_update": x[1], "revisions": x[2].strip()}})
    return d


# get_entry_update_date()
