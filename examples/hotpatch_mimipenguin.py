#!/usr/bin/env python
# -*- coding: UTF8 -*-
# Author: Nicolas VERDIER (contact@n1nj4.eu)

"""
    Poc to show how to mitigate the awesome mimipenguin script (https://github.com/huntergregal/mimipenguin)
    This script run mimipenguin.sh, search for the cleartext passwords offsets in memory and override the passwords with xxxx
    Only tested with gnome-keyring and Ubuntu 16.04, no crash so far :=)
"""
import sys, os
import subprocess
import urllib2
try:
    from memorpy import *
except ImportError as e:
    print ("%s\ninstall with: \"pip install https://github.com/n1nj4sec/memorpy/archive/master.zip\""%e)
    exit(1)

if os.geteuid()!=0:
    print "mimipenguin.sh needs root ;)"
    exit(1)

if not os.path.isfile("mimipenguin.sh"):
    mimipenguin_url="https://raw.githubusercontent.com/huntergregal/mimipenguin/master/mimipenguin.sh"
    print ("missing mimipenguin.sh, downloading it from %s"%mimipenguin_url)
    res=urllib2.urlopen(mimipenguin_url).read()
    with open("mimipenguin.sh",'wb') as w:
        w.write(res)
print "[+] running mimipenguin.sh to retrieve current passwords ..."
res=subprocess.check_output(["bash","mimipenguin.sh"])

rules = [
    {
        "type" : "[SYSTEM - GNOME]",
        "process" : "gnome-keyring-daemon"
    },
    {
        "type" : "[SYSTEM - GNOME]",
        "process" : "gdm-password"
    },
    {
        "type" : "[SYSTEM - SSH]",
        "process" : "sshd:"
    }
]

passwd_found=False
for line in res.split('\n'):
    for rule in rules:
        if rule["type"] in line:
            user,password=line[len(rule["type"])+1:].split(":",1)
            user=user.strip()
            password=password.strip()
            print "[i] user's %s password found, let's overwrite memory"%user
            try:
                gk=MemWorker(name=rule["process"])
            except Exception as e:
                print "[-] %s"%e
                continue
            for x in gk.mem_search(password):
                print "[i] writing password xxxx at offset %s"%hex(x)
                x.write("x"*len(password))
            passwd_found=True
if passwd_found:
    print "[+] all passwords overwritten :-) "
else:
    print "[+] no passwords found ! gnome was already hotpatched ? "




