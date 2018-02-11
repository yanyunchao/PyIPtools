# PyIPtools
一个用python开发的简洁IP计算工具

支持 Python2、Python3

[![Build status](https://travis-ci.org/rq/rq.svg?branch=master)](https://secure.travis-ci.org/rq/rq)
[![PyPI](https://img.shields.io/pypi/pyversions/rq.svg)](https://pypi.python.org/pypi/rq)

## Installation

from source:

```
sudo python setup.py install
```



## Getting Started

```python
# CIDR
>>> from iptools import CIDR
>>> c = CIDR('172.16.0.0/12')
>>> c.subnet_mask
255.240.0.0
>>> c.subnet
172.16.0.0
>>> c.first_ip_address
172.16.0.1
>>> c.last_ip_address
172.31.255.254
>>> c.broadcast
172.31.255.255

# ipv4 format
>>> from iptools import ipv4_format
>>> ipv4_format('10.48.240.1')
00001010.00110000.11110000.00000001

# ipv4 convert
>>> from iptools import convert_to_ipv4
>>> convert_to_ipv4('0A.00.00.FF', stype='x')
10.0.0.255

# chech ip
>>> from iptools import is_ip_in_subnet
>>> is_ip_in_subnet('172.25.32.5', '172.16.0.0/12')
True
```



## API Reference

to be continued



## Author

PyIPtool is developed and maintained by yanyunchao@vip.qq.com.
