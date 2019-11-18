# -*- coding: utf-8 -*-
# author: lijie
import struct
import xmodbus.framer as framer
import xmodbus.adu as adu


class AduRequest(adu.BasicADURequest):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.transaction_identifier = 0

    def set_transaction_identifier(self, tid):
        self.transaction_identifier = tid
        return self

    def encode(self):
        protocol_identifyer = 0
        bytes_pdu = self.pdu.encode()
        length = len(bytes_pdu) + 1
        mbap = struct.pack('>HHHB', self.transaction_identifier, protocol_identifyer, length, self.unit_id)
        return b''.join([mbap, bytes_pdu])

    def make_response_pdu(self, the_framer):
        fx = the_framer.get_response_function_code()
        data = the_framer.get_response_pdu_data()
        return self.pdu.make_response_pdu_pair(fx, data)


class AduResponseSuccess(adu.AduResponseSuccess):
    pass


class AduResponseError(adu.AduResponseError):
    pass


class SocketFramer(framer.BasicFramer):
    """"""
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.transaction_identifier = 0

    def get_response_unit_id(self):
        assert len(self.buffer) >= 7, 'len(self.buffer) need >= 7'
        return self.buffer[6]

    def get_response_function_code(self):
        assert len(self.buffer) >= 8, 'len(self.buffer) need >= 8'
        return self.buffer[7]

    def get_response_pdu_data(self):
        assert self._ready, 'need self._ready == True'
        return self.buffer[8:]

    def is_response_with_error(self):
        if self.get_response_function_code() & 0x80:
            return True
        return False

    def build_request_adu(self, request_pdu, unit_id):
        request_adu = AduRequest(request_pdu, unit_id).set_transaction_identifier(self.transaction_identifier)

        self.transaction_identifier += 1
        if self.transaction_identifier > 0xffff:
            self.transaction_identifier = 0

        return request_adu

    def is_response_ready(self, request_adu):
        return self._ready

    def response_need_bytes_count(self, request_adu):
        # address | fx-code
        if len(self.buffer) < 8:
            return 8 - len(self.buffer)

        correct_pdu_data_count, incorrect_pdu_data_count = request_adu.get_response_pdu_data_length()
        # total:
        # +---------+--------------------------
        # +         +  Transaction Identifier    2 byte
        # +  MBAP   +  Protocol Identifier       2 byte
        # +         +  Length                    2 byte
        # +         +  Unit Identifier           1 byte
        # +---------+--------------------------
        # +         +      FX     1byte
        # +  PDU    +
        # +         +     DATA    correct_pdu_data_count or incorrect_pdu_data_count
        # +---------+-------------------------
        # +  CRC    +             2byte
        # +---------+--------------------------
        if self.is_response_with_error():
            pdu_data_length = incorrect_pdu_data_count
        else:
            pdu_data_length = correct_pdu_data_count

        need = 8 + pdu_data_length - len(self.buffer)
        if need == 0:
            self._ready = True
        return need

    def get_response_adu(self, request_adu):
        response_pdu = request_adu.make_response_pdu(self)

        if self.is_response_with_error():
            return AduResponseError(request_adu, response_pdu)

        return AduResponseSuccess(request_adu, response_pdu)
