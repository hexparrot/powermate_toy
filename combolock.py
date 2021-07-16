#!/usr/bin/env python3

# Author: William Dizon <wdchromium@gmail.com>
# Thanks to: William R Sowerbutts <will@sowerbutts.com>
# Griffin powermate spec: https://android.googlesource.com/kernel/msm.git/+/eaf36994a3992b8f918c18e4f7411e8b2320a35f/drivers/input/misc/powermate.c
# Powermate interface for python included with express permission from William R Sowerbutts <https://sowerbutts.com/powermate/>

# ISC License
# 
# Copyright (c) 2021, William Dizon
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

import sys
import powermate
import combinationlock

dial = powermate.PowerMate()

lock = combinationlock.CombinationLock( (10,60,30) )
inputs = combinationlock.LockInputs
last_direction = inputs.Clockwise

while True:
    evt = dial.WaitForEvent(60)

    if evt is None:
        sys.exit(255)
    elif evt[2:4] == (2,7):
        # dial rotated
        if evt[4] == -1: #anticlock
            lock.interact(inputs.Anticlockwise)
            if last_direction != inputs.Anticlockwise:
                print('')
            last_direction = inputs.Anticlockwise
        elif evt[4] == 1:
            lock.interact(inputs.Clockwise)
            if last_direction != inputs.Clockwise:
                print('')
            last_direction = inputs.Clockwise
            if len(lock.movement) == 0:
                print('lock reset to 0', end='\r', flush=True)

        print("{0: >4}".format(lock.position), end='\r', flush=True)
    elif evt[2:4] == (1,256): #button press
        if evt[4] == 1:
            #print('button down')
            print('')
            print('secured:', lock.secured)
            if not lock.secured:
                sys.exit(0)
            else:
                lock.reset()
        elif evt[4] == 0:
            pass #print('button up')

