import unittest
import syzoj
import hashlib
from random import randint


class TestRegister(unittest.TestCase):
    def md5_pass(self, password):
        md5 = hashlib.md5()
        md5.update(password)
        return md5.hexdigest()

    def test_register(self):
        user = "tester_%d" % randint(1, int(1e9))
        pw = self.md5_pass("123_%d" % randint(1, 100))
        email = "84%d@qq.com" % randint(1, 10000)
        print user, pw, email
        self.assertEqual(syzoj.controller.register(user, pw, email), 1)

        self.assertNotEqual(syzoj.controller.register(user, pw, email), 1)

    def test_multiple_register(self):
        rid = randint(1, 10000)
        for i in range(1, 2):
            pw = self.md5_pass("123_%d_%d" % (rid, i))
            print i, pw
            self.assertEqual(syzoj.controller.register("hello_%d_%d" % (rid, i), pw, "%d@qq.com" % i), 1)


if __name__ == "__main__":
    unittest.main()
