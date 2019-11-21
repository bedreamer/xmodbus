# -*- coding: utf-8 -*-
# author: lijie
class ModbusRegister(object):
    """modbus 寄存器定义"""
    def __init__(self, address):
        self._address = address

    @property
    def address(self):
        return self._address


class BitAccessProtocol:
    """位访问协议"""
    def __init__(self):
        self._bit_map = dict()

    def define(self, bit, on_name, off_name):
        BitMap = namedtuple('BitMap', ('on_name', 'off_name'))
        self._bit_map[bit] = BitMap(on_name, off_name)


class BinAccessProtocol:
    """数据访问协议"""


class DiscretesInputRegister(ModbusRegister):
    """modbus 离散输入寄存器"""
    _writable = False

    def __init__(self, address, access_protocol):
        super().__init__(address)
        self.access_protocol = access_protocol


class CoilsRegister(ModbusRegister):
    """线圈寄存器定义"""
    _writable = True

    def __init__(self, address, access_protocol):
        super().__init__(address)
        self.access_protocol = access_protocol


class InputRegister(ModbusRegister):
    """输入寄存器"""
    _writable = False

    def __init__(self, address, access_protocol):
        super().__init__(address)
        self.access_protocol = access_protocol


class HoldingRegister(ModbusRegister):
    """保持寄存器"""
    _writable = True

    def __init__(self, address, access_protocol):
        super().__init__(address)
        self.access_protocol = access_protocol
