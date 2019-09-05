import configparser
import os.path

import uwsgi
from werkzeug.local import LocalProxy

_config = None
cfg = LocalProxy(lambda: _config)


class Configuration():
    def __init__(self, location=None, set=True):
        global _config
        if location:
            self.default_loc = location
        elif 'PY_CONFIG' in uwsgi.opt:
            self.default_loc = uwsgi.opt['PY_CONFIG'].decode()
        else:
            self.default_loc = './config.ini'

        self.sections = []
        self.load(self.default_loc)

        if set:
            _config = self

    def load(self, file):
        if os.path.isfile(file):
            config = configparser.ConfigParser()
            config.read(file)
            if config:
                self.config = config
                if config.sections():
                    self.section_list = config.sections()
                    return True
        else:
            raise EnvironmentError(f"File doesn't exist {file}")

        return False

    def unload(self):
        pass

    def read_section(self, section):
        if self.section_list:
            if section in self.section_list:
                return self.section_list[section]
        return False

    def get(self, section, key, default=None):
        if not self.section_list:
            raise EnvironmentError("Section List doesn't exist")
        if not section:
            raise ValueError("Section Not Given")
        if not key:
            raise ValueError("Key Not Given")

        if section in self.section_list:
            opts = self.config[section]
            if key in opts:
                # print("section {0}, key {1}, val {2}".format(section, key, opts[key]))
                return opts[key]
            elif default is not None:
                return default
            else:
                raise LookupError("Couldn't find key in section")
        else:
            if default is not None:
                return default
            raise LookupError("Section not found")

        raise NotImplementedError("Can't Happen")

    def set(self, key, val):
        raise NotImplementedError()

