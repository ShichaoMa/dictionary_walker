# -*- coding:utf-8 -*-
import time
import os
import glob
import subprocess


def walker_child_dict_with_multi_process(path, process_count):
    paths = glob.glob(os.path.join(path, "*"))
    runners = dict()
    while paths:
        path = paths.pop(-1)
        basename = os.path.basename(path)
        runners[path] = subprocess.Popen(
            "mkdir -p %s && cd %s && nohup python3 ../dict_walker.py amazon %s > %s.log 2>&1 &"%(
            basename, basename, path, basename), shell=True)

        while len(runners) >= process_count:
            time.sleep(10)
            for path in list(runners.keys()):
                if len(os.popen("ps -ef|grep %s"%path).readlines()) <= 2:
                    del runners[path]


if __name__ == "__main__":
    import sys
    walker_child_dict_with_multi_process(sys.argv[1], int(sys.argv[2]))