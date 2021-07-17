#!/usr/bin/env python3

# Author: William Dizon <wdchromium@gmail.com>

import asyncio
import logging

from joycontrol import logging_default as log, utils
from joycontrol.command_line_interface import ControllerCLI
from joycontrol.controller import Controller
from joycontrol.controller_state import ControllerState, button_push, button_press, button_release
from joycontrol.memory import FlashMemory
from joycontrol.protocol import controller_protocol_factory
from joycontrol.server import create_hid_server

import powermate
dial = powermate.PowerMate()

logger = logging.getLogger(__name__)

async def pairing_to_game_library(controller_state):
    await asyncio.sleep(5)
    await button_push(controller_state, 'a')
    await asyncio.sleep(0.5)
    await button_push(controller_state, 'down')
    await asyncio.sleep(0.5)
    await button_push(controller_state, 'down')
    await asyncio.sleep(0.5)
    await button_push(controller_state, 'down')
    await asyncio.sleep(0.5)
    await button_push(controller_state, 'a')
    await asyncio.sleep(0.5)
    await button_push(controller_state, 'up')

async def _main():
    # Get controller name to emulate from arguments
    controller = Controller.from_arg('PRO_CONTROLLER')

    # prepare the the emulated controller
    factory = controller_protocol_factory(controller,
                                          spi_flash=FlashMemory(),
                                          reconnect = None)
    ctl_psm, itr_psm = 17, 19
    transport, protocol = await create_hid_server(factory,
                                                  reconnect_bt_addr="B8:8A:EC:FD:C7:F5",
                                                  ctl_psm=ctl_psm,
                                                  itr_psm=itr_psm,
                                                  device_id=None,
                                                  interactive=True)

    controller_state = protocol.get_controller_state()
    #await pairing_to_game_library(controller_state)
    c_cli = ControllerCLI(controller_state)

    while True:
        evt = dial.WaitForEvent(1)
        if evt is None:
            pass
        elif evt[2:4] == (2,7): # dial rotated
            if evt[4] == -1: #anticlock
                #await button_push(controller_state, 'left', sec=0.5)
                await c_cli.cmd_stick('l', 'horizontal', 0)
            elif evt[4] == 1: #clockwise
                #await button_push(controller_state, 'right', sec=0.5)
                await c_cli.cmd_stick('l', 'horizontal', 4095)
        elif evt[2:4] == (1,256): #button press
            if evt[4] == 1: #button down
                await button_push(controller_state, 'a')
            elif evt[4] == 0: #button up
                pass

if __name__ == '__main__':
    log.configure()

    loop = asyncio.get_event_loop()
    asyncio.run(_main())
