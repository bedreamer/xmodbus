# -*- coding: utf-8 -*-
# author: lijie
import math
import struct


class PDURequest:
    def encode(self):
        """将对象处理成字节序列"""
        raise NotImplementedError

    def decode(self, data):
        """将字节序列处理成PDU可操作对象"""

    @property
    def function_name(self):
        return self.__class__.__doc__

    def get_response_pdu_length(self):
        """返回应答长度元组（correct-response-length, incorrect-response-length）"""
        raise NotImplementedError

    def get_response_pdu_data_length(self):
        correct_pdu_count, incorrect_pdu_count = self.get_response_pdu_length()
        return correct_pdu_count - 1, incorrect_pdu_count - 1

    @property
    def response_pdu_pair(self):
        raise NotImplementedError

    def make_response_pdu_pair(self, response_pdu_fx, response_pud_data):
        if response_pdu_fx & 0x80:
            return PDUResponseError(self, response_pdu_fx, response_pud_data)
        return self.response_pdu_pair(self, response_pdu_fx, response_pud_data)


class PDUResponse:
    """应答PDU"""
    def __init__(self, request_pdu, pdu_fx, pdu_data):
        self.request = request_pdu
        self.fx = pdu_fx
        self.data = pdu_data

    def as_dict(self):
        raise NotImplementedError


class PDUResponseError(PDUResponse):
    """错误应答PDU"""
    def __init__(self, request_pdu, pdu_fx, pdu_data):
        super().__init__(request_pdu, pdu_fx, pdu_data)
        self.error_code = struct.unpack('B', pdu_data)[0]

    def as_dict(self):
        return {'fx': (self.fx & 0x7F), 'code': self.error_code}


class ReadCoilsRequest(PDURequest):
    """读线圈"""
    fx = 0x01

    def __init__(self, address, quantity):
        self.address = address
        self.quantity = quantity

    def get_response_pdu_length(self):
        n = math.ceil(self.quantity/8)

        # CORRECT RESPONSE
        # function-code 1 byte
        # byte count    1 byte
        # coils status  n
        correct_response_length = 2 + n

        # INCORRECT RESPONSE
        # function-code     1 byte
        # exception code    1 byte
        incorrect_response_length = 2

        return correct_response_length, incorrect_response_length

    def encode(self):
        return struct.pack('>BHH', self.fx, self.address, self.quantity)

    @property
    def response_pdu_pair(self):
        return ReadCoilsResponse


class ReadCoilsResponse(PDUResponse):
    """读线圈应答"""
    def __init__(self, request_pdu, pdu_fx, pdu_data):
        super().__init__(request_pdu, pdu_fx, pdu_data)

    def as_dict(self):
        coils = dict()

        begin = self.request.address
        quantity = self.request.quantity

        bits_list = list()
        for b in self.data[1:]:
            bits = bin(b)[2:][::-1]
            bits = bits + '0' * (8 - len(bits))
            bits_list.append(bits)

        for b in ''.join(bits_list):
            if quantity == 0:
                break

            coils[begin] = 'on' if b == '1' else 'off'
            begin += 1
            quantity -= 1

        return {'fx': self.fx, 'data': coils}


class ReadDiscreteInputsRequest(PDURequest):
    """读离散输入"""
    fx = 0x02

    def __init__(self, address=None, quantity=None):
        self.address = address or 0
        self.quantity = quantity or 0

    def get_response_pdu_length(self):
        n = math.ceil(self.quantity/8)

        # CORRECT RESPONSE
        # function-code 1 byte
        # byte count    1 byte
        # coils status  n
        correct_response_length = 2 + n

        # INCORRECT RESPONSE
        # function-code     1 byte
        # exception code    1 byte
        incorrect_response_length = 2

        return correct_response_length, incorrect_response_length

    def encode(self):
        return struct.pack('>BHH', self.fx, self.address, self.quantity)

    @property
    def response_pdu_pair(self):
        return ReadDiscreteInputsResponse


class ReadDiscreteInputsResponse(PDUResponse):
    """读离散输入应答"""
    def __init__(self, request_pdu, pdu_fx, pdu_data):
        super().__init__(request_pdu, pdu_fx, pdu_data)

    def as_dict(self):
        coils = dict()

        begin = self.request.address
        quantity = self.request.quantity

        bits_list = list()
        for b in self.data[1:]:
            bits = bin(b)[2:][::-1]
            bits = bits + '0' * (8 - len(bits))
            bits_list.append(bits)

        for b in ''.join(bits_list):
            if quantity == 0:
                break

            coils[begin] = 'on' if b == '1' else 'off'
            begin += 1
            quantity -= 1

        return {'fx': self.fx, 'data': coils}


class ReadHoldingRegistersRequest(PDURequest):
    """读保持寄存器"""
    fx = 0x03

    def __init__(self, address, quantity):
        self.address = address
        self.quantity = quantity

    def get_response_pdu_length(self):
        # CORRECT RESPONSE
        # function-code 1 byte
        # byte count    1 byte
        # coils status  2 * n
        correct_response_length = 2 + self.quantity * 2

        # INCORRECT RESPONSE
        # function-code     1 byte
        # exception code    1 byte
        incorrect_response_length = 2

        return correct_response_length, incorrect_response_length

    def encode(self):
        return struct.pack('>BHH', self.fx, self.address, self.quantity)

    @property
    def response_pdu_pair(self):
        return ReadHoldingRegistersResponse


