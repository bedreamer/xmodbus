# -*- coding: utf-8 -*-
# author: lijie
import struct
import xmodbus.framer as framer
import xmodbus.adu as adu
import xmodbus.utilities as utilities


class AduRequest(adu.BasicADURequest):
    def encode(self):
        address = struct.pack('B', self.unit_id)
        bytes_pdu = self.pdu.encode()
        crc = utilities.computeCRC(b''.join([address, bytes_pdu]))
        bytes_crc = struct.pack('>H', crc)
        return b''.join([address, bytes_pdu, bytes_crc])

    def make_response_pdu(self, the_framer):
        fx = the_framer.get_response_function_code()
        data = the_framer.get_response_pdu_data()
        return self.pdu.make_response_pdu_pair(fx, data)


class AduResponseSuccess(adu.AduResponseSuccess):
    pass


class AduResponseError(adu.AduResponseError):
    pass


class RTUFramer(framer.BasicFramer):
    """"""
    def get_response_unit_id(self):
        assert len(self.buffer) > 0, 'len(self.buffer) need > 0'
        return self.buffer[0]

    def get_response_function_code(self):
        assert len(self.buffer) > 1, 'len(self.buffer) need > 1'
        return self.buffer[1]

    def get_response_pdu_data(self):
        assert self._ready, 'need self._ready == True'
        return self.buffer[2:-2]

    def is_response_with_error(self):
        if self.get_response_function_code() & 0x80:
            return True
        return False

    def build_request_adu(self, request_pdu, unit_id):
        return AduRequest(request_pdu, unit_id)

    def is_response_ready(self, request_adu):
        return self._ready

    def response_need_bytes_count(self, request_adu):
        # address | fx-code
        if len(self.buffer) < 2:
            return 2 - len(self.buffer)

        correct_pdu_data_count, incorrect_pdu_data_count = request_adu.get_response_pdu_data_length()
        # total:
        # +---------+--------------------------
        # + unit-id +             1byte
        # +---------+--------------------------
        # +         +      FX     1byte
        # +  PDU    +
        # +         +     DATA    correct_pdu_data_count or incorrect_pdu_data_count
        # +---------+-------------------------
        # +  CRC    +             2byte
        # +---------+--------------------------
        if self.is_response_with_error():
            total_remain_count = incorrect_pdu_data_count + 2
        else:
            total_remain_count = correct_pdu_data_count + 2

        need = total_remain_count - (len(self.buffer) - 2)
        if need == 0:
            self._ready = True
        return need

    def get_response_adu(self, request_adu):
        response_pdu = request_adu.make_response_pdu(self)

        if self.is_response_with_error():
            return AduResponseError(request_adu, response_pdu)

        return AduResponseSuccess(request_adu, response_pdu)
