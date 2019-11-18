# -*- coding: utf-8 -*-
# author: lijie


class BasicChannel(object):
    """"""
    def sync_open(self, client):
        """打开通道"""
        raise NotImplementedError

    def sync_read(self, n):
        """以同步的方式读入指定长度的数据"""
        raise NotImplementedError

    def sync_write(self, data):
        """以同步方式写出数据"""
        raise NotImplementedError

    async def aio_open(self, client):
        """异步打开通道"""
        raise NotImplementedError

    async def aio_read(self, n):
        """以异步方式读入指定长度的数据"""
        raise NotImplementedError

    async def aio_write(self, n):
        """以异步方式读入指定长度的数据"""
        raise NotImplementedError

    def close(self):
        """关闭通道"""
        raise NotImplementedError