class ReadHoldingRegistersResponse(PDUResponse):
    """读保持寄存器应答"""
    def __init__(self, request_pdu, pdu_fx, pdu_data):
        super().__init__(request_pdu, pdu_fx, pdu_data)

    def as_dict(self):
        registers = dict()

        begin = self.request.address
        quantity = self.request.quantity

        fmt = '>{}H'.format(self.request.quantity)
        values = struct.unpack(fmt, self.data[1:])

        for val in values:
            if quantity == 0:
                break
            registers[begin] = val
            begin += 1
            quantity -= 1

        return {'fx': self.fx, 'data': registers}


class ReadInputRegisterRequest(PDURequest):
    """读输入寄存器"""
    fx = 0x04

    def __init__(self, address, quantity):
        self.address = address
        self.quantity = quantity

    def get_response_pdu_length(self):
        # CORRECT RESPONSE
        # function-code 1 byte
        # byte count    1 byte
        # coils status  2 * n
        correct_response_length = 2 + self.quantity * 2

        # INCORRECT RESPONSE
        # function-code     1 byte
        # exception code    1 byte
        incorrect_response_length = 2

        return correct_response_length, incorrect_response_length

    def encode(self):
        return struct.pack('>BHH', self.fx, self.address, self.quantity)

    @property
    def response_pdu_pair(self):
        return ReadInputRegisterResponse


class ReadInputRegisterResponse(PDUResponse):
    """读输入寄存器应答"""
    def __init__(self, request_pdu, pdu_fx, pdu_data):
        super().__init__(request_pdu, pdu_fx, pdu_data)

    def as_dict(self):
        registers = dict()

        begin = self.request.address
        quantity = self.request.quantity

        fmt = '>{}H'.format(self.request.quantity)
        values = struct.unpack(fmt, self.data[1:])

        for val in values:
            if quantity == 0:
                break
            registers[begin] = val
            begin += 1
            quantity -= 1

        return {'fx': self.fx, 'data': registers}


class WriteSingleCoilRequest(PDURequest):
    """写单个线圈"""
    fx = 0x05

    def __init__(self, address, value):
        self.address = address

        if isinstance(value, bool):
            if value is True:
                value = 0xff00
            else:
                value = 0x0000
        elif isinstance(value, str):
            if value.lower() == 'on':
                value = 0xff00
            elif value.lower() == 'off':
                value = 0x0000
            else:
                raise ValueError('线圈值必须是True, False，1，0，`on`，`off`')
        elif value == 0:
            value = 0x0000
        elif value == 1:
            value = 0xff00
        else:
            raise ValueError('线圈值必须是True, False，1，0，`on`，`off`')

        self.value = value

    def get_response_pdu_length(self):
        # CORRECT RESPONSE
        # function-code     1 byte
        # output address    2 byte
        # output value      2 byte
        correct_response_length = 5

        # INCORRECT RESPONSE
        # function-code     1 byte
        # exception code    1 byte
        incorrect_response_length = 2

        return correct_response_length, incorrect_response_length

    def encode(self):
        return struct.pack('>BHH', self.fx, self.address, self.value)

    @property
    def response_pdu_pair(self):
        return WriteSingleCoilResponse


class WriteSingleCoilResponse(PDUResponse):
    """写单个线圈应答"""
    def __init__(self, request_pdu, pdu_fx, pdu_data):
        super().__init__(request_pdu, pdu_fx, pdu_data)

    def as_dict(self):
        address, value = struct.unpack('>HH', self.data)
        if value == 0xff00:
            value = 'on'
        else:
            value = 'off'
        return {'fx': self.fx, 'data': {'address': address, 'value': value}}


class WriteSingleRegisterRequest(PDURequest):
    """写单个寄存器"""
    fx = 0x06

    def __init__(self, address, value):
        self.address = address
        self.value = value

    def get_response_pdu_length(self):
        # CORRECT RESPONSE
        # function-code     1 byte
        # register address    2 byte
        # register value      2 byte
        correct_response_length = 5

        # INCORRECT RESPONSE
        # function-code     1 byte
        # exception code    1 byte
        incorrect_response_length = 2

        return correct_response_length, incorrect_response_length

    def encode(self):
        return struct.pack('>BHH', self.fx, self.address, self.value)

    @property
    def response_pdu_pair(self):
        return WriteSingleRegisterResponse


class WriteSingleRegisterResponse(PDUResponse):
    """写单个寄存器应答"""
    def __init__(self, request_pdu, pdu_fx, pdu_data):
        super().__init__(request_pdu, pdu_fx, pdu_data)

    def as_dict(self):
        address, value = struct.unpack('>HH', self.data)
        return {'fx': self.fx, 'data': {'address': address, 'value': value}}


