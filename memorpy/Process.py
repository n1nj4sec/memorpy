#!/usr/bin/env python
# -*- coding: UTF8 -*-

import sys
from BaseProcess import *
if sys.platform=='win32':
    from WinProcess import WinProcess as Process
else:
    from LinProcess import LinProcess as Process
