# -*- coding: utf-8 -*-
# author: lijie
import xmodbus.channel as channel
import socks
import socket
import time
import logging
import asyncio


_logger = logging.getLogger()


class TCPChannel(channel.BasicChannel):
    """"""
    def __init__(self, host=None, port=None, proxy_addr=None, proxy_port=None, proxy_username=None, proxy_password=None):
        self.host = host or '127.0.0.1'
        self.port = port or 502

        self.proxy_addr = proxy_addr
        self.proxy_port = proxy_port
        self.proxy_username = proxy_username
        self.proxy_password = proxy_password

        self.client = None

        self.conn = None

        self.reader = None
        self.writer = None

    def sync_open(self, client):
        """打开通道"""
        self.client = client
        if self.proxy_addr:
            _logger.info('use proxy on {}:{}'.format(self.proxy_addr, self.proxy_port))
            self.conn = socks.create_connection((self.host, self.port), timeout=1,
                                                proxy_addr=self.proxy_addr,
                                                proxy_port=self.proxy_port,
                                                proxy_username=self.proxy_username,
                                                proxy_password=self.proxy_password)
        else:
            self.conn = socket.create_connection((self.host, self.port))

    def sync_read(self, n):
        """以同步的方式读入指定长度的数据"""
        data = self.conn.recv(n)
        _logger.debug('RX {}'.format(data.hex()))
        return data

    def sync_write(self, data):
        """以同步方式写出数据"""
        _logger.debug('TX {}'.format(data.hex()))
        self.conn.send(data)
        time.sleep(0.5)

    async def aio_open(self, client):
        """异步方式打开"""
        self.client = client
        self.reader, self.writer = await asyncio.open_connection(self.host, self.port)
        _logger.debug('opened')

    async def aio_read(self, n):
        """以异步方式读入指定长度的数据"""
        return await self.reader.read(n)

    async def aio_write(self, data):
        """以异步方式读入指定长度的数据"""
        self.writer.write(data)
        await self.writer.drain()

    def close(self):
        if self.conn:
            self.conn.close()

        if self.writer:
            self.writer.close()

