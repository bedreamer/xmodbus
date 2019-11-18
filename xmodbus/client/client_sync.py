# -*- coding: utf-8 -*-
# author: lijie
import xmodbus.client as client
import xmodbus.pdu as pdu


class SyncModbusClient(client.ModbusClient):
    """同步方式的modbus客户端"""
    def process_adu_request(self, request_adu, timeout=None):
        """发送并ADU请求"""
        bytes_data = request_adu.encode()
        self.channel.sync_write(bytes_data)

        # 复位帧产生器，准备接收数据
        self.framer.reset()
        while True:
            need = self.framer.response_need_bytes_count(request_adu)
            if need <= 0:
                break

            data = self.channel.sync_read(need)
            if len(data) == 0:
                break

            self.framer.push(data)

        if self.framer.is_response_ready(request_adu):
            pass

        return self.framer.get_response_adu(request_adu)

    def open(self):
        """执行客户端的打开操作，若初始化时制定了auto_open=True则不需要显示调用"""
        return self.channel.sync_open(self)

    def read_coils(self, address, quantity, unit_id):
        """读线圈"""
        request = pdu.ReadCoilsRequest(address, quantity)
        adu = self.framer.build_request_adu(request, unit_id)
        return self.process_adu_request(adu)

    def read_discrete_inputs(self, address, quantity, unit_id):
        """读离散输入"""
        request = pdu.ReadDiscreteInputsRequest(address, quantity)
        adu = self.framer.build_request_adu(request, unit_id)
        return self.process_adu_request(adu)

    def read_holding_registers(self, address, quantity, unit_id):
        """读保持寄存器"""
        request = pdu.ReadHoldingRegistersRequest(address, quantity)
        adu = self.framer.build_request_adu(request, unit_id)
        return self.process_adu_request(adu)

    def read_input_register(self, address, quantity, unit_id):
        """读输入寄存器"""
        request = pdu.ReadInputRegisterRequest(address, quantity)
        adu = self.framer.build_request_adu(request, unit_id)
        return self.process_adu_request(adu)

    def write_single_coil(self, address, on_or_off, unit_id):
        """写单个线圈"""
        request = pdu.WriteSingleCoilRequest(address, on_or_off)
        adu = self.framer.build_request_adu(request, unit_id)
        return self.process_adu_request(adu)

    def write_single_register(self, address, value, unit_id):
        """写单个寄存器"""
        request = pdu.WriteSingleRegisterRequest(address, value)
        adu = self.framer.build_request_adu(request, unit_id)
        return self.process_adu_request(adu)

    def write_multiple_coils(self, address, coils, unit_id):
        """写多个线圈"""
        request = pdu.WriteMultipleCoilsRequest(address, coils)
        adu = self.framer.build_request_adu(request, unit_id)
        return self.process_adu_request(adu)

    def write_multiple_registers(self, address, values, unit_id):
        """写多个寄存器"""
        request = pdu.WriteMultiRegistersRequest(address, values)
        adu = self.framer.build_request_adu(request, unit_id)
        return self.process_adu_request(adu)

    def read_device_identification(self, obj_id, unit_id):
        """读设备信息"""
        request = pdu.ReadDeviceIdentificationRequest(obj_id)
        adu = self.framer.build_request_adu(request, unit_id)
        return self.process_adu_request(adu)

    def close(self):
        """关闭"""
