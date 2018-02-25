

import pyiptools


class TestCIDR(object):
    cidr_obj = pyiptools.CIDR('10.0.0.5/24')

    def test_subnet(self):
        assert self.cidr_obj.subnet == '10.0.0.0'

    def test_subnet_mask(self):
        assert self.cidr_obj.subnet_mask == '255.255.255.0'

    def test_first_ip_address(self):
        assert self.cidr_obj.first_ip_address == '10.0.0.1'

    def test_last_ip_address(self):
        assert self.cidr_obj.last_ip_address == '10.0.0.254'

    def test_broadcast(self):
        assert self.cidr_obj.broadcast == '10.0.0.255'


def test_is_string_ipv4():
    assert pyiptools.is_string_ipv4('10.5.25.6') == (True, '10.5.25.6')
    assert pyiptools.is_string_ipv4('10.5.256.6') == (False, None)


def test_is_string_ipv6():
    assert pyiptools.is_string_ipv6('fe80::9d2a:fc30:d071:66f1')[0] is True


def test_ipv4_format():
    assert pyiptools.ipv4_format('10.25.5.8', ftype='b', separator='') == \
           '00001010000110010000010100001000'


def test_convert_to_ipv4():
    assert pyiptools.convert_to_ipv4('00001010.00011001.00000101.00001000',
                                     stype='b') == '10.25.5.8'


def test_is_ip_in_subnet():
    assert pyiptools.is_ip_in_subnet('172.20.5.0', '172.16.0.0/12') is True
    assert pyiptools.is_ip_in_subnet('172.32.5.0', '172.16.0.0/12') is False


def test_is_private_ipv4():
    assert pyiptools.is_private_ipv4('172.20.5.0') is True
    assert pyiptools.is_private_ipv4('123.66.129.235') is False
