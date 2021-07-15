#!/usr/bin/env python3

import unittest
import combinationlock

class TestComboLock(unittest.TestCase):
    def setUp(self):
        pass

    def tearDown(self):
        pass

    def test_consts(self):
        inst = combinationlock.CombinationLock()
        self.assertEqual(inst.DIAL_SIZE, 94)
        self.assertEqual(inst.COMBO_LENGTH, 3)

    def test_default_pos(self):
        inst = combinationlock.CombinationLock()
        self.assertEqual(inst.position, 0)

    def test_rotate(self):
        inst = combinationlock.CombinationLock()
        li = combinationlock.LockInputs

        inst.interact(li.Clockwise)
        self.assertEqual(inst.position, 1)
        inst.interact(li.Anticlockwise)
        self.assertEqual(inst.position, 0)
        inst.interact(li.Anticlockwise)
        self.assertEqual(inst.position, inst.DIAL_SIZE - 1)
        inst.interact(li.Clockwise)
        self.assertEqual(inst.position, 0)
        inst.interact(li.Clockwise)
        self.assertEqual(inst.position, 1)

    def test_secured(self):
        inst = combinationlock.CombinationLock()
        li = combinationlock.LockInputs

        inst.interact(li.CloseShackle)
        self.assertTrue(inst.secured)
        inst.interact(li.OpenShackle)
        self.assertTrue(inst.secured)

    def test_set_code(self):
        inst = combinationlock.CombinationLock()
        self.assertTrue(inst.secured)
        self.assertEqual(inst.code, ())

        inst = combinationlock.CombinationLock( (36,24,36) )
        self.assertTrue(inst.secured)
        self.assertEqual(inst.code, (36,24,36))

        inst = combinationlock.CombinationLock( (30,80,12) )
        self.assertTrue(inst.secured)
        self.assertEqual(inst.code, (30,80,12))

    def test_code_sequence(self):
        inst = combinationlock.CombinationLock( (36,24,36) )
        seq = iter(inst.code_sequence)
        self.assertEqual(len(inst.code_sequence), 118)

        inst = combinationlock.CombinationLock( (30,80,12) )
        seq = iter(inst.code_sequence)
        self.assertEqual(len(inst.code_sequence), 164)

    def test_distance(self):
        clsm = combinationlock.CombinationLock
        li = combinationlock.LockInputs

        self.assertEqual(clsm.distance(0, 10, li.Clockwise), 10)
        self.assertEqual(clsm.distance(0, 10, li.Anticlockwise), 84)

        self.assertEqual(clsm.distance(0, 90, li.Clockwise), 90)
        self.assertEqual(clsm.distance(0, 90, li.Anticlockwise), 4)

        self.assertEqual(clsm.distance(30, 50, li.Clockwise), 20)
        self.assertEqual(clsm.distance(30, 50, li.Anticlockwise), 74)

        self.assertEqual(clsm.distance(30, 20, li.Clockwise), 84)
        self.assertEqual(clsm.distance(30, 20, li.Anticlockwise), 10)

if __name__ == "__main__":
    unittest.main()
