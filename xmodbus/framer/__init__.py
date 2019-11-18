# -*- coding: utf-8 -*-
# author: lijie


class BasicFramer:
    def __init__(self, client, channel):
        self.client = client
        self.channel = channel

        self.buffer = b''
        self._ready = False

    def get_response_unit_id(self):
        raise NotImplementedError

    def get_response_function_code(self):
        raise NotImplementedError

    def get_response_error_code(self):
        raise NotImplementedError

    def get_response_pdu_data(self):
        raise NotImplementedError

    def is_response_with_error(self):
        raise NotImplementedError

    def push(self, data):
        self.buffer += data

    def build_request_adu(self, request_pdu, unit_id):
        """return <ADU object>"""
        raise NotImplementedError

    def reset(self):
        self.buffer = b''
        self._ready = False

    def response_need_bytes_count(self, request_adu):
        """返回当前需要接收的数据长度"""
        raise NotImplementedError

    def is_response_ready(self, request_adu):
        """判定数据帧是否接收完成"""
        raise NotImplementedError

    def get_response_adu(self, request_adu):
        """返回ADU"""
        raise NotImplementedError
