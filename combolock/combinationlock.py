# Author: William Dizon <wdchromium@gmail.com>

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

from enum import Enum

class LockInputs(Enum):
    Anticlockwise = 0
    Clockwise = 1
    OpenShackle = 2
    CloseShackle = 3

class CombinationLock(object):
    
    DIAL_SIZE = 94
    COMBO_LENGTH = 3

    @classmethod
    def distance(cls, start_pos, end_pos, direction):
        if direction is LockInputs.Clockwise:
            if start_pos < end_pos: #short distance
                return end_pos - start_pos
            else: #long distance
                return cls.DIAL_SIZE - (start_pos - end_pos)
        elif direction is LockInputs.Anticlockwise:
            if start_pos < end_pos: # long distance
                return start_pos + (cls.DIAL_SIZE - end_pos)
            else:
                return start_pos - end_pos

    def __init__(self, code=(0,0,0)):
        self.position = 0
        self.secured = True
        self.code = code
        self.movement = []

    def interact(self, inputaction):
        if inputaction is LockInputs.Clockwise:
            self.position += 1
            self.movement.append(inputaction)
        elif inputaction is LockInputs.Anticlockwise:
            self.position -= 1
            self.movement.append(inputaction)

        if self.position < 0:
            self.position = self.DIAL_SIZE - 1
        elif self.position == self.DIAL_SIZE:
            self.position = 0

        from itertools import zip_longest, chain, repeat
        iter_movement = iter(self.movement)
        iter_code = chain(repeat(LockInputs.Clockwise, self.code[0]),
                          repeat(LockInputs.Anticlockwise, self.distance(self.code[0], self.code[1], LockInputs.Anticlockwise) + self.DIAL_SIZE),
                          repeat(LockInputs.Clockwise, self.distance(self.code[1], self.code[2], LockInputs.Clockwise)))

        zipped = zip_longest(iter_code, iter_movement)

        if self.code == (0,0,0):
            self.secured = True
        else:
            max_len = self.DIAL_SIZE * 3
            while len(self.movement) > max_len:
                self.movement.pop(0)
            if len(self.movement) == max_len:
                if all(a is LockInputs.Clockwise for a in self.movement[-max_len:]): # get last 94*3 elements
                    self.reset()

            self.secured = not all(a == b for a,b in zipped)

    def reset(self):
        self.movement = []
        self.position = 0
