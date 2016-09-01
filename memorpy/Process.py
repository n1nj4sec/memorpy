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

from ctypes import pointer, sizeof, windll, create_string_buffer, c_ulong, byref, GetLastError, c_bool, WinError
from structures import *
import copy
import struct
import utils
import win32security
import win32api
import platform

class ProcessException(Exception):
    pass

IsWow64Process=None
if hasattr(windll.kernel32,'IsWow64Process'):
    IsWow64Process=windll.kernel32.IsWow64Process
    IsWow64Process.restype = c_bool
    IsWow64Process.argtypes = [c_void_p, POINTER(c_bool)]

class Process(object):

    def __init__(self):
        self.h_process = None
        self.pid = None
        self.isProcessOpen = False
        self.process32 = None
        self.buffer = None
        self.bufferlen = 0

    def __del__(self):
        self.close()

    def is_64bit(self):
        if not "64" in platform.machine():
            return False
        iswow64 = c_bool(False)
        if IsWow64Process is None:
            return False
        if not IsWow64Process(self.h_process, byref(iswow64)):
            raise WinError()
        return not iswow64.value

    def list(self):
        """
        return a list of <PROCESSENTRY32>
        """
        processes = []
        hProcessSnap = CreateToolhelp32Snapshot(TH32CS_CLASS.SNAPPROCESS, 0)
        pe32 = PROCESSENTRY32()
        pe32.dwSize = sizeof(PROCESSENTRY32)
        ret = Process32First(hProcessSnap, pointer(pe32))
        while ret:
            ret = Process32Next(hProcessSnap, pointer(pe32))
            if pe32.dwFlags == 0:
                processes.append(copy.copy(pe32))
            else:
                break

        CloseHandle(hProcessSnap)
        return processes

    def name_from_process(self, dwProcessId):
        process_list = self.list()
        for process in process_list:
            if process.th32ProcessID == dwProcessId:
                return process.szExeFile[:-4]

        return False

    def process32_from_id(self, dwProcessId):
        process_list = self.list()
        for process in process_list:
            if process.th32ProcessID == dwProcessId:
                return process

    def process_from_name(self, processName):
        processes = []
        for process in self.list():
            if processName == process.szExeFile[:-4]:
                processes.append(process)

        if len(processes) > 0:
            return processes

    def open(self, dwProcessId):
        self.h_process = OpenProcess(2035711, 0, dwProcessId)
        if self.h_process is not None:
            self.isProcessOpen = True
            self.process32 = self.process32_from_id(dwProcessId)
            return True
        return False

    def close(self):
        if self.h_process is not None:
            ret = CloseHandle(self.h_process) == 1
            if ret:
                self.h_process = None
                self.pid = None
                self.isProcessOpen = False
                self.process32 = None
            return ret
        return False

    def open_debug_from_name(self, processName):
        dwProcessId = self.process_from_name(processName)
        if not dwProcessId:
            raise ProcessException("can't get pid from name %s" % processName)
        self.open_debug(dwProcessId[0].th32ProcessID)

    def open_debug(self, dwProcessId):
        process = OpenProcess(262144, 0, dwProcessId)
        #info = win32security.GetSecurityInfo(windll.kernel32.GetCurrentProcess(), 6, 0)
        info = win32security.GetSecurityInfo(win32api.GetCurrentProcess(), 6, 0)
        win32security.SetSecurityInfo(process, 6, win32security.DACL_SECURITY_INFORMATION | win32security.UNPROTECTED_DACL_SECURITY_INFORMATION, None, None, info.GetSecurityDescriptorDacl(), info.GetSecurityDescriptorGroup())
        CloseHandle(process)
        self.h_process = OpenProcess(2035711, 0, dwProcessId)
        if self.h_process:
            self.isProcessOpen = True
            self.process32 = self.process32_from_id(dwProcessId)
            return True
        return False

    def GetSystemInfo(self):
        si = SYSTEM_INFO()
        windll.kernel32.GetSystemInfo(byref(si))
        return si

    def GetNativeSystemInfo(self):
        si = SYSTEM_INFO()
        windll.kernel32.GetNativeSystemInfo(byref(si))
        return si

    def VirtualQueryEx(self, lpAddress):
        mbi = MEMORY_BASIC_INFORMATION()
        if not VirtualQueryEx(self.h_process, lpAddress, byref(mbi), sizeof(mbi)):
            raise ProcessException('Error VirtualQueryEx: 0x%08X' % lpAddress)
        return mbi

    def VirtualQueryEx64(self, lpAddress):
        mbi = MEMORY_BASIC_INFORMATION64()
        if not VirtualQueryEx64(self.h_process, lpAddress, byref(mbi), sizeof(mbi)):
            raise ProcessException('Error VirtualQueryEx: 0x%08X' % lpAddress)
        return mbi

    def VirtualProtectEx(self, base_address, size, protection):
        old_protect = c_ulong(0)
        if not windll.kernel32.VirtualProtectEx(self.h_process, base_address, size, protection, byref(old_protect)):
            raise ProcessException('Error: VirtualProtectEx(%08X, %d, %08X)' % (base_address, size, protection))
        return old_protect.value

    def write_bytes(self, address, data):
        address = int(address)
        if not self.isProcessOpen:
            raise ProcessException("Can't write_bytes(%s, %s), process %s is not open" % (address, data, self.pid))
        buffer = create_string_buffer(data)
        sizeWriten = c_ulong(0)
        bufferSize = sizeof(buffer) - 1
        _address = address
        _length = bufferSize + 1
        try:
            old_protect = self.VirtualProtectEx(_address, _length, PAGE_EXECUTE_READWRITE)
        except:
            pass

        res = windll.kernel32.WriteProcessMemory(self.h_process, address, buffer, bufferSize, byref(sizeWriten))
        try:
            self.VirtualProtectEx(_address, _length, old_protect)
        except:
            pass

        return res

    def read_bytes(self, address, bytes = 4, use_NtWow64ReadVirtualMemory64=False):
        #print "reading %s bytes from addr %s"%(bytes, address)
        if use_NtWow64ReadVirtualMemory64:
            if NtWow64ReadVirtualMemory64 is None:
                raise WindowsError("NtWow64ReadVirtualMemory64 is not available from a 64bit process")
            RpM=NtWow64ReadVirtualMemory64
        else:
            RpM=ReadProcessMemory

        address = int(address)
        if not self.isProcessOpen:
            raise ProcessException("Can't read_bytes(%s, bytes=%s), process %s is not open" % (address, bytes, self.pid))
        #print "creating buf: %s"%bytes
        buffer = create_string_buffer(bytes)
        bytesread = c_size_t(0)
        data = ''
        length = bytes
        _address = address
        _length = length
        while length:
            if RpM(self.h_process, address, buffer, bytes, byref(bytesread)) or (use_NtWow64ReadVirtualMemory64 and GetLastError()==0):
                if bytesread.value:
                    data += buffer.raw[:bytesread.value]
                    length -= bytesread.value
                    address += bytesread.value
                if not len(data):
                    raise ProcessException('Error %s in ReadProcessMemory(%08x, %d, read=%d)' % (GetLastError(),
                     address,
                     length,
                     bytesread.value))
                return data
            else:
                raise WinError()
            data += buffer.raw[:bytesread.value]
            length -= bytesread.value
            address += bytesread.value
        return data

    def read(self, address, type = 'uint', maxlen = 50):
        if type == 's' or type == 'string':
            s = self.read_bytes(int(address), bytes=maxlen)
            news = ''
            for c in s:
                if c == '\x00':
                    return news
                news += c

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

    def get_symbolic_name(self, address):
        for m in self.list_modules():
            if int(m.modBaseAddr) <= int(address) < int(m.modBaseAddr + m.modBaseSize):
                return '%s+0x%08X' % (m.szModule, int(address) - m.modBaseAddr)

        return '0x%08X' % int(address)

    def list_modules(self):
        """
        return a list of <MODULEENTRY32>
        """
        module_list = []
        if self.process32 is not None:
            hModuleSnap = CreateToolhelp32Snapshot(TH32CS_CLASS.SNAPMODULE, self.process32.th32ProcessID)
            if hModuleSnap is not None:
                module_entry = MODULEENTRY32()
                module_entry.dwSize = sizeof(module_entry)
                success = Module32First(hModuleSnap, byref(module_entry))
                while success:
                    if module_entry.th32ProcessID == self.process32.th32ProcessID:
                        module_list.append(copy.copy(module_entry))
                    success = Module32Next(hModuleSnap, byref(module_entry))

                CloseHandle(hModuleSnap)
        return module_list

    def hasModule(self, module):
        if module[-4:] != '.dll':
            module += '.dll'
        module_list = self.list_modules()
        for m in module_list:
            if module in m.szExePath.split('\\'):
                return True

        return False

    def get_instruction(self, address):
        """
        Pydasm disassemble utility function wrapper. Returns the pydasm decoded instruction in self.instruction.
        """
        import pydasm
        try:
            data = self.read_bytes(int(address), 32)
        except:
            return 'Unable to disassemble at %08x' % address

        return pydasm.get_instruction(data, pydasm.MODE_32)

