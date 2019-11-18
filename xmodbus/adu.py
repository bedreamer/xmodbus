# -*- coding: utf-8 -*-
# author: lijie
import math
import struct


class BasicADURequest:
    def __init__(self, request_pdu, unit_id):
        self.unit_id = unit_id
        self.pdu = request_pdu

    def encode(self):
        raise NotImplementedError

    def get_response_pdu_length(self):
        return self.pdu.get_response_pdu_length()

    def get_response_pdu_data_length(self):
        return self.pdu.get_response_pdu_data_length()

    def make_response_pdu(self, the_framer):
        raise NotImplementedError


class BasicADUResponse:
    def is_success(self):
        raise NotImplementedError

    def as_dict(self):
        raise NotImplementedError


class AduResponseSuccess(BasicADUResponse):
    def __init__(self, request, response_pdu):
        self.request = request
        self.success = True
        self.pdu = response_pdu

    @property
    def unit_id(self):
        return self.request.unit_id

    def is_success(self):
        return self.success

    def as_dict(self):
        return {'pdu': self.pdu.as_dict(), 'unit_id': self.request.unit_id, 'status': 'success'}


class AduResponseError(BasicADUResponse):
    def __init__(self, request, response_pdu):
        self.request = request
        self.success = False
        self.pdu = response_pdu

    @property
    def unit_id(self):
        return self.request.unit_id

    def is_success(self):
        return self.success

    def as_dict(self):
        return {'pdu': self.pdu.as_dict(), 'unit_id': self.request.unit_id, 'status': 'fail'}
