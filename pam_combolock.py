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

# INSTALLATION: This specific module is designed for use in pam.d-
# auth required pam_exec.so stdout /path/to/pam_combolock.py
# Change the combination below or adjust as necessary to accept argv,
# or to generate based on other input/properly-secured files, etc.

COMBINATION = (10,60,30)
TIMEOUT = 30

import sys
import powermate
import combinationlock

dial = powermate.PowerMate()

lock = combinationlock.CombinationLock(COMBINATION)
inputs = combinationlock.LockInputs
last_direction = inputs.Clockwise

while True:
    evt = dial.WaitForEvent(TIMEOUT)
    print(sys.stdin.readlines(), end='\r', flush=True)

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
                print('lock reset to 0')

        print("{0: >4}".format(lock.position))
    elif evt[2:4] == (1,256): #button press
        if evt[4] == 1: #print('button down')
            print('')
            print('unlocked:', not lock.secured)
            if not lock.secured:
                sys.exit(0)
            else:
                sys.exit(10)
        elif evt[4] == 0: #print('button up')
            pass

