# -*- coding: utf-8 -*-

from __future__ import unicode_literals

import platform
import six
import shlex
import subprocess

if six.PY2:
    int = long
else:
    int = int

IS_WIN = IS_LINUX = IS_OTHER_ARCH = False

arch = platform.system()

if arch == 'Windows':
    IS_WIN = True
elif arch == 'Linux':
    IS_LINUX = True
else:
    IS_OTHER_ARCH = True


def run_cmd(cmd, **kwargs):
    args = shlex.split(cmd)
    _input = kwargs.pop('input', None)
    p = subprocess.Popen(args=args,
                         stdout=subprocess.PIPE,
                         stdin=subprocess.PIPE,
                         **kwargs)
    return p.communicate(_input)
