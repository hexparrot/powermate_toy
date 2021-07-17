#!/usr/bin/env python3

# Author: William Dizon <wdchromium@gmail.com>

from enum import Enum

class Pedal(Enum):
    Neutral = 0
    Gas = 1
    Reverse = 2

import asyncio
import logging
import sys
sys.path.insert(0, "./joycontrol")

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
MAX_OFFSET = 20

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

async def change_gear(controller_state, pedal_position, offset):
    if pedal_position is Pedal.Neutral:
        if offset == -MAX_OFFSET:
            return Pedal.Gas
        elif offset == MAX_OFFSET:
            return Pedal.Reverse
        else:
            return Pedal.Neutral
    elif pedal_position is Pedal.Gas:
        if offset == -MAX_OFFSET:
            return Pedal.Gas
        elif offset == MAX_OFFSET:
            pass
        return Pedal.Neutral
    elif pedal_position is Pedal.Reverse:
        if offset == -MAX_OFFSET:
            return Pedal.Neutral
        else:
            return Pedal.Reverse
        return Pedal.Neutral

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

    offset = 0.0
    pedal_action = Pedal.Neutral
    while True:
        evt = dial.WaitForEvent(10)
        if evt is None:
            pass
        elif evt[2:4] == (2,7): # dial rotated
            if evt[4] == -1: #anticlock
                offset -= 1.0
            elif evt[4] == 1: #clockwise
                offset += 1.0

            offset = -MAX_OFFSET if offset < -MAX_OFFSET else offset
            offset = MAX_OFFSET if offset > MAX_OFFSET else offset
            await asyncio.create_task(c_cli.cmd_stick('l', 'horizontal', 2048 + (100*offset)))
            print(offset, 2048 + (100*offset), pedal_action)
            if pedal_action is Pedal.Reverse:
                await asyncio.create_task(button_press(controller_state, 'b'))
        elif evt[2:4] == (1,256): #button press
            if evt[4] == 1: #button down
                print('down', pedal_action)
                if pedal_action is not Pedal.Reverse:
                    await asyncio.create_task(button_push(controller_state, 'a'))
                pedal_action = await change_gear(controller_state,
                                                 pedal_action,
                                                 offset)
                print('returned',  pedal_action)
            elif evt[4] == 0: #button up
                print('up', pedal_action)
                if pedal_action is Pedal.Gas:
                    print('gassin')
                    await asyncio.create_task(button_press(controller_state, 'a'))
                elif pedal_action is Pedal.Neutral:
                    print('stoppin')
                    await asyncio.gather(
                        button_release(controller_state, 'a'),
                        button_release(controller_state, 'b')
                    )
                elif pedal_action is Pedal.Reverse:
                    await asyncio.create_task(button_release(controller_state, 'b'))
                    pedal_action = Pedal.Neutral

if __name__ == '__main__':
    log.configure()

    loop = asyncio.get_event_loop()
    asyncio.run(_main())
