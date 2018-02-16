# -*- coding: utf-8 -*-

from __future__ import unicode_literals

from pyiptools.utils import int


private_ipv4_classes = (
    '10.0.0.0/8',
    '172.16.0.0/12',
    '192.168.0.0/16',
)


class IPV4(object):
    """
    ipv4封装
    """
    def __init__(self, ip, **kwargs):
        self._ip = ip
        self._ip_list = []
        self.check()

    def check(self):
        if isinstance(self._ip, (list, tuple)):
            self._ip = '.'.join([str(i) for i in self._ip])

        check_res = is_string_ipv4(self._ip)
        if check_res[0]:
            self._ip = check_res[1]
            self._ip_list = [int(i) for i in self._ip.split('.')]
        else:
            raise ValueError('not a valid ip')

    @property
    def ip_str(self):
        return self._ip

    @property
    def ip_list(self):
        return self._ip_list

    def to_bin(self):
        return ipv4_format(self.ip_str, ftype='b')

    def to_hex(self):
        pass

    def to_oct(self):
        pass


class CIDR(object):
    """
    CIDR, 解释见 https://en.wikipedia.org/wiki/Classless_Inter-Domain_Routing

    cidr = CIDR('10.10.10.10/16')
    cidr = CIDR('10.10.10.10/255.255.0.0')
    """
    def __init__(self, ip_mask):
        self.ip, self.mask_code = self.check(ip_mask)

    @staticmethod
    def check(ip_mask):
        sub_net_ip, mask = ip_mask.split('/')

        ip = IPV4(sub_net_ip)
        try:
            mask_code = int(mask)
        except ValueError:
            mask_code = subnet_mask_to_cidr_mask(mask)
        if 0 <= mask_code <= 32:
            return ip.ip_str, mask_code
        raise ValueError('%s is not a valid cidr.' % ip_mask)

    @property
    def subnet(self):
        """
        网络
        :return:
        """
        try:
            return self._subnet
        except AttributeError:
            self._subnet = convert_to_ipv4(
                ipv4_format(self.ip, ftype='int') &
                cidr_mask_to_ip_int(self.mask_code),
                stype='int'
            )
            return self._subnet

    @property
    def subnet_mask(self):
        """
        子网掩码：点分形式
        :return:
        """
        try:
            return self._subnet_mask
        except AttributeError:
            self._subnet_mask = cidr_mask_to_subnet_mask(self.mask_code)
            return self._subnet_mask

    @property
    def first_ip_address(self):
        """
        第一个可用的ip
        :return:
        """
        try:
            return self._first_ip_address
        except AttributeError:
            self._first_ip_address = convert_to_ipv4(
                ipv4_format(self.subnet, ftype='int') + 1,
                stype='int'
            )
            return self._first_ip_address

    @property
    def last_ip_address(self):
        """
        最后一个可用的ip
        :return:
        """
        try:
            return self._last_ip_address
        except AttributeError:
            self._last_ip_address = convert_to_ipv4(
                ipv4_format(self.broadcast, ftype='int') - 1,
                stype='int'
            )
            return self._last_ip_address

    @property
    def broadcast(self):
        """
        广播
        :return:
        """
        try:
            return self._broadcast
        except AttributeError:
            self._broadcast = convert_to_ipv4(
                ipv4_format(self.subnet, ftype='int') +
                (1 << 32 - self.mask_code) - 1,
                stype='int'
            )
            return self._broadcast

    def ip_list(self):
        pass


def is_string_ipv4(string):
    """
    判断一个字符串是否符合ipv4地址规则
    :param string:  输入的字符串
    :return: (bool, string)
    """
    string = string.strip()
    seg = string.split('.')
    if len(seg) != 4:
        return False, None
    else:
        try:
            if not all([_si.isdigit() and -1 < int(_si) < 256
                        for _si in seg]):
                return False, None
            return True, string
        except ValueError:
            return False, None


def is_string_ipv6(string):
    """
    判断一个字符串是否符合ipv6地址规则
    :param string: 输入的字符串
    :return: (bool, string)
    """
    string = string.lower().strip()

    def is_ipv6_seg(seg):
        try:
            return all([-1 < int(_si, base=16) < 65536 and
                        _si.isalnum() and len(_si.strip()) < 5
                        for _si in seg if _si != ''])
        except ValueError:
            return False

    def normal_ipv6(string, len_limit=8):
        seg = string.split(':')
        if len(seg) != len_limit:
            return False
        else:
            if is_ipv6_seg(seg):
                return True, string
            else:
                return False, None

    def zero_compression_ipv6(string, len_limit=8):
        def is_not_colon_both_end(string):
            return not(string.startswith(':') or string.endswith(':'))

        seg = string.split('::')
        if (len(seg) == 2 and is_not_colon_both_end(seg[0]) and
                is_not_colon_both_end(seg[1])):
            seg_v6, seg_len = [], 0
            for _str in seg:
                tmp = _str.split(':')
                seg_v6.extend(tmp)
                seg_len += len(tmp) if _str else 0
            if seg_len <= len_limit - 2 and is_ipv6_seg(seg_v6):
                return True, string
            else:
                return False, None
        else:
            return False, None

    def ipv6_with_ipv4(string):
        seg = string.rpartition(':')
        if '::' in seg[0]:
            ipv6_part = zero_compression_ipv6(seg[0], len_limit=6)
        else:
            ipv6_part = normal_ipv6(string, len_limit=6)

        ipv4_part = is_string_ipv4(seg[-1])

        if ipv6_part[0] and ipv4_part[0]:
            return True, string
        else:
            return False, None

    if ':' in string and '.' in string:
        return ipv6_with_ipv4(string)
    elif '::' in string:
        return zero_compression_ipv6(string)
    else:
        return normal_ipv6(string)


