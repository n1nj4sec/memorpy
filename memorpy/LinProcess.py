# Author: Nicolas VERDIER
# This file is part of memorpy.
#
# memorpy is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# memorpy is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with memorpy.  If not, see <http://www.gnu.org/licenses/>.

import copy
import struct
import utils
import platform
import ctypes, re, sys
import os
from BaseProcess import BaseProcess, ProcessException

c_ptrace = ctypes.CDLL("libc.so.6").ptrace
c_pid_t = ctypes.c_int32 # This assumes pid_t is int32_t
c_ptrace.argtypes = [ctypes.c_int, c_pid_t, ctypes.c_void_p, ctypes.c_void_p]

class LinProcess(BaseProcess):
    def __init__(self, pid=None, name=None, debug=True, ptrace=None):
        """ Create and Open a process object from its pid or from its name """
        super(LinProcess, self).__init__()
        self.mem_file=None
        self.ptrace_started=False
        if pid is not None:
            self.pid=pid
        elif name is not None:
            self.pid=LinProcess.pid_from_name(name)
        else:
            raise ValueError("You need to instanciate process with at least a name or a pid")
        if ptrace is None:
            if os.getuid()==0:
                ptrace=False # no need to ptrace the process when root
            else:
                ptrace=True
        self._open(ptrace)

    def close(self):
        if self.ptrace_started:
            self.ptrace_detach()

    def _open(self, ptrace):
        if ptrace:
            self.ptrace_attach()

    @staticmethod
    def pid_from_name(name):
        #quick and dirty, works with all linux not depending on ps output
        for pid in os.listdir("/proc"):
            try:
                int(pid)
            except:
                continue
            pname=""
            with open("/proc/%s/cmdline"%pid,'r') as f:
                pname=f.read()
            if name in pname:
                return int(pid)
        raise ProcessException("No process with such name: %s"%name)

    ## Partial interface to ptrace(2), only for PTRACE_ATTACH and PTRACE_DETACH.
    def _ptrace(self, attach):
        op = ctypes.c_int(16 if attach else 17) #PTRACE_ATTACH or PTRACE_DETACH
        c_pid = c_pid_t(self.pid)
        null = ctypes.c_void_p()
        err = c_ptrace(op, c_pid, null, null)
        if err != 0:
            raise OSError("%s : Error using ptrace"%err)
        self.ptrace_started=True

    def iter_region(self, start_offset=None, end_offset=None, protec=None):
        with open("/proc/" + str(self.pid) + "/maps", 'r') as maps_file:
            for line in maps_file:
                m = re.match(r'([0-9A-Fa-f]+)-([0-9A-Fa-f]+) ([-rwpsx]+)', line)
                start, end, region_protec = int(m.group(1), 16), int(m.group(2), 16), m.group(3)
                if start_offset is not None:
                    if start < start_offset:
                        continue
                if end_offset is not None:
                    if start > end_offset:
                        continue
                chunk=end-start
                if 'r' in region_protec: # TODO: handle protec parameter
                    yield start, chunk
        
    def ptrace_attach(self):
        return self._ptrace(True)

    def ptrace_detach(self):
        return self._ptrace(False)

    def write_bytes(self, address, data):
        raise NotImplementedError

    def read_bytes(self, address, bytes = 4):
        data=b''
        with open("/proc/" + str(self.pid) + "/mem", 'r', 0) as mem_file:
            mem_file.seek(address)
            data=mem_file.read(bytes)
        return data


