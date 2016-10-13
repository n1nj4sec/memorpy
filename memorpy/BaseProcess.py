#!/usr/bin/env python
# -*- coding: UTF8 -*-

""" Base class for process not linked to any platform """

class ProcessException(Exception):
    pass

class BaseProcess(object):

    def __init__(self, *args, **kwargs):
        """ Create and Open a process object from its pid or from its name """
        self.h_process = None
        self.pid = None
        self.isProcessOpen = False
        self.buffer = None
        self.bufferlen = 0

    def __del__(self):
        self.close()

    def close(self):
        pass
    def iter_region(self, *args, **kwargs):
        raise NotImplementedError
    def write_bytes(self, address, data):
        raise NotImplementedError

    def read_bytes(self, address, bytes = 4):
        raise NotImplementedError

    def read(self, address, type = 'uint', maxlen = 50, errors='raise'):
        if type == 's' or type == 'string':
            s = self.read_bytes(int(address), bytes=maxlen)
            news = ''
            for c in s:
                if c == '\x00':
                    return news
                news += c
            if errors=='ignore':
                return news
            raise ProcessException('string > maxlen')
        else:
            if type == 'bytes' or type == 'b':
                return self.read_bytes(int(address), bytes=maxlen)
            s, l = utils.type_unpack(type)
            return struct.unpack(s, self.read_bytes(int(address), bytes=l))[0]

    def write(self, address, data, type = 'uint'):
        if type != 'bytes':
            s, l = utils.type_unpack(type)
            return self.write_bytes(int(address), struct.pack(s, data))
        else:
            return self.write_bytes(int(address), data)
   