class WriteMultipleCoilsRequest(PDURequest):
    """写多个线圈"""
    fx = 0x0F

    def __init__(self, address, coils):
        self.address = address
        self.coils = coils

    def get_response_pdu_length(self):
        # CORRECT RESPONSE
        # function-code     1 byte
        # starting address  2 byte
        # quantity          2 byte
        correct_response_length = 5

        # INCORRECT RESPONSE
        # function-code     1 byte
        # exception code    1 byte
        incorrect_response_length = 2

        return correct_response_length, incorrect_response_length

    @staticmethod
    def _encode_coils(coils_list):
        for idx, value in enumerate(coils_list):
            if value in {1, 0}:
                continue

            if isinstance(value, bool):
                if value is True:
                    coils_list[idx] = 1
                else:
                    coils_list[idx] = 0
            elif isinstance(value, str):
                if value.lower() == 'on':
                    coils_list[idx] = 1
                elif value.lower() == 'off':
                    coils_list[idx] = 0
                else:
                    raise ValueError('线圈值必须是True, False，1，0，`on`，`off`')
            else:
                raise ValueError('线圈值必须是True, False，1，0，`on`，`off`')

        str_coils = ''.join([str(v) for v in coils_list])
        padding = '0' * (8 - (len(str_coils) % 8))
        coils = ''.join([str_coils, padding])[::-1]
        bx = list()
        for ib in range(int(len(coils)/8)):
            x = struct.pack('B', int(coils[ib * 8: ib * 8 + 8], 2))
            bx.append(x)
        return b''.join(bx)[::-1]

    def encode(self):
        output = self._encode_coils(self.coils[::])
        byte_count = math.ceil(len(self.coils)/8.0)
        head = struct.pack('>BHHB', self.fx, self.address, len(self.coils), byte_count)
        return head + output

    @property
    def response_pdu_pair(self):
        return WriteMultipleCoilsResponse


class WriteMultipleCoilsResponse(PDUResponse):
    """写多个线圈应答"""
    def __init__(self, request_pdu, pdu_fx, pdu_data):
        super().__init__(request_pdu, pdu_fx, pdu_data)

    def as_dict(self):
        address, quantity = struct.unpack('>HH', self.data)
        return {'fx': self.fx, 'data': {'address': address, 'quantity': quantity}}


class WriteMultiRegistersRequest(PDURequest):
    """写多个寄存器"""
    fx = 0x10

    def __init__(self, address, values):
        self.address = address
        self.values = values

    def get_response_pdu_length(self):
        # CORRECT RESPONSE
        # function-code     1 byte
        # starting address  2 byte
        # quantity          2 byte
        correct_response_length = 5

        # INCORRECT RESPONSE
        # function-code     1 byte
        # exception code    1 byte
        incorrect_response_length = 2

        return correct_response_length, incorrect_response_length

    def encode(self):
        values = struct.pack('>{}H'.format(len(self.values)), *self.values)
        byte_count = len(self.values) * 2
        head = struct.pack('>BHHB', self.fx, self.address, len(self.values), byte_count)
        return head + values

    @property
    def response_pdu_pair(self):
        return WriteMultiRegistersResponse


class WriteMultiRegistersResponse(PDUResponse):
    """写多个寄存器应答"""
    def __init__(self, request_pdu, pdu_fx, pdu_data):
        super().__init__(request_pdu, pdu_fx, pdu_data)

    def as_dict(self):
        address, quantity = struct.unpack('>HH', self.data)
        return {'fx': self.fx, 'data': {'address': address, 'quantity': quantity}}


class ReadDeviceIdentificationRequest(PDURequest):
    """读设备标识"""
    fx = 0x2B

    def __init__(self, obj_id):
        self.obj_id = obj_id

    def get_response_pdu_length(self):
        # CORRECT RESPONSE
        # function-code     1 byte
        # starting address  2 byte
        # quantity          2 byte
        correct_response_length = 5

        # INCORRECT RESPONSE
        # function-code     1 byte
        # exception code    1 byte
        incorrect_response_length = 2

        return correct_response_length, incorrect_response_length

    def encode(self):
        if 0 <= self.obj_id <= 2:
            dev_id_code = 0x01
        elif 3 <= self.obj_id <= 0x7F:
            dev_id_code = 0x02
        elif 0x80 <= self.obj_id <= 0xFF:
            dev_id_code = 0x03
        else:
            dev_id_code = 0x04

        return struct.pack('>BBBB', self.fx, 0x0E, dev_id_code, self.obj_id)

    @property
    def response_pdu_pair(self):
        return WriteMultiRegistersResponse


class ReadDeviceIdentificationResponse(PDUResponse):
    """读设备标识应答"""
    def __init__(self, request_pdu, pdu_fx, pdu_data):
        super().__init__(request_pdu, pdu_fx, pdu_data)

    def as_dict(self):
        return {'fx': self.fx, 'data': self.data}


if __name__ == '__main__':
    x = WriteMultipleCoilsRequest._encode_coils([1, 0, 1, 0, 0, 0, 0, 0, 1, 0])
    print(x)

