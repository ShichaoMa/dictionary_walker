# -*- coding:utf-8 -*-
import os
import glob
import traceback
import requests

from functools import partial


class DicWalk(object):
    """
    一个可以遍历目录的程序，适合遍历超多的文件。可断点续遍。
    """

    def __init__(self, callback, dictionary):
        self.callback = callback
        self.config = "config"
        self.errors = "error"
        self.dictionary = dictionary

    def start(self):
        if os.path.exists(self.config):
            config = open(self.config, "r+")
        else:
            config = open(self.config, "w+")
            config.write("%s\n"%self.dictionary.rstrip("/"))
        errors = open(self.errors, "a")
        config.seek(0)
        path_nodes = [i.strip() for i in config.readlines() if i.strip()]
        path = path_nodes.pop(0)
        for filename in self.walk(path, config, path_nodes):
            if not self.callback(filename, self.dictionary):
                errors.write(filename + "\n")
                errors.flush()
        config.close()
        errors.close()

    def walk(self, path, start_config, path_nodes=None):
        """
        用来保存遍历的地址，同时也可以找到中断的遍历地址并继续遍历
        :param path:
        :param start_config:
        :param path_nodes:
        :return:
        """
        rebuild, find, path_node = True, True, None
        if path_nodes:
            path_node = path_nodes.pop(0)
            find = False
            cursor = len(path) + 1
        else:
            rebuild = False
            cursor = start_config.tell()

        for filename in glob.glob(os.path.join(path, "*")):
            if rebuild and (os.path.basename(filename) != path_node and not find):
                continue
            find = True
            if not path_nodes:
                last_cursor = start_config.tell()
                start_config.seek(cursor)
                start_config.write(" "*(last_cursor-cursor))
                start_config.flush()
                start_config.seek(cursor)
            if os.path.isdir(filename):
                path = filename
                if not path_nodes:
                    start_config.write(os.path.basename(filename) + "\n")
                    start_config.flush()
                yield from self.walk(path, start_config, path_nodes)
            else:
                if self.match(filename):
                    yield filename

    @staticmethod
    def match(filename):
        """
        如果找到的文件是你所需要的，返回True
        :param filename:
        :return:
        """
        return filename.endswith("jpg") and not filename.count("_")


def send(filename, dictionary, site=None, session=None):
    """
    callback函数,可根据自己需求实现，若返回False，则在error文件中会记录该文件名。
    :param filename:
    :param dictionary:
    :param session:
    :return:
    """
    site = site or filename.replace("%s/"%dictionary.rstrip("/"), "").split("/")[0]
    try:
        url = "http://192.168.200.79:8888/%s/" % site
        resp = session.post(url,
                            files={"file": (os.path.basename(filename), open(filename, "rb"))}, timeout=10)
        if resp.status_code < 300:
            print(filename)
            return True
        else:
            print(resp.text)
            return False
    except Exception:
        traceback.print_exc()
        return False


if __name__ == "__main__":
    import sys
    DicWalk(partial(send, site=sys.argv[1], session=requests.Session()), sys.argv[2]).start()
