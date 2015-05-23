# memorpy
Python library using ctypes to search/edit windows programs memory

#usage examples :
```python
>>> from memorpy import *
>>> mw=MemWorker("notepad")
>>> l=[x for x in mw.umem_search("hello")]
>>> l
[<Addr: 0x003287B0>]
>>> a=l[0]
>>> a
<Addr: 0x003287B0>
>>> a+4
<Addr: 0x003287B4>
>>> print a
<Addr: 0x003287B0 : "h\x00e\x00l\x00l\x00o\x00 \x00t\x00h\x00i\x00s\x00 \x00i\x0
0s\x00 \x00a\x00 \x00m\x00e\x00s\x00s\x00a\x00g\x00e\x00 \x00I\x00" (bytes)>
>>> (a+4).read(4)
'l\x00l\x00'
>>> a.read(100).decode("utf-16-le")
u'hello this is a message I typed in notepad.exe !\x00\x00'
>>> a.write("pwned".encode("utf-16-le"))
1
>>> a.read(100).decode("utf-16-le")
u'pwned this is a message I typed in notepad.exe !\x00\x00'
```