def is_ipv4_in_range(ip_str, range_str):
    """
    判断一个ip是否在一个ip范围内
    :param ip_str:
    :param range_str:
    :return:
    """
    ip_seg = ip_str.split('.')
    range_seg = range_str.split('.')

    for i, _str in enumerate(range_seg):
        if _str == '*':
            continue
        if '-' in _str:
            sp = _str.split('-')
            if not (sp[0] <= ip_seg[i] <= sp[1]):
                return False
        elif ip_seg[i] != _str:
                return False
    return True


def is_legal_ipv4(string):
    pass


def is_legal_ipv6(string):
    pass


def ipv4_format(ipv4_str, ftype='b', **kwargs):
    """
    ip格式化转换
    :param ipv4_str:
    :param ftype:
        int: 一个整数
        b: 二进制
        o: 八进制
        x: 十六进制
    :param kwargs:
        filling: 是否以0填充
        separator: 分隔符，默认为 '.'
    :return:
    """
    ipv4_check = is_string_ipv4(ipv4_str)
    if ipv4_check[0]:
        ipv4_str = ipv4_check[1]
        ip_segs = ipv4_str.split('.')

        if ftype == 'int':
            dec_value = 0
            for i, ip_seg in enumerate(ip_segs):
                dec_value += int(ip_seg) << (24 - 8 * i)
            return dec_value
        elif ftype in ('b', 'o', 'x'):
            res = []
            for ip_seg in ip_segs:
                seg_str = format(int(ip_seg), ftype)
                if kwargs.get('filling', True):
                    seg_str = '0' * (len(format(255, ftype)) -
                                     len(seg_str)) + seg_str
                res.append(seg_str)
            separator = kwargs.get('separator', '.')
            return separator.join(res)
        else:
            raise ValueError('ftype: %s not support' % ftype)
    raise ValueError('%s not a normal IP.' % ipv4_str)


def convert_to_ipv4(source, stype='d'):
    """
    转换为常见的ip地址
    :param source:
    :param stype:
    :return:
    """
    base_map = {
        'b': 2,
        'o': 8,
        'd': 10,
        'x': 16,
    }
    if stype == 'int':
        source = format(int(source), 'b')
        stype = 'b'
    if '.' not in source:
        seg_len = len(format(255, stype))
        max_len = seg_len * 4
        if len(source) <= max_len:
            _source = ('0' * max_len + source)[-max_len:]
            _ipv4_segs = [_source[ix:ix + seg_len]
                          for ix in range(0, max_len, seg_len)]

            source = '.'.join(_ipv4_segs)
        else:
            raise ValueError('len of source error')

    if stype in base_map:
        segs = [str(int(seg, base=base_map[stype]))
                for seg in source.split('.')]
        ipv4_str = '.'.join(segs)
        check = is_string_ipv4(ipv4_str)
        if check[0]:
            return check[1]
        else:
            raise ValueError('invalid ip for source: %s' % source)
    else:
        raise ValueError('invalid ftype arg: %s' % stype)


def is_ip_in_subnet(ipv4_str, subnet_str):
    """
    判断ip是否在子网中
    :param ipv4_str:
    :param subnet_str: 10.10.10.10/16
    :return:
    """
    cidr = CIDR(subnet_str)
    sub_net_ip, mask_code = cidr.ip, cidr.mask_code
    res = (ipv4_format(ipv4_str, ftype='int') &
           cidr_mask_to_ip_int(int(mask_code))
           == ipv4_format(sub_net_ip, ftype='int'))
    return res


def is_private_ipv4(ipv4_str):
    """
    是否为一个私有ip
    :param ipv4_str:
    :return:
    """
    check = is_string_ipv4(ipv4_str)
    if not check[0]:
        return False
    return any([is_ip_in_subnet(check[1], range_i)
                for range_i in private_ipv4_classes])


def cidr_mask_to_ip_int(mask_num):
    """
    掩码位数转换为整数值
    :param mask_num: 16
    :return:
    """
    cidr_num = int(mask_num)
    if 0 < cidr_num <= 32:
        return ((1 << cidr_num) - 1) << (32 - cidr_num)
    raise ValueError('% is not valid cidr code.' % cidr_num)


def cidr_mask_to_subnet_mask(mask_num):
    """
    掩码位数转换为点分掩码
    :param mask_num:
    :return:
    """
    return convert_to_ipv4(cidr_mask_to_ip_int(mask_num), stype='int')


def subnet_mask_to_cidr_mask(subnet_mask):
    """
    点分掩码转换为掩码位数
    :param subnet_mask:
    :return:
    """
    subnet_bin = ipv4_format(subnet_mask, ftype='b', separator='')
    cidr_mask, _, check = subnet_bin.partition('0')
    if int(check or '0', base=2):
        raise ValueError('%s is not valid subnet mask.' % subnet_mask)
    return len(cidr_mask)
