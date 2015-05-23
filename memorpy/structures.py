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

from ctypes import Structure, c_long, c_int, c_uint, c_char, c_void_p, c_ubyte, c_ushort, c_ulong, windll, POINTER, wintypes

BYTE = c_ubyte
WORD = c_ushort
DWORD = c_ulong

class MEMORY_BASIC_INFORMATION(Structure):
    _fields_ = [('BaseAddress', c_ulong),
     ('AllocationBase', c_ulong),
     ('AllocationProtect', c_ulong),
     ('RegionSize', c_ulong),
     ('State', c_ulong),
     ('Protect', c_ulong),
     ('Type', c_ulong)]


class SYSTEM_INFO(Structure):
    _fields_ = [('wProcessorArchitecture', WORD),
     ('wReserved', WORD),
     ('dwPageSize', DWORD),
     ('lpMinimumApplicationAddress', DWORD),
     ('lpMaximumApplicationAddress', DWORD),
     ('dwActiveProcessorMask', DWORD),
     ('dwNumberOfProcessors', DWORD),
     ('dwProcessorType', DWORD),
     ('dwAllocationGranularity', DWORD),
     ('wProcessorLevel', WORD),
     ('wProcessorRevision', WORD)]


class PROCESSENTRY32(Structure):
    _fields_ = [('dwSize', c_uint),
     ('cntUsage', c_uint),
     ('th32ProcessID', c_uint),
     ('th32DefaultHeapID', c_uint),
     ('th32ModuleID', c_uint),
     ('cntThreads', c_uint),
     ('th32ParentProcessID', c_uint),
     ('pcPriClassBase', c_long),
     ('dwFlags', c_uint),
     ('szExeFile', c_char * 260),
     ('th32MemoryBase', c_long),
     ('th32AccessKey', c_long)]


class MODULEENTRY32(Structure):
    _fields_ = [('dwSize', c_uint),
     ('th32ModuleID', c_uint),
     ('th32ProcessID', c_uint),
     ('GlblcntUsage', c_uint),
     ('ProccntUsage', c_uint),
     ('modBaseAddr', c_uint),
     ('modBaseSize', c_uint),
     ('hModule', c_uint),
     ('szModule', c_char * 256),
     ('szExePath', c_char * 260)]


class THREADENTRY32(Structure):
    _fields_ = [('dwSize', c_uint),
     ('cntUsage', c_uint),
     ('th32ThreadID', c_uint),
     ('th32OwnerProcessID', c_uint),
     ('tpBasePri', c_uint),
     ('tpDeltaPri', c_uint),
     ('dwFlags', c_uint)]


class TH32CS_CLASS(object):
    INHERIT = 2147483648L
    SNAPHEAPLIST = 1
    SNAPMODULE = 8
    SNAPMODULE32 = 16
    SNAPPROCESS = 2
    SNAPTHREAD = 4
    ALL = 2032639


Module32First = windll.kernel32.Module32First
Module32First.argtypes = [c_void_p, POINTER(MODULEENTRY32)]
Module32First.rettype = c_int
Module32Next = windll.kernel32.Module32Next
Module32Next.argtypes = [c_void_p, POINTER(MODULEENTRY32)]
Module32Next.rettype = c_int

Process32First = windll.kernel32.Process32First
Process32First.argtypes = [c_void_p, POINTER(PROCESSENTRY32)]
Process32First.rettype = c_int
Process32Next = windll.kernel32.Process32Next
Process32Next.argtypes = [c_void_p, POINTER(PROCESSENTRY32)]
Process32Next.rettype = c_int

CreateToolhelp32Snapshot = windll.kernel32.CreateToolhelp32Snapshot
CreateToolhelp32Snapshot.reltype = c_long
CreateToolhelp32Snapshot.argtypes = [c_int, c_int]

CloseHandle = windll.kernel32.CloseHandle
CloseHandle.argtypes = [c_void_p]
CloseHandle.rettype = c_int

OpenProcess = windll.kernel32.OpenProcess
OpenProcess.argtypes = [c_void_p, c_int, c_long]
OpenProcess.rettype = c_long
OpenProcessToken = windll.advapi32.OpenProcessToken
OpenProcessToken.argtypes = (wintypes.HANDLE, wintypes.DWORD, POINTER(wintypes.HANDLE))
OpenProcessToken.restype = wintypes.BOOL

PAGE_EXECUTE_READWRITE = 64
PAGE_EXECUTE_READ = 32
PAGE_READONLY = 2
PAGE_READWRITE = 4
PAGE_NOCACHE = 512
PAGE_WRITECOMBINE = 1024
PAGE_GUARD = 256

MEM_COMMIT = 4096
MEM_FREE = 65536
MEM_RESERVE = 8192

