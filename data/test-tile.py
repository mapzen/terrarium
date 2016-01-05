#!/usr/bin/env python
import os
from terrarium import makeTile

path = '../data/B'

if not os.path.exists(path):
    os.makedirs(path)

makeTile(path, 82, 198, 9, True)