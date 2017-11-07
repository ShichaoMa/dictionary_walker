# -*- coding:utf-8 -*-
import time
import os
import glob
import subprocess


def walk_child_dict_with_multi_process(path, process_count):
    site_name = os.path.basename(path)
    paths = glob.glob(os.path.join(path, "*"))
    runners = dict()
    while paths:
        path = paths.pop(-1)
        basename = os.path.basename(path)
        runners[path] = subprocess.Popen(
            "mkdir -p %s && cd %s && nohup python3 ../dict_walker.py %s %s > %s.log 2>&1 &"%(
            basename, basename, site_name, path, basename), shell=True)

        while len(runners) >= process_count:
            time.sleep(10)
            for path in list(runners.keys()):
                if not len([line for line in os.popen("ps -ef|grep %s"%path).readlines() if not line.count("grep %s"%path)]):
                    del runners[path]


if __name__ == "__main__":
    import sys
    walk_child_dict_with_multi_process(sys.argv[1], int(sys.argv[2]))