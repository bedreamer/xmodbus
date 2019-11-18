# -*- coding: utf-8 -*-
# author: lijie
import xmodbus.framer.framer_rtu as rtu


class ModbusClient(object):
    """modbus客户端基类"""
    def __init__(self, channel, framer_cls=None, auto_open=None):
        self.channel = channel
        if framer_cls is None:
            framer_cls = rtu.RTUFramer
        self.framer = framer_cls(self, channel)

        if auto_open is None:
            auto_open = True

        if auto_open:
            self.open()

    def process_adu_request(self, adu, timeout=None):
        raise NotImplementedError

    def open(self):
        raise NotImplementedError

    def read_coils(self, address, quantity, unit_id):
        """读线圈"""
        raise NotImplementedError

    def read_discrete_inputs(self, address, quantity, unit_id):
        """读离散输入"""
        raise NotImplementedError

    def read_holding_registers(self, address, quantity, unit_id):
        """读保持寄存器"""
        raise NotImplementedError

    def read_input_register(self, address, quantity, unit_id):
        """读输入寄存器"""
        raise NotImplementedError

    def write_single_coil(self, address, on_or_off, unit_id):
        """写单个线圈"""
        raise NotImplementedError

    def write_single_register(self, address, value, unit_id):
        """写单个寄存器"""
        raise NotImplementedError

    def write_multiple_coils(self, address, coils, unit_id):
        """写多个线圈"""
        raise NotImplementedError

    def write_multiple_registers(self, address, values, unit_id):
        """写多个寄存器"""
        raise NotImplementedError

    def close(self):
        """关闭"""
        raise NotImplementedError
