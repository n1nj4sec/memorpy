from memorpy import MemWorker
mw=MemWorker.MemWorker(pid=7808) #you can also select a process by its name with the kwarg name=
# print([hex(x) for x in list("Sweet dreams".encode('utf-16LE'))])
generator = mw.mem_search("Sweet dreams".encode('utf-16LE'), start_offset=0x40000000, end_offset=0x60000000)
l = [x for x in generator]
print(l)