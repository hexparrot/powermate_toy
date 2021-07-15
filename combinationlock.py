# Author: William Dizon <wdchromium@gmail.com>

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

    def __init__(self, code=()):
        from collections import deque

        self.position = 0
        self.secured = True
        self.code = code
        self.code_sequence = []

        try:
            for i in range(self.distance(code[0], code[1], LockInputs.Anticlockwise) + self.DIAL_SIZE):
                self.code_sequence.append(LockInputs.Anticlockwise)
            for i in range(self.distance(code[1], code[2], LockInputs.Clockwise)):
                self.code_sequence.append(LockInputs.Clockwise)
        except IndexError:
            pass

        self.movement = deque((None for _ in range(self.DIAL_SIZE * self.COMBO_LENGTH)),
                              self.DIAL_SIZE * self.COMBO_LENGTH)

    def interact(self, inputaction):
        if inputaction is LockInputs.Clockwise:
            self.position += 1
            self.movement.appendleft(inputaction)
        elif inputaction is LockInputs.Anticlockwise:
            self.position -= 1
            self.movement.appendleft(inputaction)

        if self.position < 0:
            self.position = self.DIAL_SIZE - 1
        elif self.position == self.DIAL_SIZE:
            self.position = 0

