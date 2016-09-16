import syzoj
from syzoj.models.contest import *
from syzoj.models.user import *
import unittest
import time


class TestContest(unittest.TestCase):
    def setUp(self):
        self.holder = User.query.filter_by(username="abc").first()
        self.start_time = time.time()
        self.contest = Contest("test_con", self.start_time + 2, self.start_time + 5, self.holder)

    def test_set_problems(self):
        prob_list = [1, 2, 3]
        self.contest.set_problems(prob_list)
        self.contest.save()

        probs = self.contest.get_problems()
        print probs
        self.assertTrue(probs)

    def test_is_running(self):
        before = False
        running = False
        after = False
        while True:
            ir = self.contest.is_running()
            if not before:
                if not ir:
                    before = True
            elif not running:
                if ir:
                    running = True
            elif not after:
                if not ir:
                    after = True
            if time.time() > self.start_time + 6:
                break
        self.assertTrue(before)
        self.assertTrue(running)
        self.assertTrue(after)
