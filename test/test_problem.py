import syzoj
from syzoj.models import Problem
import unittest


class TestCreateProblem(unittest.TestCase):
    def setUp(self):
        user = syzoj.models.User.query.filter_by(id=1).first()
        title = u"\u6D4B\u8BD5\u9898\u76EE".encode("utf-8")
        pid = syzoj.controller.create_problem(user, title)
        print pid
        self.problem = Problem.query.filter_by(id=pid).first()
        self.assertTrue(pid >= 1)

    def test_edit_problem(self):
        des = "Give you two integer A and B.Now please calculate A+B."
        hint = "uh...."
        self.problem.update(description=des)
        self.problem.save()
        self.assertEqual(self.problem.description, des)

        self.problem.update(limit_and_hint=hint)
        self.problem.save()
        self.assertEqual(self.problem.description, des)

        self.problem.is_public = True
        self.problem.save()
