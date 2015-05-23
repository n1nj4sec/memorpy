# memorpy
Python library using ctypes to search/edit windows programs memory

#usage examples :
in this example open a notepad.exe (x32) and type in some text we will edit from memory !
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
<Addr: 0x003287B0 : "h\x00e\x00l\x00l\x00o\x00 \x00t\x00h\x00i\x00s\x00 \x00i\x00s\x00 \x00a\x00 \x00m\x00e\x00s\x00s\x00a\x00g\x00e\x00 \x00I\x00" (bytes)>
>>> a.read(100).decode("utf-16-le")
u'hello this is a message I typed in notepad.exe !\x00\x00'
>>> a.write("pwned".encode("utf-16-le"))
1
>>> a.read(100).decode("utf-16-le")
u'pwned this is a message I typed in notepad.exe !\x00\x00'
```
look back at your notepad and the text should be changed ! :)
A quicker way to do this could be :
```python
>>> mw.umem_replace("hello","pwned")
```

Some other interesting features like searching for different values types in memory and monitor their changes are also implemented through the Locator class. For example if you are looking to cheat in a game and you start with 200 ammo, you could do something like :

```python
>>> lo=Locator(mw)
>>> lo.feed(200)
...
<Addr: 0x0018FDE2>,
<Addr: 0x0018FDE4>,
<Addr: 0x0018FDE6>,
...]}
```
use some ammo and "refeed" the locator (do this a couple of times until there is one result left)
```python
>>> lo.feed(199)
{'double': [],
 'float': [],
 'int': [<Addr: 0x0019FAF0>],
 'long': [],
 'short': [],
 'uint': [],
 'ulong': [],
 'ushort': []}
>>> a=_["int"][0]
>>> a.read()
199
>>>a.write(999999)
1
```
now you have infinite ammo :o)
I hope this code will be useful to someone
Have fun !
