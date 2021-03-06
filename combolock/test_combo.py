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
        self.assertEqual(inst.code, (0,0,0))

        inst = combinationlock.CombinationLock( (36,24,36) )
        self.assertTrue(inst.secured)
        self.assertEqual(inst.code, (36,24,36))

        inst = combinationlock.CombinationLock( (30,80,12) )
        self.assertTrue(inst.secured)
        self.assertEqual(inst.code, (30,80,12))

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

    def test_open_lock(self):
        inst = combinationlock.CombinationLock( (36,24,36) )
        li = combinationlock.LockInputs

        self.assertTrue(inst.secured)

        for _ in range(36):
            inst.interact(li.Clockwise)
            self.assertTrue(inst.secured)

        for _ in range(inst.DIAL_SIZE + inst.distance(36, 24, li.Anticlockwise)):
            inst.interact(li.Anticlockwise)
            self.assertTrue(inst.secured)

        for _ in range(inst.distance(24, 36, li.Clockwise) - 1):
            inst.interact(li.Clockwise)
            self.assertTrue(inst.secured)

        inst.interact(li.Clockwise)
        self.assertFalse(inst.secured)

    def test_unopened_lock_relocks(self):
        inst = combinationlock.CombinationLock( (36,24,36) )
        li = combinationlock.LockInputs

        self.assertTrue(inst.secured)

        for _ in range(36):
            inst.interact(li.Clockwise)
            self.assertTrue(inst.secured)

        for _ in range(inst.DIAL_SIZE + inst.distance(36, 24, li.Anticlockwise)):
            inst.interact(li.Anticlockwise)
            self.assertTrue(inst.secured)

        for _ in range(inst.distance(24, 36, li.Clockwise) - 1):
            inst.interact(li.Clockwise)
            self.assertTrue(inst.secured)

        inst.interact(li.Clockwise)
        self.assertFalse(inst.secured)
        inst.interact(li.Clockwise)
        self.assertTrue(inst.secured)

    def test_unset_lock(self):
        inst = combinationlock.CombinationLock()
        li = combinationlock.LockInputs

        self.assertTrue(inst.secured)
        # this works because of the implied +DIAL_SIZE for the anticlock rotation
        for _ in range(inst.DIAL_SIZE):
            inst.interact(li.Anticlockwise)
            self.assertTrue(inst.secured)
        self.assertTrue(inst.secured)

    def test_reset_lock(self):
        inst = combinationlock.CombinationLock( (36,24,36) )
        li = combinationlock.LockInputs

        self.assertTrue(inst.secured)
        inst.interact(li.Clockwise)
        self.assertTrue(inst.secured)

        # correct sequence, but polluted with preceding clock turn
        for _ in range(36):
            inst.interact(li.Clockwise)
            self.assertTrue(inst.secured)

        for _ in range(inst.DIAL_SIZE + inst.distance(36, 24, li.Anticlockwise)):
            inst.interact(li.Anticlockwise)
            self.assertTrue(inst.secured)

        for _ in range(inst.distance(24, 36, li.Clockwise)):
            inst.interact(li.Clockwise)
            self.assertTrue(inst.secured)

        self.assertTrue(inst.secured)
        inst.reset()
        self.assertEqual(inst.position, 0)

        # correct sequence
        for _ in range(36):
            inst.interact(li.Clockwise)
            self.assertTrue(inst.secured)

        for _ in range(inst.DIAL_SIZE + inst.distance(36, 24, li.Anticlockwise)):
            inst.interact(li.Anticlockwise)
            self.assertTrue(inst.secured)

        for _ in range(inst.distance(24, 36, li.Clockwise) - 1):
            inst.interact(li.Clockwise)
            self.assertTrue(inst.secured)

        inst.interact(li.Clockwise)
        self.assertFalse(inst.secured)

    def test_reset_on_three_clockturns(self):
        inst = combinationlock.CombinationLock( (36,24,36) )
        li = combinationlock.LockInputs

        for _ in range(36):
            inst.interact(li.Clockwise)

        for _ in range(40):
            inst.interact(li.Anticlockwise)

        self.assertEqual(len(inst.movement), 76)

        for _ in range((inst.DIAL_SIZE * 3) - 1):
            inst.interact(li.Clockwise)
            self.assertNotEqual(len(inst.movement), 0)

        inst.interact(li.Clockwise)
        self.assertEqual(len(inst.movement), 0)
        self.assertEqual(inst.position, 0)

    def test_limit_history_to_three_turns(self):
        inst = combinationlock.CombinationLock( (36,24,36) )
        li = combinationlock.LockInputs

        max_len = inst.DIAL_SIZE * 3

        for _ in range(max_len - 1):
            inst.interact(li.Anticlockwise)
            self.assertTrue(len(inst.movement) < inst.DIAL_SIZE * 3)

        inst.interact(li.Anticlockwise)
        self.assertEqual(len(inst.movement), inst.DIAL_SIZE * 3)
        inst.interact(li.Anticlockwise)
        self.assertEqual(len(inst.movement), inst.DIAL_SIZE * 3)

if __name__ == "__main__":
    unittest.main()

