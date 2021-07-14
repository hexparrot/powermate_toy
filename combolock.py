#!/usr/bin/env python2

# Author: William Dizon <wdchromium@gmail.com>
# Thanks to: William R Sowerbutts <will@sowerbutts.com>
# Griffin powermate spec: https://android.googlesource.com/kernel/msm.git/+/eaf36994a3992b8f918c18e4f7411e8b2320a35f/drivers/input/misc/powermate.c
# Dependencies: powermate interface for python <https://sowerbutts.com/powermate/>

# ISC License
# 
# Copyright (c) [year], [fullname]
# 
# Permission to use, copy, modify, and/or distribute this software for any
# purpose with or without fee is hereby granted, provided that the above
# copyright notice and this permission notice appear in all copies.
# 
# THE SOFTWARE IS PROVIDED "AS IS" AND THE AUTHOR DISCLAIMS ALL WARRANTIES
# WITH REGARD TO THIS SOFTWARE INCLUDING ALL IMPLIED WARRANTIES OF
# MERCHANTABILITY AND FITNESS. IN NO EVENT SHALL THE AUTHOR BE LIABLE FOR
# ANY SPECIAL, DIRECT, INDIRECT, OR CONSEQUENTIAL DAMAGES OR ANY DAMAGES
# WHATSOEVER RESULTING FROM LOSS OF USE, DATA OR PROFITS, WHETHER IN AN
# ACTION OF CONTRACT, NEGLIGENCE OR OTHER TORTIOUS ACTION, ARISING OUT OF
# OR IN CONNECTION WITH THE USE OR PERFORMANCE OF THIS SOFTWARE.

import powermate as pm
from collections import deque

NUMBERS_ON_DIAL = 94
QUEUE_LENGTH = NUMBERS_ON_DIAL * 3 
DEVICE = '/dev/input/event1'

def offset_to_label(offset):
    # Accepts relative position to 0/reset lock
    # Returns number on 'realworld' dial pointer
    # Default value of 94 returns range 0-93
    retval = offset
    while retval < 0:
        retval += NUMBERS_ON_DIAL
    while retval > NUMBERS_ON_DIAL:
        retval -= NUMBERS_ON_DIAL
    return retval

dial = pm.PowerMate(DEVICE)
dial.SetLEDState(256, 254, 2, False, False)

# deque contains list of last x button events
# where x is a function of the numbers on the
# dial. 3*n clock is the trigger for reset.
# T/anticlockwise, F/clockwise
q = deque(False for _ in range(QUEUE_LENGTH))

offset = 0
last = offset

while True:
    evt = dial.WaitForEvent(60)
    if evt is None:
        break # quit after 60 seconds of no input
        # (epoch,      ???   , x,   y,  dir)
        # (1626211922, 773829, 2,   7,    1)
        # (...,        ...   , 2,   7, -1/1) - dial rotation
        # (...,        ...   , 1, 256,  0/1) - button press
        # (x,y) pair determines type of event registered
    elif evt[2:4] == (2,7):
        # dial rotated

        if evt[4] == -1:
            #print 'anticlockwise'

            q.popleft()
            q.append(True)
            offset += -1
        elif evt[4] == 1:
            #print 'clockwise'

            mapped = map(lambda x: x is False, q)
            if all(mapped):
                # restart the loop if ALL events are clockwise.
                # save cycles since subsequent clockwise inputs will have no
                # meaningful state changes. result of reset + extra clockwise
                continue

            q.popleft()
            q.append(False)
            offset += 1
    elif evt[2:4] == (1,256):
        # button press
        if evt[4] == 1:
            print 'button down'
        elif evt[4] == 0:
            print 'button up'

    mapped = map(lambda x: x is False, q)
    if all(mapped):
        if offset != 0:
            print 'reset dial to 0'
        offset, last = 0, 0
        q = deque(False for _ in range(QUEUE_LENGTH))

    if last != offset:
        reported = offset_to_label(offset)
        print reported
        last = offset

        # SetLEDState(brightness, pulse_speed, pulse_table, p_when_sleep, p_when_awake)
        # dial.SetLEDState(0-254, 0-510, 0-2, False, False)
        # lower numbers, lower brightness
        dial.SetLEDState(min(reported * 2, 254), 254, 2, False, False)
