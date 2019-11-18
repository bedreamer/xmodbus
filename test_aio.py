# -*- coding: utf-8 -*-
# author: lijie
import logging
import asyncio

# client mode
import xmodbus.client.client_aio as client

# channel
import xmodbus.channel.ch_tcp as tcp

# framer
from xmodbus.framer.framer_rtu import RTUFramer
from xmodbus.framer.framer_socket import SocketFramer


logging.basicConfig(level=logging.DEBUG)


tcp_channel = tcp.TCPChannel(host='192.168.1.34', port=502)

Default_Channel = tcp_channel
Default_Framer_Cls = SocketFramer


async def main():
    # 读线圈
    # modbus RTU over TCP/IP with sync mode
    c = client.AioModbusClient(channel=Default_Channel, framer_cls=Default_Framer_Cls, auto_open=False)
    await c.open()

    try:
        while True:
            adu = await c.read_coils(5, 5, 1)
            print(adu.as_dict())

            # 读离散输入
            result = await c.read_discrete_inputs(0, 10, 1)
            print(result.as_dict())

            # 读保持寄存器
            result = await c.read_holding_registers(0, 100, 1)
            print(result.as_dict())

            # 读输入寄存器
            result = await c.read_input_register(0, 60, 1)
            print(result.as_dict())

            # 写单个线圈
            result = await c.write_single_coil(0, 'on', 1)
            print(result.as_dict())

            # 写单个线圈
            result = await c.write_multiple_coils(0, ['on', 'on', 'on'], 1)
            print(result.as_dict())

            # 写单个寄存器
            result = await c.write_single_register(0, 60, 1)
            print(result.as_dict())

            # 写多个寄存器
            import random
            result = await c.write_multiple_registers(0, [random.randrange(0, 255) for _ in range(40)], 1)
            print(result.as_dict())

            # 读设备标识信息
            # result = c.read_device_identification(0x00, 1)
            # print(result.as_dict())
            await asyncio.sleep(1)
    finally:
        c.close()


l = asyncio.get_event_loop()
asyncio.run(main())
