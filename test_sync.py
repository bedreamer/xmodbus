# -*- coding: utf-8 -*-
# author: lijie
import logging

# client mode
import xmodbus.client.client_sync as client

# channel
import xmodbus.channel.ch_tcp as tcp

# framer
from xmodbus.framer.framer_rtu import RTUFramer
from xmodbus.framer.framer_socket import SocketFramer


logging.basicConfig(level=logging.DEBUG)

tcp_channel = tcp.TCPChannel(host='192.168.1.34', port=502)
proxy_tcp_channel = tcp.TCPChannel(host='192.168.1.34', port=502, proxy_addr='127.0.0.1', proxy_port=1080)

Default_Channel = tcp_channel
Default_Framer_Cls = SocketFramer


def main():
    # modbus RTU over TCP/IP with sync mode
    c = client.SyncModbusClient(channel=Default_Channel, framer_cls=Default_Framer_Cls)

    try:
        while True:
            # 读线圈
            adu = c.read_coils(5, 5, 1)
            print(adu.as_dict())

            # 读离散输入
            result = c.read_discrete_inputs(0, 10, 1)
            print(result.as_dict())

            # 读保持寄存器
            result = c.read_holding_registers(0, 100, 1)
            print(result.as_dict())

            # 读输入寄存器
            result = c.read_input_register(0, 60, 1)
            print(result.as_dict())

            # 写单个线圈
            result = c.write_single_coil(0, 'on', 1)
            print(result.as_dict())

            # 写单个线圈
            result = c.write_multiple_coils(0, ['on', 'on', 'on'], 1)
            print(result.as_dict())

            # 写单个寄存器
            result = c.write_single_register(0, 60, 1)
            print(result.as_dict())

            # 写多个寄存器
            import random
            result = c.write_multiple_registers(0, [random.randrange(0, 255) for _ in range(40)], 1)
            print(result.as_dict())

            # 读设备标识信息
            # result = c.read_device_identification(0x00, 1)
            # print(result.as_dict())
    finally:
        c.close()


main()
